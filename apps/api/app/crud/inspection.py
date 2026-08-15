from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inspection import (
    Inspection,
    InspectionStatus,
)
from app.schemas.inspection import (
    InspectionCreate,
    InspectionSubmitRequest,
    InspectionUpdate,
)


def create_inspection(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
    performed_by_user_id: UUID,
    inspection_data: InspectionCreate,
) -> Inspection:
    inspection = Inspection(
        organization_id=organization_id,
        project_id=project_id,
        performed_by_user_id=performed_by_user_id,
        title=inspection_data.title,
        inspection_type=inspection_data.inspection_type.value,
        inspection_date=inspection_data.inspection_date,
        notes=inspection_data.notes,
    )

    db.add(inspection)
    db.flush()

    return inspection


def get_inspection(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
) -> Inspection | None:
    statement = select(Inspection).where(
        Inspection.id == inspection_id,
        Inspection.organization_id == organization_id,
        Inspection.project_id == project_id,
    )

    return db.scalar(statement)


def list_inspections(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
) -> list[Inspection]:
    statement = (
        select(Inspection)
        .where(
            Inspection.organization_id == organization_id,
            Inspection.project_id == project_id,
        )
        .order_by(
            Inspection.inspection_date.desc(),
            Inspection.created_at.desc(),
        )
    )

    return list(db.scalars(statement).all())


def update_inspection(
    db: Session,
    inspection: Inspection,
    inspection_data: InspectionUpdate,
) -> Inspection:
    updates = inspection_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        if hasattr(value, "value"):
            value = value.value

        setattr(
            inspection,
            field,
            value,
        )

    db.flush()

    return inspection


def submit_inspection(
    db: Session,
    inspection: Inspection,
    submission_data: InspectionSubmitRequest,
) -> Inspection:
    inspection.result = submission_data.result.value

    if submission_data.notes is not None:
        inspection.notes = submission_data.notes

    inspection.status = InspectionStatus.SUBMITTED.value

    inspection.submitted_at = datetime.now(UTC)

    db.flush()

    return inspection
