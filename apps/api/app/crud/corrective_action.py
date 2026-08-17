from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.corrective_action import (
    CorrectiveAction,
    CorrectiveActionStatus,
)
from app.schemas.corrective_action import (
    CorrectiveActionCompleteRequest,
    CorrectiveActionCreate,
    CorrectiveActionUpdate,
    CorrectiveActionVerifyRequest,
)


def create_corrective_action(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    created_by_user_id: UUID,
    action_data: CorrectiveActionCreate,
) -> CorrectiveAction:
    action = CorrectiveAction(
        organization_id=organization_id,
        project_id=project_id,
        inspection_id=inspection_id,
        observation_id=action_data.observation_id,
        created_by_user_id=created_by_user_id,
        title=action_data.title,
        description=action_data.description,
        priority=action_data.priority.value,
        assigned_to_user_id=(action_data.assigned_to_user_id),
        due_date=action_data.due_date,
    )

    db.add(action)
    db.flush()

    return action


def get_corrective_action(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
    action_id: UUID,
) -> CorrectiveAction | None:
    statement = select(CorrectiveAction).where(
        CorrectiveAction.id == action_id,
        CorrectiveAction.organization_id == organization_id,
        CorrectiveAction.project_id == project_id,
    )

    return db.scalar(statement)


def list_corrective_actions(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
) -> list[CorrectiveAction]:
    statement = (
        select(CorrectiveAction)
        .where(
            CorrectiveAction.organization_id == organization_id,
            CorrectiveAction.project_id == project_id,
        )
        .order_by(
            CorrectiveAction.due_date.asc(),
            CorrectiveAction.created_at.asc(),
        )
    )

    return list(db.scalars(statement).all())


def update_corrective_action(
    db: Session,
    action: CorrectiveAction,
    action_data: CorrectiveActionUpdate,
) -> CorrectiveAction:
    updates = action_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        if hasattr(value, "value"):
            value = value.value

        setattr(
            action,
            field,
            value,
        )

    db.flush()

    return action


def start_corrective_action(
    db: Session,
    action: CorrectiveAction,
) -> CorrectiveAction:
    action.status = CorrectiveActionStatus.IN_PROGRESS.value

    db.flush()

    return action


def complete_corrective_action(
    db: Session,
    action: CorrectiveAction,
    completed_by_user_id: UUID,
    completion_data: CorrectiveActionCompleteRequest,
) -> CorrectiveAction:
    action.status = CorrectiveActionStatus.COMPLETED.value

    action.completion_notes = completion_data.completion_notes

    action.completed_by_user_id = completed_by_user_id

    action.completed_at = datetime.now(UTC)

    db.flush()

    return action


def verify_corrective_action(
    db: Session,
    action: CorrectiveAction,
    verified_by_user_id: UUID,
    verification_data: CorrectiveActionVerifyRequest,
) -> CorrectiveAction:
    action.status = CorrectiveActionStatus.VERIFIED.value

    action.verification_notes = verification_data.verification_notes

    action.verified_by_user_id = verified_by_user_id

    action.verified_at = datetime.now(UTC)

    db.flush()

    return action
