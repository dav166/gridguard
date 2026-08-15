from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.api.dependencies import (
    CurrentOrganizationMembership,
    CurrentUser,
    DatabaseSession,
    ProjectWriteMembership,
)
from app.crud.inspection import (
    create_inspection,
    get_inspection,
    list_inspections,
    submit_inspection,
    update_inspection,
)
from app.crud.project import get_project
from app.models.inspection import InspectionStatus
from app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
    InspectionSubmitRequest,
    InspectionUpdate,
)

router = APIRouter(
    prefix=("/organizations/{organization_id}/projects/{project_id}/inspections"),
    tags=["inspections"],
)


def ensure_project_exists(
    db: DatabaseSession,
    organization_id: UUID,
    project_id: UUID,
) -> None:
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


@router.post(
    "",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an inspection draft",
)
def create_inspection_endpoint(
    organization_id: UUID,
    project_id: UUID,
    inspection_data: InspectionCreate,
    _writer: ProjectWriteMembership,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> InspectionResponse:
    ensure_project_exists(
        db,
        organization_id,
        project_id,
    )

    inspection = create_inspection(
        db=db,
        organization_id=organization_id,
        project_id=project_id,
        performed_by_user_id=current_user.id,
        inspection_data=inspection_data,
    )

    db.commit()
    db.refresh(inspection)

    return InspectionResponse.model_validate(inspection)


@router.get(
    "",
    response_model=list[InspectionResponse],
    summary="List project inspections",
)
def list_inspections_endpoint(
    organization_id: UUID,
    project_id: UUID,
    _membership: CurrentOrganizationMembership,
    db: DatabaseSession,
) -> list[InspectionResponse]:
    ensure_project_exists(
        db,
        organization_id,
        project_id,
    )

    inspections = list_inspections(
        db,
        organization_id,
        project_id,
    )

    return [InspectionResponse.model_validate(inspection) for inspection in inspections]


@router.get(
    "/{inspection_id}",
    response_model=InspectionResponse,
    summary="Get an inspection",
)
def get_inspection_endpoint(
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    _membership: CurrentOrganizationMembership,
    db: DatabaseSession,
) -> InspectionResponse:
    inspection = get_inspection(
        db,
        organization_id,
        project_id,
        inspection_id,
    )

    if inspection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found.",
        )

    return InspectionResponse.model_validate(inspection)


@router.patch(
    "/{inspection_id}",
    response_model=InspectionResponse,
    summary="Update an inspection draft",
)
def update_inspection_endpoint(
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    inspection_data: InspectionUpdate,
    _writer: ProjectWriteMembership,
    db: DatabaseSession,
) -> InspectionResponse:
    inspection = get_inspection(
        db,
        organization_id,
        project_id,
        inspection_id,
    )

    if inspection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found.",
        )

    if inspection.status == InspectionStatus.SUBMITTED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Submitted inspections cannot be edited."),
        )

    inspection = update_inspection(
        db,
        inspection,
        inspection_data,
    )

    db.commit()
    db.refresh(inspection)

    return InspectionResponse.model_validate(inspection)


@router.post(
    "/{inspection_id}/submit",
    response_model=InspectionResponse,
    summary="Submit an inspection",
)
def submit_inspection_endpoint(
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    submission_data: InspectionSubmitRequest,
    _writer: ProjectWriteMembership,
    db: DatabaseSession,
) -> InspectionResponse:
    inspection = get_inspection(
        db,
        organization_id,
        project_id,
        inspection_id,
    )

    if inspection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found.",
        )

    if inspection.status == InspectionStatus.SUBMITTED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Inspection is already submitted.",
        )

    inspection = submit_inspection(
        db,
        inspection,
        submission_data,
    )

    db.commit()
    db.refresh(inspection)

    return InspectionResponse.model_validate(inspection)
