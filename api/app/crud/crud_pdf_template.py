"""
CRUD operations for PDF Template models with GrapesJS integration.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.pdf_template import (
    GeneratedPdf,
    PdfTemplate,
    PdfTemplateVersion,
)
from app.schemas.pdf_template import (
    GeneratedPdfCreate,
    PdfTemplateCreate,
    PdfTemplateUpdate,
)


class CRUDPdfTemplate(
    CRUDBase[PdfTemplate, PdfTemplateCreate, PdfTemplateUpdate]
):
    """CRUD operations for PDF templates."""

    def get(self, db: Session, id: UUID) -> Optional[PdfTemplate]:
        """Get template by UUID."""
        return db.query(PdfTemplate).filter(PdfTemplate.id == id).first()

    def get_by_slug(
        self, db: Session, *, slug: str
    ) -> Optional[PdfTemplate]:
        """Get template by slug."""
        return db.query(PdfTemplate).filter(
            PdfTemplate.slug == slug
        ).first()

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_public: Optional[bool] = None,
        tenant_id: Optional[int] = None,
        created_by: Optional[int] = None,
        search: Optional[str] = None,
    ) -> tuple[List[PdfTemplate], int]:
        """Get multiple templates with filters and pagination."""
        query = db.query(PdfTemplate)

        # Apply filters
        if category:
            query = query.filter(PdfTemplate.category == category)
        if is_active is not None:
            query = query.filter(PdfTemplate.is_active == is_active)
        if is_public is not None:
            query = query.filter(PdfTemplate.is_public == is_public)
        if tenant_id is not None:
            query = query.filter(
                or_(
                    PdfTemplate.tenant_id == tenant_id,
                    PdfTemplate.is_public.is_(True),
                )
            )
        if created_by:
            query = query.filter(PdfTemplate.created_by == created_by)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    PdfTemplate.name.ilike(search_pattern),
                    PdfTemplate.description.ilike(search_pattern),
                    PdfTemplate.slug.ilike(search_pattern),
                )
            )

        # Get total count
        total = query.count()

        # Get paginated results
        templates = (
            query.order_by(desc(PdfTemplate.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return templates, total

    def create_with_creator(
        self, db: Session, *, obj_in: PdfTemplateCreate, creator_id: int
    ) -> PdfTemplate:
        """Create template with creator."""
        obj_in_data = obj_in.model_dump()
        obj_in_data["created_by"] = creator_id
        db_obj = PdfTemplate(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Create initial version
        self._create_version(
            db,
            template=db_obj,
            version_number=1,
            version_name="Initial version",
            creator_id=creator_id,
        )

        return db_obj

    def update_template(
        self,
        db: Session,
        *,
        db_obj: PdfTemplate,
        obj_in: PdfTemplateUpdate,
        creator_id: int,
        create_version: bool = True,
    ) -> PdfTemplate:
        """Update template and optionally create version."""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Track if content changed
        content_changed = any(
            key in update_data
            for key in [
                "grapesjs_data",
                "grapesjs_html",
                "grapesjs_css",
                "data_mapping",
            ]
        )

        # Update template
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Create version if content changed and requested
        if create_version and content_changed:
            latest_version = (
                db.query(PdfTemplateVersion)
                .filter(PdfTemplateVersion.template_id == db_obj.id)
                .order_by(desc(PdfTemplateVersion.version_number))
                .first()
            )
            next_version = (
                latest_version.version_number + 1
                if latest_version
                else 1
            )
            self._create_version(
                db,
                template=db_obj,
                version_number=next_version,
                creator_id=creator_id,
            )

        return db_obj

    def _create_version(
        self,
        db: Session,
        *,
        template: PdfTemplate,
        version_number: int,
        creator_id: int,
        version_name: Optional[str] = None,
        change_description: Optional[str] = None,
    ) -> PdfTemplateVersion:
        """Create a new version of the template."""
        version = PdfTemplateVersion(
            template_id=template.id,
            version_number=version_number,
            version_name=version_name,
            grapesjs_data=template.grapesjs_data,
            grapesjs_html=template.grapesjs_html,
            grapesjs_css=template.grapesjs_css,
            data_mapping=template.data_mapping,
            change_description=change_description,
            created_by=creator_id,
        )
        db.add(version)
        db.commit()
        db.refresh(version)
        return version

    def increment_usage(
        self, db: Session, *, template_id: UUID
    ) -> Optional[PdfTemplate]:
        """Increment usage count for template."""
        template = self.get(db, id=template_id)
        if template:
            template.usage_count += 1
            template.last_used_at = func.now()
            db.commit()
            db.refresh(template)
        return template

    def duplicate(
        self,
        db: Session,
        *,
        template_id: UUID,
        new_name: str,
        new_slug: str,
        creator_id: int,
        include_versions: bool = False,
    ) -> Optional[PdfTemplate]:
        """Duplicate an existing template."""
        original = self.get(db, id=template_id)
        if not original:
            return None

        # Create new template
        duplicate = PdfTemplate(
            name=new_name,
            slug=new_slug,
            description=f"Copy of {original.name}",
            grapesjs_data=original.grapesjs_data,
            grapesjs_html=original.grapesjs_html,
            grapesjs_css=original.grapesjs_css,
            category=original.category,
            thumbnail=original.thumbnail,
            data_mapping=original.data_mapping,
            sample_data=original.sample_data,
            is_active=original.is_active,
            is_public=False,
            page_size=original.page_size,
            page_orientation=original.page_orientation,
            created_by=creator_id,
            tenant_id=original.tenant_id,
        )
        db.add(duplicate)
        db.commit()
        db.refresh(duplicate)

        # Duplicate versions if requested
        if include_versions:
            versions = (
                db.query(PdfTemplateVersion)
                .filter(
                    PdfTemplateVersion.template_id == template_id
                )
                .order_by(PdfTemplateVersion.version_number)
                .all()
            )
            for version in versions:
                new_version = PdfTemplateVersion(
                    template_id=duplicate.id,
                    version_number=version.version_number,
                    version_name=version.version_name,
                    grapesjs_data=version.grapesjs_data,
                    grapesjs_html=version.grapesjs_html,
                    grapesjs_css=version.grapesjs_css,
                    data_mapping=version.data_mapping,
                    change_description=f"Duplicated from original",
                    created_by=creator_id,
                )
                db.add(new_version)
            db.commit()

        return duplicate

    def get_categories(self, db: Session) -> List[str]:
        """Get all unique categories."""
        result = (
            db.query(PdfTemplate.category)
            .distinct()
            .filter(PdfTemplate.is_active.is_(True))
            .all()
        )
        return [cat[0] for cat in result if cat[0]]


class CRUDPdfTemplateVersion(CRUDBase):
    """CRUD operations for PDF template versions."""

    def get(
        self, db: Session, id: UUID
    ) -> Optional[PdfTemplateVersion]:
        """Get version by UUID."""
        return (
            db.query(PdfTemplateVersion)
            .filter(PdfTemplateVersion.id == id)
            .first()
        )

    def get_by_template(
        self, db: Session, *, template_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[List[PdfTemplateVersion], int]:
        """Get versions for a template."""
        query = db.query(PdfTemplateVersion).filter(
            PdfTemplateVersion.template_id == template_id
        )

        total = query.count()

        versions = (
            query.order_by(desc(PdfTemplateVersion.version_number))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return versions, total

    def get_version_by_number(
        self, db: Session, *, template_id: UUID, version_number: int
    ) -> Optional[PdfTemplateVersion]:
        """Get specific version by number."""
        return (
            db.query(PdfTemplateVersion)
            .filter(
                and_(
                    PdfTemplateVersion.template_id == template_id,
                    PdfTemplateVersion.version_number == version_number,
                )
            )
            .first()
        )

    def get_latest_version(
        self, db: Session, *, template_id: UUID
    ) -> Optional[PdfTemplateVersion]:
        """Get latest version of template."""
        return (
            db.query(PdfTemplateVersion)
            .filter(PdfTemplateVersion.template_id == template_id)
            .order_by(desc(PdfTemplateVersion.version_number))
            .first()
        )


class CRUDGeneratedPdf(CRUDBase[GeneratedPdf, GeneratedPdfCreate, None]):
    """CRUD operations for generated PDFs."""

    def get(self, db: Session, id: UUID) -> Optional[GeneratedPdf]:
        """Get generated PDF by UUID."""
        return db.query(GeneratedPdf).filter(
            GeneratedPdf.id == id
        ).first()

    def get_multi_by_template(
        self,
        db: Session,
        *,
        template_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[GeneratedPdf], int]:
        """Get generated PDFs for a template."""
        query = db.query(GeneratedPdf).options(
            joinedload(GeneratedPdf.template)
        ).filter(
            GeneratedPdf.template_id == template_id
        )

        total = query.count()

        pdfs = (
            query.order_by(desc(GeneratedPdf.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return pdfs, total

    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[GeneratedPdf], int]:
        """Get generated PDFs by user."""
        query = db.query(GeneratedPdf).options(
            joinedload(GeneratedPdf.template)
        ).filter(
            GeneratedPdf.generated_by == user_id
        )

        total = query.count()

        pdfs = (
            query.order_by(desc(GeneratedPdf.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return pdfs, total

    def create_with_generator(
        self, db: Session, *, obj_in: GeneratedPdfCreate, generator_id: int
    ) -> GeneratedPdf:
        """Create generated PDF record."""
        obj_in_data = obj_in.model_dump()
        obj_in_data["generated_by"] = generator_id

        # Calculate expiration if not set
        if "expires_at" not in obj_in_data or obj_in_data["expires_at"] is None:
            obj_in_data["expires_at"] = datetime.utcnow() + timedelta(days=30)

        db_obj = GeneratedPdf(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_download(
        self, db: Session, *, pdf_id: UUID
    ) -> Optional[GeneratedPdf]:
        """Increment download count."""
        pdf = self.get(db, id=pdf_id)
        if pdf:
            pdf.download_count += 1
            pdf.last_accessed_at = func.now()
            db.commit()
            db.refresh(pdf)
        return pdf

    def cleanup_expired(self, db: Session) -> int:
        """Delete expired PDFs."""
        expired = (
            db.query(GeneratedPdf)
            .filter(
                and_(
                    GeneratedPdf.expires_at.isnot(None),
                    GeneratedPdf.expires_at < datetime.utcnow(),
                )
            )
            .all()
        )

        count = len(expired)
        for pdf in expired:
            db.delete(pdf)

        db.commit()
        return count


# Create singleton instances
pdf_template = CRUDPdfTemplate(PdfTemplate)
pdf_template_version = CRUDPdfTemplateVersion(PdfTemplateVersion)
generated_pdf = CRUDGeneratedPdf(GeneratedPdf)
