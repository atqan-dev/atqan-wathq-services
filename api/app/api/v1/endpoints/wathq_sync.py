"""
WATHQ data sync endpoints - sync data from wathq_call_logs to structured tables.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app import models, schemas
from app.api import deps
from app.crud import crud_wathq_commercial_registration

router = APIRouter()


@router.post("/commercial-registration/sync", response_model=Dict[str, Any])
def sync_commercial_registration_from_logs(
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Sync commercial registration data from wathq_call_logs to CR tables.

    Filters:
    - status_code = 200
    - service_slug = 'commercial-registration'
    - endpoint starts with 'fullinfo/'

    Parses response_body and creates/updates records in:
    - commercial_registrations
    - capital_info
    - cr_activities
    - cr_parties
    - cr_managers
    - cr_entity_characters
    - cr_stocks
    - cr_estores
    - cr_liquidators
    """

    try:
        # First, let's check what we have in the database
        all_cr_logs = (
            db.query(models.WathqCallLog)
            .filter(models.WathqCallLog.service_slug == "commercial-registration")
            .all()
        )

        print(f"Found {len(all_cr_logs)} commercial-registration logs in database")
        for log in all_cr_logs[:5]:  # Print first 5 for debugging
            print(f"  - endpoint: {log.endpoint}, status: {log.status_code}")

        # Query wathq_call_logs with filters - match /fullinfo/* pattern
        call_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "commercial-registration",
                    models.WathqCallLog.endpoint.like("/fullinfo/%"),
                )
            )
            .all()
        )

        print(f"Found {len(call_logs)} logs matching /fullinfo/% pattern")
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    if not call_logs:
        # Try without the fullinfo filter to see what endpoints we have
        any_success_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "commercial-registration",
                )
            )
            .limit(10)
            .all()
        )

        endpoints_found = [log.endpoint for log in any_success_logs]

        return {
            "success": True,
            "message": f"No call logs found matching criteria. Found {len(all_cr_logs)} CR logs total, but none with endpoint like 'fullinfo/%'. Endpoints found: {endpoints_found}",
            "synced_count": 0,
            "total_logs": 0,
            "errors": [],
        }

    synced_count = 0
    errors = []

    for log in call_logs:
        # Use a savepoint for each record so errors don't abort the whole transaction
        savepoint = db.begin_nested()

        try:
            print(f"Processing log {log.id}...")
            response_body = log.response_body

            # Check if response has the expected structure
            if not response_body or not isinstance(response_body, dict):
                error_msg = "Invalid response_body structure"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Extract CR data from response_body
            # The structure might be: {"data": {...}} or direct data
            cr_data = response_body.get("data", response_body)

            if not cr_data or not isinstance(cr_data, dict):
                error_msg = "No data found in response_body"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Extract cr_number
            cr_number = cr_data.get("crNumber") or cr_data.get("cr_number")
            if not cr_number:
                error_msg = "No cr_number found in data"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            print(f"  Processing CR: {cr_number}")

            # Always create new records to maintain historical data
            # Check if we already synced this specific log by log_id
            existing_cr = (
                db.query(models.CommercialRegistration)
                .filter(models.CommercialRegistration.log_id == log.id)
                .first()
            )

            if existing_cr:
                print(f"  Skipping CR {cr_number} - already synced from log {log.id}")
                savepoint.commit()
                continue

            print(
                f"  Creating new historical record for CR: {cr_number} from log {log.id}"
            )
            # Always create new record to maintain history
            _create_commercial_registration(db, cr_data, log)

            # Commit the savepoint
            savepoint.commit()
            synced_count += 1
            print(f"  Successfully synced CR: {cr_number}")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  Error processing log {log.id}: {error_msg}")
            import traceback

            traceback.print_exc()
            errors.append({"log_id": str(log.id), "error": error_msg})
            # Rollback this record's changes
            savepoint.rollback()
            continue

    try:
        db.commit()
        print(f"Successfully committed {synced_count} records")
    except Exception as e:
        print(f"Error committing to database: {str(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")

    return {
        "success": True,
        "message": f"Synced {synced_count} records from {len(call_logs)} call logs",
        "synced_count": synced_count,
        "total_logs": len(call_logs),
        "errors": errors,
    }


def _create_commercial_registration(
    db: Session, cr_data: Dict, log: models.WathqCallLog
) -> models.CommercialRegistration:
    """Create a new commercial registration record with all related data."""

    # Extract nested objects
    entity_type = cr_data.get("entityType", {}) or {}
    status = cr_data.get("status", {}) or {}
    contact_info = cr_data.get("contactInfo", {}) or {}
    fiscal_year = cr_data.get("fiscalYear", {}) or {}
    management = cr_data.get("management", {}) or {}

    # Create main CR record
    cr = models.CommercialRegistration(
        log_id=log.id,  # Link to the source call log
        cr_number=cr_data.get("crNumber") or cr_data.get("cr_number"),
        cr_national_number=cr_data.get("crNationalNumber"),
        version_no=cr_data.get("versionNo"),
        fetched_at=log.fetched_at,  # Track when this data was fetched
        name=cr_data.get("name"),
        name_lang_id=cr_data.get("nameLangId"),
        name_lang_desc=cr_data.get("nameLangDesc"),
        cr_capital=cr_data.get("crCapital"),
        company_duration=cr_data.get("companyDuration"),
        is_main=cr_data.get("isMain"),
        issue_date_gregorian=cr_data.get("issueDateGregorian"),
        issue_date_hijri=cr_data.get("issueDateHijri"),
        main_cr_national_number=cr_data.get("mainCrNationalNumber"),
        main_cr_number=cr_data.get("mainCrNumber"),
        in_liquidation_process=cr_data.get("inLiquidationProcess"),
        has_ecommerce=cr_data.get("hasEcommerce"),
        headquarter_city_id=cr_data.get("headquarterCityId"),
        headquarter_city_name=cr_data.get("headquarterCityName"),
        is_license_based=cr_data.get("isLicenseBased"),
        license_issuer_national_number=cr_data.get("licenseIssuerNationalNumber"),
        license_issuer_name=cr_data.get("licenseIssuerName"),
        partners_nationality_id=cr_data.get("partnersNationalityId"),
        partners_nationality_name=cr_data.get("partnersNationalityName"),
        # Extract from entityType object
        entity_type_id=entity_type.get("id"),
        entity_type_name=entity_type.get("name"),
        entity_form_id=entity_type.get("formId"),
        entity_form_name=entity_type.get("formName"),
        # Extract from status object
        status_id=status.get("id"),
        status_name=status.get("name"),
        confirmation_date_gregorian=(
            status.get("confirmationDate", {}).get("gregorian")
            if status.get("confirmationDate")
            else None
        ),
        confirmation_date_hijri=(
            status.get("confirmationDate", {}).get("hijri")
            if status.get("confirmationDate")
            else None
        ),
        reactivation_date_gregorian=(
            status.get("reactivationDate", {}).get("gregorian")
            if status.get("reactivationDate")
            else None
        ),
        reactivation_date_hijri=(
            status.get("reactivationDate", {}).get("hijri")
            if status.get("reactivationDate")
            else None
        ),
        suspension_date_gregorian=(
            status.get("suspensionDate", {}).get("gregorian")
            if status.get("suspensionDate")
            else None
        ),
        suspension_date_hijri=(
            status.get("suspensionDate", {}).get("hijri")
            if status.get("suspensionDate")
            else None
        ),
        deletion_date_gregorian=(
            status.get("deletionDate", {}).get("gregorian")
            if status.get("deletionDate")
            else None
        ),
        deletion_date_hijri=(
            status.get("deletionDate", {}).get("hijri")
            if status.get("deletionDate")
            else None
        ),
        # Extract from contactInfo object
        contact_phone=contact_info.get("phoneNo"),
        contact_mobile=contact_info.get("mobileNo"),
        contact_email=contact_info.get("email"),
        contact_website=contact_info.get("websiteUrl"),
        # Extract from fiscalYear object
        fiscal_is_first=fiscal_year.get("isFirst"),
        fiscal_calendar_type_id=fiscal_year.get("calendarTypeId"),
        fiscal_calendar_type_name=fiscal_year.get("calendarTypeName"),
        fiscal_end_month=fiscal_year.get("endMonth"),
        fiscal_end_day=fiscal_year.get("endDay"),
        fiscal_end_year=fiscal_year.get("endYear"),
        # Extract from management object
        mgmt_structure_id=management.get("structureId"),
        mgmt_structure_name=management.get("structureName"),
        request_body=log.request_data,
    )

    db.add(cr)
    db.flush()  # Get the ID

    # Create related records
    _create_capital_info(db, cr.id, cr_data.get("capitalInfo"))
    _create_activities(db, cr.id, cr_data.get("activities", []))
    _create_parties(db, cr.id, cr_data.get("parties", []))
    _create_managers(db, cr.id, cr_data.get("managers", []))
    _create_entity_characters(db, cr.id, cr_data.get("entityCharacters", []))
    _create_stocks(db, cr.id, cr_data.get("stocks", []))
    _create_estores(db, cr.id, cr_data.get("estores", []))
    _create_liquidators(db, cr.id, cr_data.get("liquidators", []))

    return cr


def _create_capital_info(db: Session, cr_id: int, capital_data: Dict):
    """Create capital info record."""
    if not capital_data:
        return

    capital = models.CapitalInfo(
        cr_id=cr_id,
        capital_amount=capital_data.get("capitalAmount"),
        capital_currency_id=capital_data.get("capitalCurrencyId"),
        capital_currency_name=capital_data.get("capitalCurrencyName"),
        paid_amount=capital_data.get("paidAmount"),
        remaining_amount=capital_data.get("remainingAmount"),
    )
    db.add(capital)


def _create_activities(db: Session, cr_id: int, activities: List[Dict]):
    """Create activity records."""
    for activity_data in activities:
        activity = models.CRActivity(
            cr_id=cr_id,
            activity_id=activity_data.get("activityId"),
            activity_name=activity_data.get("activityName"),
            is_main=activity_data.get("isMain"),
        )
        db.add(activity)


def _create_parties(db: Session, cr_id: int, parties: List[Dict]):
    """Create party records."""
    for party_data in parties:
        party = models.CRParty(
            cr_id=cr_id,
            cr_number=party_data.get("crNumber"),
            name=party_data.get("name"),
            type_id=party_data.get("typeId"),
            type_name=party_data.get("typeName"),
            identity_id=party_data.get("identityId"),
            identity_type_id=party_data.get("identityTypeId"),
            identity_type_name=party_data.get("identityTypeName"),
            share_cash_count=party_data.get("shareCashCount"),
            share_in_kind_count=party_data.get("shareInKindCount"),
            share_total_count=party_data.get("shareTotalCount"),
        )
        db.add(party)


def _create_managers(db: Session, cr_id: int, managers: List[Dict]):
    """Create manager records."""
    for manager_data in managers:
        manager = models.CRManager(
            cr_id=cr_id,
            cr_number=manager_data.get("crNumber"),
            name=manager_data.get("name"),
            type_id=manager_data.get("typeId"),
            type_name=manager_data.get("typeName"),
            is_licensed=manager_data.get("isLicensed"),
            identity_id=manager_data.get("identityId"),
            identity_type_id=manager_data.get("identityTypeId"),
            identity_type_name=manager_data.get("identityTypeName"),
            nationality_id=manager_data.get("nationalityId"),
            nationality_name=manager_data.get("nationalityName"),
        )
        db.add(manager)


def _create_entity_characters(db: Session, cr_id: int, characters: List[Dict]):
    """Create entity character records."""
    for char_data in characters:
        character = models.CREntityCharacter(
            cr_id=cr_id,
            cr_number=char_data.get("crNumber"),
            character_id=char_data.get("id"),
            character_name=char_data.get("name"),
        )
        db.add(character)


def _create_stocks(db: Session, cr_id: int, stocks: List[Dict]):
    """Create stock records."""
    for stock_data in stocks:
        stock = models.CRStock(
            cr_id=cr_id,
            cr_number=stock_data.get("crNumber"),
            type_id=stock_data.get("typeId"),
            type_name=stock_data.get("typeName"),
            count=stock_data.get("count"),
            value=stock_data.get("value"),
        )
        db.add(stock)


def _create_estores(db: Session, cr_id: int, estores: List[Dict]):
    """Create estore records."""
    for estore_data in estores:
        estore = models.CREstore(
            cr_id=cr_id,
            cr_number=estore_data.get("crNumber"),
            name=estore_data.get("name"),
            url=estore_data.get("url"),
            type_id=estore_data.get("typeId"),
            type_name=estore_data.get("typeName"),
        )
        db.add(estore)


def _create_liquidators(db: Session, cr_id: int, liquidators: List[Dict]):
    """Create liquidator records."""
    for liquidator_data in liquidators:
        liquidator = models.CRLiquidator(
            cr_id=cr_id,
            cr_number=liquidator_data.get("crNumber"),
            name=liquidator_data.get("name"),
            type_id=liquidator_data.get("typeId"),
            type_name=liquidator_data.get("typeName"),
            identity_id=liquidator_data.get("identityId"),
            identity_type_id=liquidator_data.get("identityTypeId"),
            identity_type_name=liquidator_data.get("identityTypeName"),
            nationality_id=liquidator_data.get("nationalityId"),
            nationality_name=liquidator_data.get("nationalityName"),
        )
        db.add(liquidator)


@router.post("/corporate-contract/sync", response_model=Dict[str, Any])
def sync_corporate_contract_from_logs(
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Sync corporate contract data from wathq_call_logs to corporate contract tables.

    Filters:
    - status_code = 200
    - service_slug = 'company-contract'
    - endpoint starts with '/info/'

    Parses response_body and creates/updates records in:
    - corporate_contracts
    - contract_stocks
    - contract_parties
    - contract_managers
    - contract_management_config
    - contract_activities
    - contract_articles
    - contract_decisions
    - notification_channels
    """

    try:
        # Query wathq_call_logs with filters - match /info/* pattern
        call_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "company-contract",
                    models.WathqCallLog.endpoint.like("/info/%"),
                )
            )
            .all()
        )

        print(
            f"Found {len(call_logs)} logs matching /info/% pattern for company-contract"
        )
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    if not call_logs:
        # Try without the info filter to see what endpoints we have
        any_success_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "company-contract",
                )
            )
            .limit(10)
            .all()
        )

        endpoints_found = [log.endpoint for log in any_success_logs]

        return {
            "success": True,
            "message": f"No call logs found matching criteria. Endpoints found: {endpoints_found}",
            "synced_count": 0,
            "total_logs": 0,
            "errors": [],
        }

    synced_count = 0
    errors = []

    for log in call_logs:
        savepoint = db.begin_nested()

        try:
            print(f"Processing log {log.id}...")
            response_body = log.response_body

            if not response_body or not isinstance(response_body, dict):
                error_msg = "Invalid response_body structure"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Extract contract data from response_body
            contract_data = response_body.get("data", response_body)

            if not contract_data or not isinstance(contract_data, dict):
                error_msg = "No data found in response_body"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Extract contract identifier - WATHQ API uses contractCopyNumber and entity.crNationalNumber
            # The data may be nested in 'entity' object or at root level
            entity_data = contract_data.get("entity", {}) or {}

            contract_copy_number = contract_data.get(
                "contractCopyNumber"
            ) or contract_data.get("contract_copy_number")
            cr_national_number = (
                entity_data.get("crNationalNumber")
                or contract_data.get("crNationalNumber")
                or contract_data.get("cr_national_number")
            )

            # Use cr_national_number as primary identifier, fall back to contract_copy_number
            contract_identifier = cr_national_number or contract_copy_number
            if not contract_identifier:
                error_msg = (
                    "No cr_national_number or contract_copy_number found in data"
                )
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            print(
                f"  Processing Contract: cr_national_number={cr_national_number}, copy_number={contract_copy_number}"
            )

            # Check if we already synced this specific log using log_id column
            from app.models.wathq_corporate_contract import CorporateContract

            existing_contract = (
                db.query(CorporateContract)
                .filter(CorporateContract.log_id == log.id)
                .first()
            )

            if existing_contract:
                print(
                    f"  Skipping Contract {contract_identifier} - already synced from log {log.id}"
                )
                savepoint.commit()
                continue

            print(
                f"  Creating new record for Contract: {contract_identifier} from log {log.id}"
            )
            _create_corporate_contract(db, contract_data, log)

            savepoint.commit()
            synced_count += 1
            print(f"  Successfully synced Contract: {contract_identifier}")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  Error processing log {log.id}: {error_msg}")
            import traceback

            traceback.print_exc()
            errors.append({"log_id": str(log.id), "error": error_msg})
            savepoint.rollback()
            continue

    try:
        db.commit()
        print(f"Successfully committed {synced_count} records")
    except Exception as e:
        print(f"Error committing to database: {str(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")

    return {
        "success": True,
        "message": f"Synced {synced_count} records from {len(call_logs)} call logs",
        "synced_count": synced_count,
        "total_logs": len(call_logs),
        "errors": errors,
    }


def _create_corporate_contract(
    db: Session, contract_data: Dict, log: models.WathqCallLog
):
    """Create a new corporate contract record with all related data."""
    from app.models.wathq_corporate_contract import (
        CorporateContract,
        ContractStock,
        ContractParty,
        ContractManager,
        ContractManagementConfig,
        ContractActivity,
        ContractArticle,
        ContractDecision,
        NotificationChannel,
    )

    # Extract nested objects - WATHQ API nests entity info in 'entity' object
    entity = contract_data.get("entity", {}) or {}
    entity_type = (
        entity.get("entityType", {}) or contract_data.get("entityType", {}) or {}
    )
    fiscal_year = (
        entity.get("fiscalYear", {}) or contract_data.get("fiscalYear", {}) or {}
    )
    capital_info = (
        entity.get("capitalInfo", {}) or contract_data.get("capitalInfo", {}) or {}
    )
    management = (
        entity.get("management", {}) or contract_data.get("management", {}) or {}
    )

    # Create main contract record
    contract = CorporateContract(
        contract_id=contract_data.get("contractId") or contract_data.get("contract_id"),
        contract_copy_number=contract_data.get("contractCopyNumber")
        or contract_data.get("contract_copy_number"),
        contract_date=contract_data.get("contractDate")
        or contract_data.get("contract_date"),
        cr_national_number=entity.get("crNationalNumber")
        or contract_data.get("crNationalNumber")
        or contract_data.get("cr_national_number"),
        cr_number=entity.get("crNumber")
        or contract_data.get("crNumber")
        or contract_data.get("cr_number"),
        entity_name=entity.get("name")
        or contract_data.get("entityName")
        or contract_data.get("entity_name"),
        entity_name_lang_desc=entity.get("nameLangDesc")
        or contract_data.get("entityNameLangDesc")
        or contract_data.get("entity_name_lang_desc"),
        company_duration=entity.get("companyDuration")
        or contract_data.get("companyDuration")
        or contract_data.get("company_duration"),
        headquarter_city_name=entity.get("headquarterCityName")
        or contract_data.get("headquarterCityName")
        or contract_data.get("headquarter_city_name"),
        is_license_based=entity.get("isLicenseBased")
        or contract_data.get("isLicenseBased")
        or contract_data.get("is_license_based"),
        entity_type_name=entity_type.get("name")
        or contract_data.get("entity_type_name"),
        entity_form_name=entity_type.get("formName")
        or contract_data.get("entity_form_name"),
        fiscal_calendar_type=fiscal_year.get("calendarTypeName")
        or contract_data.get("fiscal_calendar_type"),
        fiscal_year_end_month=fiscal_year.get("endMonth")
        or contract_data.get("fiscal_year_end_month"),
        fiscal_year_end_day=fiscal_year.get("endDay")
        or contract_data.get("fiscal_year_end_day"),
        fiscal_year_end_year=fiscal_year.get("endYear")
        or contract_data.get("fiscal_year_end_year"),
        currency_name=capital_info.get("currencyName")
        or contract_data.get("currency_name"),
        total_capital=capital_info.get("totalCapital")
        or contract_data.get("total_capital"),
        paid_capital=capital_info.get("paidCapital")
        or contract_data.get("paid_capital"),
        cash_capital=capital_info.get("cashCapital")
        or contract_data.get("cash_capital"),
        in_kind_capital=capital_info.get("inKindCapital")
        or contract_data.get("in_kind_capital"),
        is_set_aside_enabled=contract_data.get("isSetAsideEnabled")
        or contract_data.get("is_set_aside_enabled"),
        profit_allocation_percentage=contract_data.get("profitAllocationPercentage")
        or contract_data.get("profit_allocation_percentage"),
        profit_allocation_purpose=contract_data.get("profitAllocationPurpose")
        or contract_data.get("profit_allocation_purpose"),
        additional_decision_text=contract_data.get("additionalDecisionText")
        or contract_data.get("additional_decision_text"),
        log_id=log.id,
        fetched_at=log.fetched_at,
        request_body=log.request_data,
    )

    db.add(contract)
    db.flush()  # Get the ID

    # Create related records
    _create_contract_stocks(db, contract.id, contract_data.get("stocks", []))
    _create_contract_parties(db, contract.id, contract_data.get("parties", []))
    _create_contract_managers(db, contract.id, contract_data.get("managers", []))
    _create_contract_management_config(db, contract.id, management)
    _create_contract_activities(db, contract.id, contract_data.get("activities", []))
    _create_contract_articles(db, contract.id, contract_data.get("articles", []))
    _create_contract_decisions(db, contract.id, contract_data.get("decisions", []))
    _create_notification_channels(
        db, contract.id, contract_data.get("notificationChannels", [])
    )

    return contract


def _create_contract_stocks(db: Session, contract_id: int, stocks: List[Dict]):
    """Create contract stock records."""
    from app.models.wathq_corporate_contract import ContractStock

    for stock_data in stocks:
        stock = ContractStock(
            contract_id=contract_id,
            stock_type_name=stock_data.get("stockTypeName")
            or stock_data.get("stock_type_name"),
            stock_count=stock_data.get("stockCount") or stock_data.get("stock_count"),
            stock_value=stock_data.get("stockValue") or stock_data.get("stock_value"),
        )
        db.add(stock)


def _create_contract_parties(db: Session, contract_id: int, parties: List[Dict]):
    """Create contract party records."""
    from app.models.wathq_corporate_contract import ContractParty

    for party_data in parties:
        party = ContractParty(
            contract_id=contract_id,
            name=party_data.get("name"),
            type_name=party_data.get("typeName") or party_data.get("type_name"),
            identity_number=party_data.get("identityNumber")
            or party_data.get("identity_number"),
            identity_type=party_data.get("identityType")
            or party_data.get("identity_type"),
            nationality=party_data.get("nationality"),
            guardian_name=party_data.get("guardianName")
            or party_data.get("guardian_name"),
        )
        db.add(party)


def _create_contract_managers(db: Session, contract_id: int, managers: List[Dict]):
    """Create contract manager records."""
    from app.models.wathq_corporate_contract import ContractManager

    for manager_data in managers:
        manager = ContractManager(
            contract_id=contract_id,
            name=manager_data.get("name"),
            type_name=manager_data.get("typeName") or manager_data.get("type_name"),
            is_licensed=manager_data.get("isLicensed")
            or manager_data.get("is_licensed"),
            identity_number=manager_data.get("identityNumber")
            or manager_data.get("identity_number"),
            nationality=manager_data.get("nationality"),
            position_name=manager_data.get("positionName")
            or manager_data.get("position_name"),
        )
        db.add(manager)


def _create_contract_management_config(
    db: Session, contract_id: int, management_data: Dict
):
    """Create contract management config record."""
    from app.models.wathq_corporate_contract import ContractManagementConfig

    if not management_data:
        return

    config = ContractManagementConfig(
        contract_id=contract_id,
        structure_name=management_data.get("structureName")
        or management_data.get("structure_name"),
        meeting_quorum_name=management_data.get("meetingQuorumName")
        or management_data.get("meeting_quorum_name"),
        can_delegate_attendance=management_data.get("canDelegateAttendance")
        or management_data.get("can_delegate_attendance"),
        term_years=management_data.get("termYears")
        or management_data.get("term_years"),
    )
    db.add(config)


def _create_contract_activities(db: Session, contract_id: int, activities: List[Dict]):
    """Create contract activity records."""
    from app.models.wathq_corporate_contract import ContractActivity

    for activity_data in activities:
        activity = ContractActivity(
            contract_id=contract_id,
            activity_id=activity_data.get("activityId")
            or activity_data.get("activity_id"),
            activity_name=activity_data.get("activityName")
            or activity_data.get("activity_name"),
        )
        db.add(activity)


def _create_contract_articles(db: Session, contract_id: int, articles: List[Dict]):
    """Create contract article records."""
    from app.models.wathq_corporate_contract import ContractArticle

    for article_data in articles:
        article = ContractArticle(
            contract_id=contract_id,
            original_id=article_data.get("originalId")
            or article_data.get("original_id"),
            article_text=article_data.get("articleText")
            or article_data.get("article_text"),
            part_name=article_data.get("partName") or article_data.get("part_name"),
        )
        db.add(article)


def _create_contract_decisions(db: Session, contract_id: int, decisions: List[Dict]):
    """Create contract decision records."""
    from app.models.wathq_corporate_contract import ContractDecision

    for decision_data in decisions:
        decision = ContractDecision(
            contract_id=contract_id,
            decision_name=decision_data.get("decisionName")
            or decision_data.get("decision_name"),
            approve_percentage=decision_data.get("approvePercentage")
            or decision_data.get("approve_percentage"),
        )
        db.add(decision)


def _create_notification_channels(db: Session, contract_id: int, channels: List[Dict]):
    """Create notification channel records."""
    from app.models.wathq_corporate_contract import NotificationChannel

    for channel_data in channels:
        channel = NotificationChannel(
            contract_id=contract_id,
            channel_name=channel_data.get("channelName")
            or channel_data.get("channel_name"),
        )
        db.add(channel)


@router.post("/power-of-attorney/sync", response_model=Dict[str, Any])
def sync_power_of_attorney_from_logs(
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Sync power of attorney data from wathq_call_logs to POA tables.

    Filters:
    - status_code = 200
    - service_slug = 'attorney-services'
    - endpoint starts with '/info/'

    Parses response_body and creates/updates records in:
    - power_of_attorney
    - poa_allowed_actors
    - poa_principals
    - poa_agents
    - poa_text_list_items
    """

    try:
        # Query wathq_call_logs with filters
        call_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "attorney-services",
                    models.WathqCallLog.endpoint.like("/info/%"),
                )
            )
            .all()
        )

        print(
            f"Found {len(call_logs)} logs matching /info/% pattern for attorney-services"
        )
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    if not call_logs:
        # Try without the info filter to see what endpoints we have
        any_success_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "attorney-services",
                )
            )
            .limit(10)
            .all()
        )

        endpoints_found = [log.endpoint for log in any_success_logs]

        return {
            "success": True,
            "message": f"No call logs found matching criteria. Endpoints found: {endpoints_found}",
            "synced_count": 0,
            "total_logs": 0,
            "errors": [],
        }

    synced_count = 0
    errors = []

    for log in call_logs:
        savepoint = db.begin_nested()

        try:
            print(f"Processing log {log.id}...")
            response_body = log.response_body

            if not response_body or not isinstance(response_body, dict):
                error_msg = "Invalid response_body structure"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Extract POA data from response_body
            poa_data = response_body.get("data", response_body)

            if not poa_data or not isinstance(poa_data, dict):
                error_msg = "No data found in response_body"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Extract POA code/number as identifier
            # API response uses 'code' field
            poa_code = (
                poa_data.get("code")
                or poa_data.get("attorneyNumber")
                or poa_data.get("attorney_number")
            )
            if not poa_code:
                error_msg = "No attorney code/number found in data"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            print(f"  Processing POA: {poa_code}")

            # Check if we already synced this specific log using log_id column
            from app.models.wathq_power_of_attorney import PowerOfAttorney

            existing_poa = (
                db.query(PowerOfAttorney)
                .filter(PowerOfAttorney.log_id == log.id)
                .first()
            )

            if existing_poa:
                print(f"  Skipping POA {poa_code} - already synced from log {log.id}")
                savepoint.commit()
                continue

            print(f"  Creating new record for POA: {poa_code} from log {log.id}")
            _create_power_of_attorney(db, poa_data, log)

            savepoint.commit()
            synced_count += 1
            print(f"  Successfully synced POA: {poa_code}")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  Error processing log {log.id}: {error_msg}")
            import traceback

            traceback.print_exc()
            errors.append({"log_id": str(log.id), "error": error_msg})
            savepoint.rollback()
            continue

    try:
        db.commit()
        print(f"Successfully committed {synced_count} records")
    except Exception as e:
        print(f"Error committing to database: {str(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")

    return {
        "success": True,
        "message": f"Synced {synced_count} records from {len(call_logs)} call logs",
        "synced_count": synced_count,
        "total_logs": len(call_logs),
        "errors": errors,
    }


def _create_power_of_attorney(db: Session, poa_data: Dict, log: models.WathqCallLog):
    """Create a new power of attorney record with all related data."""
    from app.models.wathq_power_of_attorney import (
        PowerOfAttorney,
        PoaAllowedActor,
        PoaPrincipal,
        PoaAgent,
        PoaTextListItem,
    )

    # Extract nested objects
    location = poa_data.get("location", {}) or {}
    agents_behavior = poa_data.get("agentsBehavior", {}) or {}

    # Create main POA record
    # API response uses: code, issueHijriDate, issueGregDate, expiryHijriDate, expiryGregDate, text
    poa = PowerOfAttorney(
        log_id=log.id,
        fetched_at=log.fetched_at,
        code=str(
            poa_data.get("code")
            or poa_data.get("attorneyNumber")
            or poa_data.get("attorney_number")
        ),
        status=poa_data.get("status"),
        issue_hijri_date=poa_data.get("issueHijriDate")
        or poa_data.get("issueDateHijri")
        or poa_data.get("issue_hijri_date"),
        expiry_hijri_date=poa_data.get("expiryHijriDate")
        or poa_data.get("expiryDateHijri")
        or poa_data.get("expiry_hijri_date"),
        attorney_type=poa_data.get("attorneyType") or poa_data.get("attorney_type"),
        location_id=location.get("id"),
        location_name=location.get("name"),
        agents_behavior_ar=agents_behavior.get("ar"),
        agents_behavior_en=agents_behavior.get("en"),
        document_text=poa_data.get("text")
        or poa_data.get("attorneyText")
        or poa_data.get("attorney_text"),
        request_body=log.request_data,
    )

    db.add(poa)
    db.flush()  # Get the ID

    # Create related records
    _create_poa_allowed_actors(
        db,
        poa.id,
        poa_data.get("AllowedToActOnBehalf", []) or poa_data.get("allowed_actors", []),
    )
    _create_poa_principals(db, poa.id, poa_data.get("principals", []))
    _create_poa_agents(db, poa.id, poa_data.get("agents", []))
    _create_poa_text_list_items(
        db, poa.id, poa_data.get("textList", []) or poa_data.get("text_list", [])
    )

    return poa


def _create_poa_allowed_actors(db: Session, poa_id: int, actors: List[Dict]):
    """Create POA allowed actor records."""
    from app.models.wathq_power_of_attorney import PoaAllowedActor

    for actor_data in actors:
        actor = PoaAllowedActor(
            poa_id=poa_id,
            identity_no=actor_data.get("IdentityNo") or actor_data.get("identity_no"),
            social_type_id=actor_data.get("SocialTypeID")
            or actor_data.get("social_type_id"),
            social_type_name=actor_data.get("SocialTypeName")
            or actor_data.get("social_type_name"),
            name=actor_data.get("Name") or actor_data.get("name"),
            type_id=actor_data.get("Type") or actor_data.get("type_id"),
            type_name=actor_data.get("TypeName") or actor_data.get("type_name"),
            type_name_en=actor_data.get("TypeNameEn") or actor_data.get("type_name_en"),
            sefa_id=actor_data.get("SefaID") or actor_data.get("sefa_id"),
            sefa_name=actor_data.get("SefaName") or actor_data.get("sefa_name"),
            national_number=actor_data.get("NationalNumber")
            or actor_data.get("national_number"),
            cr_number=actor_data.get("CRNumber") or actor_data.get("cr_number"),
            karar_number=actor_data.get("KararNumber")
            or actor_data.get("karar_number"),
            malaki_number=actor_data.get("MalakiNumber")
            or actor_data.get("malaki_number"),
            document_type_name=actor_data.get("DocumentTypeName")
            or actor_data.get("document_type_name"),
            company_represent_type_id=actor_data.get("CompanyRepresentTypeID")
            or actor_data.get("company_represent_type_id"),
            company_represent_type_name=actor_data.get("CompanyRepresentTypeName")
            or actor_data.get("company_represent_type_name"),
            sakk_number=actor_data.get("SakkNumber") or actor_data.get("sakk_number"),
        )
        db.add(actor)


def _create_poa_principals(db: Session, poa_id: int, principals: List[Dict]):
    """Create POA principal records."""
    from app.models.wathq_power_of_attorney import PoaPrincipal

    for principal_data in principals:
        principal = PoaPrincipal(
            poa_id=poa_id,
            principal_identity_id=principal_data.get("id")
            or principal_data.get("principal_identity_id"),
            name=principal_data.get("name"),
            sefa_id=principal_data.get("SefaId") or principal_data.get("sefa_id"),
            sefa_name=principal_data.get("SefaName") or principal_data.get("sefa_name"),
        )
        db.add(principal)


def _create_poa_agents(db: Session, poa_id: int, agents: List[Dict]):
    """Create POA agent records."""
    from app.models.wathq_power_of_attorney import PoaAgent

    for agent_data in agents:
        agent = PoaAgent(
            poa_id=poa_id,
            agent_identity_id=agent_data.get("id")
            or agent_data.get("agent_identity_id"),
            name=agent_data.get("name"),
            sefa_id=agent_data.get("SefaId") or agent_data.get("sefa_id"),
            sefa_name=agent_data.get("SefaName") or agent_data.get("sefa_name"),
        )
        db.add(agent)


def _create_poa_text_list_items(db: Session, poa_id: int, items: List[Dict]):
    """Create POA text list item records."""
    from app.models.wathq_power_of_attorney import PoaTextListItem

    for item_data in items:
        item = PoaTextListItem(
            poa_id=poa_id,
            list_item_id=item_data.get("id") or item_data.get("list_item_id"),
            text_content=item_data.get("text") or item_data.get("text_content"),
            item_type=item_data.get("type") or item_data.get("item_type"),
        )
        db.add(item)


@router.post("/real-estate/sync", response_model=Dict[str, Any])
def sync_real_estate_from_logs(
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Sync real estate deed data from wathq_call_logs to deed tables.

    Filters:
    - status_code = 200
    - service_slug = 'real-estate'
    - endpoint starts with '/deed/'

    Parses response_body and creates/updates records in:
    - deeds
    - deed_owners
    - deed_real_estates
    """

    try:
        # Query wathq_call_logs with filters
        # API endpoint pattern is /deed/{cr_number}/{deed_number}/{copy_number}
        call_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "real-estate",
                    models.WathqCallLog.endpoint.like("/deed/%"),
                )
            )
            .all()
        )

        print(f"Found {len(call_logs)} logs matching /deed/% pattern for real-estate")
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    if not call_logs:
        # Try without the info filter to see what endpoints we have
        any_success_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "real-estate",
                )
            )
            .limit(10)
            .all()
        )

        endpoints_found = [log.endpoint for log in any_success_logs]

        return {
            "success": True,
            "message": f"No call logs found matching criteria. Endpoints found: {endpoints_found}",
            "synced_count": 0,
            "total_logs": 0,
            "errors": [],
        }

    synced_count = 0
    errors = []

    for log in call_logs:
        savepoint = db.begin_nested()

        try:
            print(f"Processing log {log.id}...")
            response_body = log.response_body

            if not response_body or not isinstance(response_body, dict):
                error_msg = "Invalid response_body structure"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Extract deed data from response_body
            # API response structure has nested objects: deedDetails, courtDetails, deedInfo, etc.
            deed_data = response_body.get("data", response_body)

            if not deed_data or not isinstance(deed_data, dict):
                error_msg = "No data found in response_body"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Extract deed identifier from nested deedDetails
            deed_details = deed_data.get("deedDetails", {}) or {}
            deed_number = (
                deed_details.get("deedNumber")
                or deed_details.get("deedSerial")
                or deed_data.get("deedNumber")
                or deed_data.get("deedSerial")
            )
            if not deed_number:
                error_msg = "No deed number/serial found in data"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            print(f"  Processing Deed: {deed_number}")

            # Check if we already synced this specific log using log_id column
            from app.models.wathq_real_estate_deed import Deed

            existing_deed = db.query(Deed).filter(Deed.log_id == log.id).first()

            if existing_deed:
                print(
                    f"  Skipping Deed {deed_number} - already synced from log {log.id}"
                )
                savepoint.commit()
                continue

            print(f"  Creating new record for Deed: {deed_number} from log {log.id}")
            _create_deed(db, deed_data, log)

            savepoint.commit()
            synced_count += 1
            print(f"  Successfully synced Deed: {deed_number}")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  Error processing log {log.id}: {error_msg}")
            import traceback

            traceback.print_exc()
            errors.append({"log_id": str(log.id), "error": error_msg})
            savepoint.rollback()
            continue

    try:
        db.commit()
        print(f"Successfully committed {synced_count} records")
    except Exception as e:
        print(f"Error committing to database: {str(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")

    return {
        "success": True,
        "message": f"Synced {synced_count} records from {len(call_logs)} call logs",
        "synced_count": synced_count,
        "total_logs": len(call_logs),
        "errors": errors,
    }


def _create_deed(db: Session, deed_data: Dict, log: models.WathqCallLog):
    """Create a new deed record with all related data."""
    from app.models.wathq_real_estate_deed import Deed, DeedOwner, DeedRealEstate

    # Extract nested objects from API response
    # API structure: deedDetails, courtDetails, deedInfo, deedLimitsDetails, ownerDetails, realEstateDetails
    deed_details = deed_data.get("deedDetails", {}) or {}
    court_details = deed_data.get("courtDetails", {}) or {}
    deed_info = deed_data.get("deedInfo", {}) or {}
    limits = deed_data.get("deedLimitsDetails", {}) or {}

    # Create main deed record
    deed = Deed(
        log_id=log.id,
        fetched_at=log.fetched_at,
        deed_number=deed_details.get("deedNumber") or deed_data.get("deedNumber"),
        deed_serial=deed_details.get("deedSerial") or deed_data.get("deedSerial"),
        deed_date=deed_details.get("deedDate") or deed_data.get("deedDate"),
        deed_text=deed_details.get("deedText") or deed_data.get("deedText"),
        deed_source=court_details.get("deedSource") or deed_data.get("deedSource"),
        deed_city=court_details.get("deedCity") or deed_data.get("deedCity"),
        deed_status=deed_data.get("deedStatus"),
        deed_area=deed_info.get("deedArea") or deed_data.get("deedArea"),
        deed_area_text=deed_info.get("deedAreaText") or deed_data.get("deedAreaText"),
        is_real_estate_constrained=deed_info.get("isRealEstateConstrained")
        or deed_data.get("isRealEstateConstrained"),
        is_real_estate_halted=deed_info.get("isRealEstateHalted")
        or deed_data.get("isRealEstateHalted"),
        is_real_estate_mortgaged=deed_info.get("isRealEstateMortgaged")
        or deed_data.get("isRealEstateMortgaged"),
        is_real_estate_testamented=deed_info.get("isRealEstateTestamented")
        or deed_data.get("isRealEstateTestamented"),
        # North limit
        limit_north_name=limits.get("northLimitName"),
        limit_north_description=limits.get("northLimitDescription"),
        limit_north_length=limits.get("northLimitLength"),
        limit_north_length_char=limits.get("northLimitLengthChar"),
        # South limit
        limit_south_name=limits.get("southLimitName"),
        limit_south_description=limits.get("southLimitDescription"),
        limit_south_length=limits.get("southLimitLength"),
        limit_south_length_char=limits.get("southLimitLengthChar"),
        # East limit
        limit_east_name=limits.get("eastLimitName"),
        limit_east_description=limits.get("eastLimitDescription"),
        limit_east_length=limits.get("eastLimitLength"),
        limit_east_length_char=limits.get("eastLimitLengthChar"),
        # West limit
        limit_west_name=limits.get("westLimitName"),
        limit_west_description=limits.get("westLimitDescription"),
        limit_west_length=limits.get("westLimitLength"),
        limit_west_length_char=limits.get("westLimitLengthChar"),
        request_body=log.request_data,
    )

    db.add(deed)
    db.flush()  # Get the ID

    # Create related records - API uses ownerDetails and realEstateDetails
    _create_deed_owners(
        db, deed.id, deed_data.get("ownerDetails", []) or deed_data.get("owners", [])
    )
    _create_deed_real_estates(
        db,
        deed.id,
        deed_data.get("realEstateDetails", []) or deed_data.get("realEstates", []),
    )

    return deed


def _create_deed_owners(db: Session, deed_id: int, owners: List[Dict]):
    """Create deed owner records."""
    from app.models.wathq_real_estate_deed import DeedOwner

    for owner_data in owners:
        owner = DeedOwner(
            deed_id=deed_id,
            owner_name=owner_data.get("ownerName")
            or owner_data.get("owner_name")
            or owner_data.get("name"),
            birth_date=owner_data.get("birthDate") or owner_data.get("birth_date"),
            id_number=owner_data.get("idNumber") or owner_data.get("id_number"),
            id_type=owner_data.get("idType") or owner_data.get("id_type"),
            id_type_text=owner_data.get("idTypeText") or owner_data.get("id_type_text"),
            owner_type=owner_data.get("ownerType") or owner_data.get("owner_type"),
            nationality=owner_data.get("nationality"),
            owning_area=owner_data.get("owningArea") or owner_data.get("owning_area"),
            owning_amount=owner_data.get("owningAmount")
            or owner_data.get("owning_amount"),
            constrained=owner_data.get("constrained"),
            halt=owner_data.get("halt"),
            pawned=owner_data.get("pawned"),
            testament=owner_data.get("testament"),
        )
        db.add(owner)


def _create_deed_real_estates(db: Session, deed_id: int, real_estates: List[Dict]):
    """Create deed real estate records."""
    from app.models.wathq_real_estate_deed import DeedRealEstate

    for re_data in real_estates:
        # Extract borders - API uses realEstateBorderDetails
        borders = (
            re_data.get("realEstateBorderDetails", {})
            or re_data.get("borders", {})
            or {}
        )

        real_estate = DeedRealEstate(
            deed_id=deed_id,
            deed_serial=re_data.get("deedSerial") or re_data.get("deed_serial"),
            region_code=re_data.get("regionCode") or re_data.get("region_code"),
            region_name=re_data.get("regionName") or re_data.get("region_name"),
            city_code=re_data.get("cityCode") or re_data.get("city_code"),
            city_name=re_data.get("cityName") or re_data.get("city_name"),
            real_estate_type_name=re_data.get("realEstateTypeName")
            or re_data.get("real_estate_type_name"),
            land_number=re_data.get("landNumber") or re_data.get("land_number"),
            plan_number=re_data.get("planNumber") or re_data.get("plan_number"),
            area=re_data.get("area"),
            area_text=re_data.get("areaText") or re_data.get("area_text"),
            district_code=re_data.get("districtCode") or re_data.get("district_code"),
            district_name=re_data.get("districtName") or re_data.get("district_name"),
            location_description=re_data.get("locationDescription")
            or re_data.get("location_description"),
            constrained=re_data.get("constrained"),
            halt=re_data.get("halt"),
            pawned=re_data.get("pawned"),
            testament=re_data.get("testament"),
            is_north_riyadh_exceptioned=re_data.get("isNorthRiyadhExceptioned")
            or re_data.get("is_north_riyadh_exceptioned"),
            # Border descriptions - API uses northLimitDescription, etc.
            border_north_description=borders.get("northLimitDescription"),
            border_north_length=borders.get("northLimitLength"),
            border_north_length_char=borders.get("northLimitLengthChar"),
            border_south_description=borders.get("southLimitDescription"),
            border_south_length=borders.get("southLimitLength"),
            border_south_length_char=borders.get("southLimitLengthChar"),
            border_east_description=borders.get("eastLimitDescription"),
            border_east_length=borders.get("eastLimitLength"),
            border_east_length_char=borders.get("eastLimitLengthChar"),
            border_west_description=borders.get("westLimitDescription"),
            border_west_length=borders.get("westLimitLength"),
            border_west_length_char=borders.get("westLimitLengthChar"),
        )
        db.add(real_estate)


@router.post("/national-address/sync", response_model=Dict[str, Any])
def sync_national_address_from_logs(
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Sync national address data from wathq_call_logs to addresses table.

    Filters:
    - status_code = 200
    - service_slug = 'national-address'
    - endpoint starts with '/info/' or '/address/'

    Parses response_body and creates records in:
    - addresses
    """

    try:
        # Query wathq_call_logs with filters
        call_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "national-address",
                )
            )
            .all()
        )

        print(f"Found {len(call_logs)} logs for national-address")
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    if not call_logs:
        return {
            "success": True,
            "message": "No call logs found matching criteria",
            "synced_count": 0,
            "total_logs": 0,
            "errors": [],
        }

    synced_count = 0
    errors = []

    for log in call_logs:
        savepoint = db.begin_nested()

        try:
            print(f"Processing log {log.id}...")
            response_body = log.response_body

            if not response_body:
                error_msg = "Empty response_body"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Handle response_body being an array directly (API returns array of addresses)
            if isinstance(response_body, list):
                addresses_list = response_body
            elif isinstance(response_body, dict):
                # Extract address data from response_body
                address_data = response_body.get("data", response_body)
                # Handle case where data is a list of addresses
                if isinstance(address_data, list):
                    addresses_list = address_data
                elif isinstance(address_data, dict):
                    # Could be single address or have addresses nested
                    addresses_list = address_data.get("addresses", [address_data])
                else:
                    error_msg = "No valid address data found in response_body"
                    print(f"  Error: {error_msg}")
                    errors.append({"log_id": str(log.id), "error": error_msg})
                    savepoint.rollback()
                    continue
            else:
                error_msg = "Invalid response_body structure"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            if not addresses_list:
                error_msg = "Empty address data"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Check if we already synced this specific log using log_id column
            from app.models.wathq_national_address import Address

            existing_address = (
                db.query(Address).filter(Address.log_id == log.id).first()
            )

            if existing_address:
                print(f"  Skipping - already synced from log {log.id}")
                savepoint.commit()
                continue

            # Create address records for each address in the response
            for addr_data in addresses_list:
                if isinstance(addr_data, dict):
                    _create_address(db, addr_data, log)

            savepoint.commit()
            synced_count += 1
            print(
                f"  Successfully synced {len(addresses_list)} address(es) from log {log.id}"
            )

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  Error processing log {log.id}: {error_msg}")
            import traceback

            traceback.print_exc()
            errors.append({"log_id": str(log.id), "error": error_msg})
            savepoint.rollback()
            continue

    try:
        db.commit()
        print(f"Successfully committed {synced_count} records")
    except Exception as e:
        print(f"Error committing to database: {str(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")

    return {
        "success": True,
        "message": f"Synced {synced_count} records from {len(call_logs)} call logs",
        "synced_count": synced_count,
        "total_logs": len(call_logs),
        "errors": errors,
    }


def _create_address(db: Session, addr_data: Dict, log: models.WathqCallLog):
    """Create a new address record."""
    from app.models.wathq_national_address import Address

    address = Address(
        log_id=log.id,
        fetched_at=log.fetched_at,
        pk_address_id=addr_data.get("pkAddressId")
        or addr_data.get("pk_address_id")
        or addr_data.get("addressId"),
        title=addr_data.get("title"),
        address=addr_data.get("address") or addr_data.get("address1"),
        address2=addr_data.get("address2"),
        latitude=addr_data.get("latitude"),
        longitude=addr_data.get("longitude"),
        building_number=addr_data.get("buildingNumber")
        or addr_data.get("building_number"),
        street=addr_data.get("street") or addr_data.get("streetName"),
        district=addr_data.get("district") or addr_data.get("districtName"),
        district_id=addr_data.get("districtId") or addr_data.get("district_id"),
        city=addr_data.get("city") or addr_data.get("cityName"),
        city_id=addr_data.get("cityId") or addr_data.get("city_id"),
        post_code=addr_data.get("postCode")
        or addr_data.get("post_code")
        or addr_data.get("zipCode"),
        additional_number=addr_data.get("additionalNumber")
        or addr_data.get("additional_number"),
        region_name=addr_data.get("regionName")
        or addr_data.get("region_name")
        or addr_data.get("region"),
        region_id=addr_data.get("regionId") or addr_data.get("region_id"),
        is_primary_address=addr_data.get("isPrimaryAddress")
        or addr_data.get("is_primary_address")
        or addr_data.get("isPrimary"),
        unit_number=addr_data.get("unitNumber") or addr_data.get("unit_number"),
        restriction=addr_data.get("restriction"),
        status=addr_data.get("status"),
        request_body=log.request_data,
    )

    db.add(address)
    return address


@router.post("/employee/sync", response_model=Dict[str, Any])
def sync_employee_from_logs(
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Sync employee data from wathq_call_logs to employees table.

    Filters:
    - status_code = 200
    - service_slug = 'employee-verification'

    Parses response_body and creates records in:
    - employees
    - employment_details
    """

    try:
        # Query wathq_call_logs with filters
        call_logs = (
            db.query(models.WathqCallLog)
            .filter(
                and_(
                    models.WathqCallLog.status_code == 200,
                    models.WathqCallLog.service_slug == "employee-verification",
                )
            )
            .all()
        )

        print(f"Found {len(call_logs)} logs for employee-verification")
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    if not call_logs:
        return {
            "success": True,
            "message": "No call logs found matching criteria",
            "synced_count": 0,
            "total_logs": 0,
            "errors": [],
        }

    synced_count = 0
    errors = []

    for log in call_logs:
        savepoint = db.begin_nested()

        try:
            print(f"Processing log {log.id}...")
            response_body = log.response_body

            if not response_body or not isinstance(response_body, dict):
                error_msg = "Invalid response_body structure"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Extract employee data from response_body
            emp_data = response_body.get("data", response_body)

            if not emp_data or not isinstance(emp_data, dict):
                error_msg = "No valid employee data found in response_body"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            # Get employee identifier
            emp_name = emp_data.get("name") or emp_data.get("employeeName")
            if not emp_name:
                error_msg = "No employee name found in data"
                print(f"  Error: {error_msg}")
                errors.append({"log_id": str(log.id), "error": error_msg})
                savepoint.rollback()
                continue

            print(f"  Processing Employee: {emp_name}")

            # Check if we already synced this specific log using log_id column
            from app.models.wathq_employee import Employee

            existing_employee = (
                db.query(Employee).filter(Employee.log_id == log.id).first()
            )

            if existing_employee:
                print(
                    f"  Skipping Employee {emp_name} - already synced from log {log.id}"
                )
                savepoint.commit()
                continue

            print(f"  Creating new record for Employee: {emp_name} from log {log.id}")
            _create_employee(db, emp_data, log)

            savepoint.commit()
            synced_count += 1
            print(f"  Successfully synced Employee: {emp_name}")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  Error processing log {log.id}: {error_msg}")
            import traceback

            traceback.print_exc()
            errors.append({"log_id": str(log.id), "error": error_msg})
            savepoint.rollback()
            continue

    try:
        db.commit()
        print(f"Successfully committed {synced_count} records")
    except Exception as e:
        print(f"Error committing to database: {str(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")

    return {
        "success": True,
        "message": f"Synced {synced_count} records from {len(call_logs)} call logs",
        "synced_count": synced_count,
        "total_logs": len(call_logs),
        "errors": errors,
    }


def _create_employee(db: Session, emp_data: Dict, log: models.WathqCallLog):
    """Create a new employee record with employment details."""
    from app.models.wathq_employee import Employee, EmploymentDetail

    employee = Employee(
        log_id=log.id,
        fetched_at=log.fetched_at,
        name=emp_data.get("name") or emp_data.get("employeeName"),
        nationality=emp_data.get("nationality"),
        working_months=emp_data.get("workingMonths") or emp_data.get("working_months"),
        request_body=log.request_data,
    )

    db.add(employee)
    db.flush()  # Get the ID

    # Create employment details
    # API uses employmentInfo with nested wageDetails
    employment_list = (
        emp_data.get("employmentInfo", [])
        or emp_data.get("employmentDetails", [])
        or emp_data.get("employment_details", [])
        or emp_data.get("employments", [])
    )

    # If no list, check if there's a single employment record at root level
    if not employment_list and (emp_data.get("employer") or emp_data.get("status")):
        employment_list = [emp_data]

    for detail_data in employment_list:
        if isinstance(detail_data, dict):
            # Extract wage details from nested wageDetails object
            wage_details = detail_data.get("wageDetails", {}) or {}

            detail = EmploymentDetail(
                employee_id=employee.employee_id,
                employer=detail_data.get("employer") or detail_data.get("employerName"),
                status=detail_data.get("status"),
                basic_wage=wage_details.get("basicWage")
                or detail_data.get("basicWage")
                or detail_data.get("basic_wage"),
                housing_allowance=wage_details.get("housingAllowance")
                or detail_data.get("housingAllowance")
                or detail_data.get("housing_allowance"),
                other_allowance=wage_details.get("otherAllowance")
                or detail_data.get("otherAllowance")
                or detail_data.get("other_allowance"),
                full_wage=wage_details.get("fullWage")
                or detail_data.get("fullWage")
                or detail_data.get("full_wage"),
            )
            db.add(detail)

    return employee
