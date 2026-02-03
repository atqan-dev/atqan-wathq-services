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
        all_cr_logs = db.query(models.WathqCallLog).filter(
            models.WathqCallLog.service_slug == 'commercial-registration'
        ).all()
        
        print(f"Found {len(all_cr_logs)} commercial-registration logs in database")
        for log in all_cr_logs[:5]:  # Print first 5 for debugging
            print(f"  - endpoint: {log.endpoint}, status: {log.status_code}")
        
        # Query wathq_call_logs with filters - match /fullinfo/* pattern
        call_logs = db.query(models.WathqCallLog).filter(
            and_(
                models.WathqCallLog.status_code == 200,
                models.WathqCallLog.service_slug == 'commercial-registration',
                models.WathqCallLog.endpoint.like('/fullinfo/%')
            )
        ).all()
        
        print(f"Found {len(call_logs)} logs matching /fullinfo/% pattern")
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    
    if not call_logs:
        # Try without the fullinfo filter to see what endpoints we have
        any_success_logs = db.query(models.WathqCallLog).filter(
            and_(
                models.WathqCallLog.status_code == 200,
                models.WathqCallLog.service_slug == 'commercial-registration'
            )
        ).limit(10).all()
        
        endpoints_found = [log.endpoint for log in any_success_logs]
        
        return {
            "success": True,
            "message": f"No call logs found matching criteria. Found {len(all_cr_logs)} CR logs total, but none with endpoint like 'fullinfo/%'. Endpoints found: {endpoints_found}",
            "synced_count": 0,
            "total_logs": 0,
            "errors": []
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
                errors.append({
                    "log_id": str(log.id),
                    "error": error_msg
                })
                savepoint.rollback()
                continue
            
            # Extract CR data from response_body
            # The structure might be: {"data": {...}} or direct data
            cr_data = response_body.get('data', response_body)
            
            if not cr_data or not isinstance(cr_data, dict):
                error_msg = "No data found in response_body"
                print(f"  Error: {error_msg}")
                errors.append({
                    "log_id": str(log.id),
                    "error": error_msg
                })
                savepoint.rollback()
                continue
            
            # Extract cr_number
            cr_number = cr_data.get('crNumber') or cr_data.get('cr_number')
            if not cr_number:
                error_msg = "No cr_number found in data"
                print(f"  Error: {error_msg}")
                errors.append({
                    "log_id": str(log.id),
                    "error": error_msg
                })
                savepoint.rollback()
                continue
            
            print(f"  Processing CR: {cr_number}")
            
            # Always create new records to maintain historical data
            # Check if we already synced this specific log by log_id
            existing_cr = db.query(models.CommercialRegistration).filter(
                models.CommercialRegistration.log_id == log.id
            ).first()
            
            if existing_cr:
                print(f"  Skipping CR {cr_number} - already synced from log {log.id}")
                savepoint.commit()
                continue
            
            print(f"  Creating new historical record for CR: {cr_number} from log {log.id}")
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
            errors.append({
                "log_id": str(log.id),
                "error": error_msg
            })
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
        "errors": errors
    }


def _create_commercial_registration(db: Session, cr_data: Dict, log: models.WathqCallLog) -> models.CommercialRegistration:
    """Create a new commercial registration record with all related data."""
    
    # Extract nested objects
    entity_type = cr_data.get('entityType', {}) or {}
    status = cr_data.get('status', {}) or {}
    contact_info = cr_data.get('contactInfo', {}) or {}
    fiscal_year = cr_data.get('fiscalYear', {}) or {}
    management = cr_data.get('management', {}) or {}
    
    # Create main CR record
    cr = models.CommercialRegistration(
        log_id=log.id,  # Link to the source call log
        cr_number=cr_data.get('crNumber') or cr_data.get('cr_number'),
        cr_national_number=cr_data.get('crNationalNumber'),
        version_no=cr_data.get('versionNo'),
        fetched_at=log.fetched_at,  # Track when this data was fetched
        name=cr_data.get('name'),
        name_lang_id=cr_data.get('nameLangId'),
        name_lang_desc=cr_data.get('nameLangDesc'),
        cr_capital=cr_data.get('crCapital'),
        company_duration=cr_data.get('companyDuration'),
        is_main=cr_data.get('isMain'),
        issue_date_gregorian=cr_data.get('issueDateGregorian'),
        issue_date_hijri=cr_data.get('issueDateHijri'),
        main_cr_national_number=cr_data.get('mainCrNationalNumber'),
        main_cr_number=cr_data.get('mainCrNumber'),
        in_liquidation_process=cr_data.get('inLiquidationProcess'),
        has_ecommerce=cr_data.get('hasEcommerce'),
        headquarter_city_id=cr_data.get('headquarterCityId'),
        headquarter_city_name=cr_data.get('headquarterCityName'),
        is_license_based=cr_data.get('isLicenseBased'),
        license_issuer_national_number=cr_data.get('licenseIssuerNationalNumber'),
        license_issuer_name=cr_data.get('licenseIssuerName'),
        partners_nationality_id=cr_data.get('partnersNationalityId'),
        partners_nationality_name=cr_data.get('partnersNationalityName'),
        # Extract from entityType object
        entity_type_id=entity_type.get('id'),
        entity_type_name=entity_type.get('name'),
        entity_form_id=entity_type.get('formId'),
        entity_form_name=entity_type.get('formName'),
        # Extract from status object
        status_id=status.get('id'),
        status_name=status.get('name'),
        confirmation_date_gregorian=status.get('confirmationDate', {}).get('gregorian') if status.get('confirmationDate') else None,
        confirmation_date_hijri=status.get('confirmationDate', {}).get('hijri') if status.get('confirmationDate') else None,
        reactivation_date_gregorian=status.get('reactivationDate', {}).get('gregorian') if status.get('reactivationDate') else None,
        reactivation_date_hijri=status.get('reactivationDate', {}).get('hijri') if status.get('reactivationDate') else None,
        suspension_date_gregorian=status.get('suspensionDate', {}).get('gregorian') if status.get('suspensionDate') else None,
        suspension_date_hijri=status.get('suspensionDate', {}).get('hijri') if status.get('suspensionDate') else None,
        deletion_date_gregorian=status.get('deletionDate', {}).get('gregorian') if status.get('deletionDate') else None,
        deletion_date_hijri=status.get('deletionDate', {}).get('hijri') if status.get('deletionDate') else None,
        # Extract from contactInfo object
        contact_phone=contact_info.get('phoneNo'),
        contact_mobile=contact_info.get('mobileNo'),
        contact_email=contact_info.get('email'),
        contact_website=contact_info.get('websiteUrl'),
        # Extract from fiscalYear object
        fiscal_is_first=fiscal_year.get('isFirst'),
        fiscal_calendar_type_id=fiscal_year.get('calendarTypeId'),
        fiscal_calendar_type_name=fiscal_year.get('calendarTypeName'),
        fiscal_end_month=fiscal_year.get('endMonth'),
        fiscal_end_day=fiscal_year.get('endDay'),
        fiscal_end_year=fiscal_year.get('endYear'),
        # Extract from management object
        mgmt_structure_id=management.get('structureId'),
        mgmt_structure_name=management.get('structureName'),
        request_body=log.request_data
    )
    
    db.add(cr)
    db.flush()  # Get the ID
    
    # Create related records
    _create_capital_info(db, cr.id, cr_data.get('capitalInfo'))
    _create_activities(db, cr.id, cr_data.get('activities', []))
    _create_parties(db, cr.id, cr_data.get('parties', []))
    _create_managers(db, cr.id, cr_data.get('managers', []))
    _create_entity_characters(db, cr.id, cr_data.get('entityCharacters', []))
    _create_stocks(db, cr.id, cr_data.get('stocks', []))
    _create_estores(db, cr.id, cr_data.get('estores', []))
    _create_liquidators(db, cr.id, cr_data.get('liquidators', []))
    
    return cr


def _create_capital_info(db: Session, cr_id: int, capital_data: Dict):
    """Create capital info record."""
    if not capital_data:
        return
    
    capital = models.CapitalInfo(
        cr_id=cr_id,
        capital_amount=capital_data.get('capitalAmount'),
        capital_currency_id=capital_data.get('capitalCurrencyId'),
        capital_currency_name=capital_data.get('capitalCurrencyName'),
        paid_amount=capital_data.get('paidAmount'),
        remaining_amount=capital_data.get('remainingAmount')
    )
    db.add(capital)


def _create_activities(db: Session, cr_id: int, activities: List[Dict]):
    """Create activity records."""
    for activity_data in activities:
        activity = models.CRActivity(
            cr_id=cr_id,
            activity_id=activity_data.get('activityId'),
            activity_name=activity_data.get('activityName'),
            is_main=activity_data.get('isMain')
        )
        db.add(activity)


def _create_parties(db: Session, cr_id: int, parties: List[Dict]):
    """Create party records."""
    for party_data in parties:
        party = models.CRParty(
            cr_id=cr_id,
            cr_number=party_data.get('crNumber'),  
            name=party_data.get('name'),
            type_id=party_data.get('typeId'),
            type_name=party_data.get('typeName'),
            identity_id=party_data.get('identityId'),
            identity_type_id=party_data.get('identityTypeId'),
            identity_type_name=party_data.get('identityTypeName'),
            share_cash_count=party_data.get('shareCashCount'),
            share_in_kind_count=party_data.get('shareInKindCount'),
            share_total_count=party_data.get('shareTotalCount')
        )
        db.add(party)


def _create_managers(db: Session, cr_id: int, managers: List[Dict]):
    """Create manager records."""
    for manager_data in managers:
        manager = models.CRManager(
            cr_id=cr_id,
            cr_number=manager_data.get('crNumber'),
            name=manager_data.get('name'),
            type_id=manager_data.get('typeId'),
            type_name=manager_data.get('typeName'),
            is_licensed=manager_data.get('isLicensed'),
            identity_id=manager_data.get('identityId'),
            identity_type_id=manager_data.get('identityTypeId'),
            identity_type_name=manager_data.get('identityTypeName'),
            nationality_id=manager_data.get('nationalityId'),
            nationality_name=manager_data.get('nationalityName')
        )
        db.add(manager)


def _create_entity_characters(db: Session, cr_id: int, characters: List[Dict]):
    """Create entity character records."""
    for char_data in characters:
        character = models.CREntityCharacter(
            cr_id=cr_id,
            cr_number=char_data.get('crNumber'),
            character_id=char_data.get('id'),
            character_name=char_data.get('name')
        )
        db.add(character)


def _create_stocks(db: Session, cr_id: int, stocks: List[Dict]):
    """Create stock records."""
    for stock_data in stocks:
        stock = models.CRStock(
            cr_id=cr_id,
            cr_number=stock_data.get('crNumber'),
            type_id=stock_data.get('typeId'),
            type_name=stock_data.get('typeName'),
            count=stock_data.get('count'),
            value=stock_data.get('value')
        )
        db.add(stock)


def _create_estores(db: Session, cr_id: int, estores: List[Dict]):
    """Create estore records."""
    for estore_data in estores:
        estore = models.CREstore(
            cr_id=cr_id,
            cr_number=estore_data.get('crNumber'),
            name=estore_data.get('name'),
            url=estore_data.get('url'),
            type_id=estore_data.get('typeId'),
            type_name=estore_data.get('typeName')
        )
        db.add(estore)


def _create_liquidators(db: Session, cr_id: int, liquidators: List[Dict]):
    """Create liquidator records."""
    for liquidator_data in liquidators:
        liquidator = models.CRLiquidator(
            cr_id=cr_id,
            cr_number=liquidator_data.get('crNumber'),
            name=liquidator_data.get('name'),
            type_id=liquidator_data.get('typeId'),
            type_name=liquidator_data.get('typeName'),
            identity_id=liquidator_data.get('identityId'),
            identity_type_id=liquidator_data.get('identityTypeId'),
            identity_type_name=liquidator_data.get('identityTypeName'),
            nationality_id=liquidator_data.get('nationalityId'),
            nationality_name=liquidator_data.get('nationalityName')
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
        call_logs = db.query(models.WathqCallLog).filter(
            and_(
                models.WathqCallLog.status_code == 200,
                models.WathqCallLog.service_slug == 'company-contract',
                models.WathqCallLog.endpoint.like('/info/%')
            )
        ).all()
        
        print(f"Found {len(call_logs)} logs matching /info/% pattern for company-contract")
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    
    if not call_logs:
        # Try without the info filter to see what endpoints we have
        any_success_logs = db.query(models.WathqCallLog).filter(
            and_(
                models.WathqCallLog.status_code == 200,
                models.WathqCallLog.service_slug == 'company-contract'
            )
        ).limit(10).all()
        
        endpoints_found = [log.endpoint for log in any_success_logs]
        
        return {
            "success": True,
            "message": f"No call logs found matching criteria. Endpoints found: {endpoints_found}",
            "synced_count": 0,
            "total_logs": 0,
            "errors": []
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
                errors.append({
                    "log_id": str(log.id),
                    "error": error_msg
                })
                savepoint.rollback()
                continue
            
            # Extract contract data from response_body
            contract_data = response_body.get('data', response_body)
            
            if not contract_data or not isinstance(contract_data, dict):
                error_msg = "No data found in response_body"
                print(f"  Error: {error_msg}")
                errors.append({
                    "log_id": str(log.id),
                    "error": error_msg
                })
                savepoint.rollback()
                continue
            
            # Extract contract_id
            contract_id = contract_data.get('contractId') or contract_data.get('contract_id')
            if not contract_id:
                error_msg = "No contract_id found in data"
                print(f"  Error: {error_msg}")
                errors.append({
                    "log_id": str(log.id),
                    "error": error_msg
                })
                savepoint.rollback()
                continue
            
            print(f"  Processing Contract ID: {contract_id}")
            
            # Check if we already synced this specific log
            from app.models.wathq_corporate_contract import CorporateContract
            existing_contract = db.query(CorporateContract).filter(
                CorporateContract.request_body['log_id'].astext == str(log.id)
            ).first()
            
            if existing_contract:
                print(f"  Skipping Contract {contract_id} - already synced from log {log.id}")
                savepoint.commit()
                continue
            
            print(f"  Creating new record for Contract: {contract_id} from log {log.id}")
            _create_corporate_contract(db, contract_data, log)
            
            savepoint.commit()
            synced_count += 1
            print(f"  Successfully synced Contract: {contract_id}")
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  Error processing log {log.id}: {error_msg}")
            import traceback
            traceback.print_exc()
            errors.append({
                "log_id": str(log.id),
                "error": error_msg
            })
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
        "errors": errors
    }


def _create_corporate_contract(db: Session, contract_data: Dict, log: models.WathqCallLog):
    """Create a new corporate contract record with all related data."""
    from app.models.wathq_corporate_contract import (
        CorporateContract, ContractStock, ContractParty, ContractManager,
        ContractManagementConfig, ContractActivity, ContractArticle,
        ContractDecision, NotificationChannel
    )
    
    # Extract nested objects
    entity_type = contract_data.get('entityType', {}) or {}
    fiscal_year = contract_data.get('fiscalYear', {}) or {}
    capital_info = contract_data.get('capitalInfo', {}) or {}
    management = contract_data.get('management', {}) or {}
    
    # Create main contract record
    contract = CorporateContract(
        contract_id=contract_data.get('contractId') or contract_data.get('contract_id'),
        contract_copy_number=contract_data.get('contractCopyNumber') or contract_data.get('contract_copy_number'),
        contract_date=contract_data.get('contractDate') or contract_data.get('contract_date'),
        cr_national_number=contract_data.get('crNationalNumber') or contract_data.get('cr_national_number'),
        cr_number=contract_data.get('crNumber') or contract_data.get('cr_number'),
        entity_name=contract_data.get('entityName') or contract_data.get('entity_name'),
        entity_name_lang_desc=contract_data.get('entityNameLangDesc') or contract_data.get('entity_name_lang_desc'),
        company_duration=contract_data.get('companyDuration') or contract_data.get('company_duration'),
        headquarter_city_name=contract_data.get('headquarterCityName') or contract_data.get('headquarter_city_name'),
        is_license_based=contract_data.get('isLicenseBased') or contract_data.get('is_license_based'),
        entity_type_name=entity_type.get('name') or contract_data.get('entity_type_name'),
        entity_form_name=entity_type.get('formName') or contract_data.get('entity_form_name'),
        fiscal_calendar_type=fiscal_year.get('calendarTypeName') or contract_data.get('fiscal_calendar_type'),
        fiscal_year_end_month=fiscal_year.get('endMonth') or contract_data.get('fiscal_year_end_month'),
        fiscal_year_end_day=fiscal_year.get('endDay') or contract_data.get('fiscal_year_end_day'),
        fiscal_year_end_year=fiscal_year.get('endYear') or contract_data.get('fiscal_year_end_year'),
        currency_name=capital_info.get('currencyName') or contract_data.get('currency_name'),
        total_capital=capital_info.get('totalCapital') or contract_data.get('total_capital'),
        paid_capital=capital_info.get('paidCapital') or contract_data.get('paid_capital'),
        cash_capital=capital_info.get('cashCapital') or contract_data.get('cash_capital'),
        in_kind_capital=capital_info.get('inKindCapital') or contract_data.get('in_kind_capital'),
        is_set_aside_enabled=contract_data.get('isSetAsideEnabled') or contract_data.get('is_set_aside_enabled'),
        profit_allocation_percentage=contract_data.get('profitAllocationPercentage') or contract_data.get('profit_allocation_percentage'),
        profit_allocation_purpose=contract_data.get('profitAllocationPurpose') or contract_data.get('profit_allocation_purpose'),
        additional_decision_text=contract_data.get('additionalDecisionText') or contract_data.get('additional_decision_text'),
        request_body={'log_id': str(log.id), 'fetched_at': str(log.fetched_at)}
    )
    
    db.add(contract)
    db.flush()  # Get the ID
    
    # Create related records
    _create_contract_stocks(db, contract.id, contract_data.get('stocks', []))
    _create_contract_parties(db, contract.id, contract_data.get('parties', []))
    _create_contract_managers(db, contract.id, contract_data.get('managers', []))
    _create_contract_management_config(db, contract.id, management)
    _create_contract_activities(db, contract.id, contract_data.get('activities', []))
    _create_contract_articles(db, contract.id, contract_data.get('articles', []))
    _create_contract_decisions(db, contract.id, contract_data.get('decisions', []))
    _create_notification_channels(db, contract.id, contract_data.get('notificationChannels', []))
    
    return contract


def _create_contract_stocks(db: Session, contract_id: int, stocks: List[Dict]):
    """Create contract stock records."""
    from app.models.wathq_corporate_contract import ContractStock
    for stock_data in stocks:
        stock = ContractStock(
            contract_id=contract_id,
            stock_type_name=stock_data.get('stockTypeName') or stock_data.get('stock_type_name'),
            stock_count=stock_data.get('stockCount') or stock_data.get('stock_count'),
            stock_value=stock_data.get('stockValue') or stock_data.get('stock_value')
        )
        db.add(stock)


def _create_contract_parties(db: Session, contract_id: int, parties: List[Dict]):
    """Create contract party records."""
    from app.models.wathq_corporate_contract import ContractParty
    for party_data in parties:
        party = ContractParty(
            contract_id=contract_id,
            name=party_data.get('name'),
            type_name=party_data.get('typeName') or party_data.get('type_name'),
            identity_number=party_data.get('identityNumber') or party_data.get('identity_number'),
            identity_type=party_data.get('identityType') or party_data.get('identity_type'),
            nationality=party_data.get('nationality'),
            guardian_name=party_data.get('guardianName') or party_data.get('guardian_name')
        )
        db.add(party)


def _create_contract_managers(db: Session, contract_id: int, managers: List[Dict]):
    """Create contract manager records."""
    from app.models.wathq_corporate_contract import ContractManager
    for manager_data in managers:
        manager = ContractManager(
            contract_id=contract_id,
            name=manager_data.get('name'),
            type_name=manager_data.get('typeName') or manager_data.get('type_name'),
            is_licensed=manager_data.get('isLicensed') or manager_data.get('is_licensed'),
            identity_number=manager_data.get('identityNumber') or manager_data.get('identity_number'),
            nationality=manager_data.get('nationality'),
            position_name=manager_data.get('positionName') or manager_data.get('position_name')
        )
        db.add(manager)


def _create_contract_management_config(db: Session, contract_id: int, management_data: Dict):
    """Create contract management config record."""
    from app.models.wathq_corporate_contract import ContractManagementConfig
    if not management_data:
        return
    
    config = ContractManagementConfig(
        contract_id=contract_id,
        structure_name=management_data.get('structureName') or management_data.get('structure_name'),
        meeting_quorum_name=management_data.get('meetingQuorumName') or management_data.get('meeting_quorum_name'),
        can_delegate_attendance=management_data.get('canDelegateAttendance') or management_data.get('can_delegate_attendance'),
        term_years=management_data.get('termYears') or management_data.get('term_years')
    )
    db.add(config)


def _create_contract_activities(db: Session, contract_id: int, activities: List[Dict]):
    """Create contract activity records."""
    from app.models.wathq_corporate_contract import ContractActivity
    for activity_data in activities:
        activity = ContractActivity(
            contract_id=contract_id,
            activity_id=activity_data.get('activityId') or activity_data.get('activity_id'),
            activity_name=activity_data.get('activityName') or activity_data.get('activity_name')
        )
        db.add(activity)


def _create_contract_articles(db: Session, contract_id: int, articles: List[Dict]):
    """Create contract article records."""
    from app.models.wathq_corporate_contract import ContractArticle
    for article_data in articles:
        article = ContractArticle(
            contract_id=contract_id,
            original_id=article_data.get('originalId') or article_data.get('original_id'),
            article_text=article_data.get('articleText') or article_data.get('article_text'),
            part_name=article_data.get('partName') or article_data.get('part_name')
        )
        db.add(article)


def _create_contract_decisions(db: Session, contract_id: int, decisions: List[Dict]):
    """Create contract decision records."""
    from app.models.wathq_corporate_contract import ContractDecision
    for decision_data in decisions:
        decision = ContractDecision(
            contract_id=contract_id,
            decision_name=decision_data.get('decisionName') or decision_data.get('decision_name'),
            approve_percentage=decision_data.get('approvePercentage') or decision_data.get('approve_percentage')
        )
        db.add(decision)


def _create_notification_channels(db: Session, contract_id: int, channels: List[Dict]):
    """Create notification channel records."""
    from app.models.wathq_corporate_contract import NotificationChannel
    for channel_data in channels:
        channel = NotificationChannel(
            contract_id=contract_id,
            channel_name=channel_data.get('channelName') or channel_data.get('channel_name')
        )
        db.add(channel)
