from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)


def create_project(
    db: Session,
    organization_id: UUID,
    created_by_user_id: UUID,
    project_data: ProjectCreate,
) -> Project:
    project = Project(
        organization_id=organization_id,
        created_by_user_id=created_by_user_id,
        name=project_data.name,
        code=project_data.code,
        project_type=project_data.project_type.value,
        location=project_data.location,
        description=project_data.description,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
    )

    db.add(project)
    db.flush()

    return project


def get_project(
    db: Session,
    organization_id: UUID,
    project_id: UUID,
) -> Project | None:
    statement = select(Project).where(
        Project.id == project_id,
        Project.organization_id == organization_id,
    )

    return db.scalar(statement)


def list_projects(
    db: Session,
    organization_id: UUID,
) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.organization_id == organization_id)
        .order_by(Project.created_at.desc())
    )

    return list(db.scalars(statement).all())


def update_project(
    db: Session,
    project: Project,
    project_data: ProjectUpdate,
) -> Project:
    updates = project_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(
            project,
            field,
            value,
        )

    db.flush()

    return project
