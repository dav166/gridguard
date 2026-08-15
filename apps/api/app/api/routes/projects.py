from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import (
    CurrentOrganizationMembership,
    CurrentUser,
    DatabaseSession,
    ProjectWriteMembership,
)
from app.crud.project import (
    create_project,
    get_project,
    list_projects,
    update_project,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/projects",
    tags=["projects"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
def create_project_endpoint(
    organization_id: UUID,
    project_data: ProjectCreate,
    _writer: ProjectWriteMembership,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ProjectResponse:
    try:
        project = create_project(
            db=db,
            organization_id=organization_id,
            created_by_user_id=current_user.id,
            project_data=project_data,
        )

        db.commit()
        db.refresh(project)

    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("A project with this code already exists in this organization."),
        ) from error

    return ProjectResponse.model_validate(project)


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List organization projects",
)
def list_projects_endpoint(
    organization_id: UUID,
    _membership: CurrentOrganizationMembership,
    db: DatabaseSession,
) -> list[ProjectResponse]:
    projects = list_projects(
        db,
        organization_id,
    )

    return [ProjectResponse.model_validate(project) for project in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project",
)
def get_project_endpoint(
    organization_id: UUID,
    project_id: UUID,
    _membership: CurrentOrganizationMembership,
    db: DatabaseSession,
) -> ProjectResponse:
    project = get_project(
        db,
        organization_id,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return ProjectResponse.model_validate(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
)
def update_project_endpoint(
    organization_id: UUID,
    project_id: UUID,
    project_data: ProjectUpdate,
    _writer: ProjectWriteMembership,
    db: DatabaseSession,
) -> ProjectResponse:
    project = get_project(
        db,
        organization_id,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    proposed_start_date = (
        project_data.start_date
        if "start_date" in project_data.model_fields_set
        else project.start_date
    )

    proposed_end_date = (
        project_data.end_date if "end_date" in project_data.model_fields_set else project.end_date
    )

    if (
        proposed_start_date is not None
        and proposed_end_date is not None
        and proposed_end_date < proposed_start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("end_date must be on or after start_date."),
        )

    try:
        project = update_project(
            db,
            project,
            project_data,
        )

        db.commit()
        db.refresh(project)

    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("A project with this code already exists in this organization."),
        ) from error

    return ProjectResponse.model_validate(project)
