from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.observation import (
    ObservationSeverity,
    SafetyObservation,
)
from app.schemas.observation import (
    ObservationCreate,
    ObservationUpdate,
)


def create_observation(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    created_by_user_id: UUID,
    observation_data: ObservationCreate,
) -> SafetyObservation:
    severity = observation_data.severity.value if observation_data.severity is not None else None

    requires_corrective_action = (
        observation_data.requires_corrective_action
        or observation_data.severity
        in {
            ObservationSeverity.HIGH,
            ObservationSeverity.CRITICAL,
        }
    )

    observation = SafetyObservation(
        organization_id=organization_id,
        project_id=project_id,
        inspection_id=inspection_id,
        created_by_user_id=created_by_user_id,
        kind=observation_data.kind.value,
        category=observation_data.category.value,
        severity=severity,
        location=observation_data.location,
        description=observation_data.description,
        immediate_action_taken=(observation_data.immediate_action_taken),
        requires_corrective_action=(requires_corrective_action),
    )

    db.add(observation)
    db.flush()

    return observation


def get_observation(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    observation_id: UUID,
) -> SafetyObservation | None:
    statement = select(SafetyObservation).where(
        SafetyObservation.id == observation_id,
        SafetyObservation.organization_id == organization_id,
        SafetyObservation.project_id == project_id,
        SafetyObservation.inspection_id == inspection_id,
    )

    return db.scalar(statement)


def list_observations(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
) -> list[SafetyObservation]:
    statement = (
        select(SafetyObservation)
        .where(
            SafetyObservation.organization_id == organization_id,
            SafetyObservation.project_id == project_id,
            SafetyObservation.inspection_id == inspection_id,
        )
        .order_by(SafetyObservation.created_at.asc())
    )

    return list(db.scalars(statement).all())


def update_observation(
    db: Session,
    observation: SafetyObservation,
    observation_data: ObservationUpdate,
) -> SafetyObservation:
    updates = observation_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        if hasattr(value, "value"):
            value = value.value

        setattr(
            observation,
            field,
            value,
        )

    db.flush()

    return observation
