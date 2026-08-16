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
from app.crud.inspection import get_inspection
from app.crud.observation import (
    create_observation,
    get_observation,
    list_observations,
    update_observation,
)
from app.models.inspection import (
    Inspection,
    InspectionStatus,
)
from app.models.observation import (
    ObservationKind,
    ObservationSeverity,
)
from app.schemas.observation import (
    ObservationCreate,
    ObservationResponse,
    ObservationUpdate,
)

router = APIRouter(
    prefix=(
        "/organizations/{organization_id}"
        "/projects/{project_id}"
        "/inspections/{inspection_id}"
        "/observations"
    ),
    tags=["safety observations"],
)


def get_existing_inspection(
    db: DatabaseSession,
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
) -> Inspection:
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

    return inspection


def require_draft_inspection(
    db: DatabaseSession,
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
) -> Inspection:
    inspection = get_existing_inspection(
        db,
        organization_id,
        project_id,
        inspection_id,
    )

    if inspection.status == InspectionStatus.SUBMITTED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Submitted inspections cannot be modified."),
        )

    return inspection


@router.post(
    "",
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a safety observation",
)
def create_observation_endpoint(
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    observation_data: ObservationCreate,
    _writer: ProjectWriteMembership,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ObservationResponse:
    require_draft_inspection(
        db,
        organization_id,
        project_id,
        inspection_id,
    )

    observation = create_observation(
        db=db,
        organization_id=organization_id,
        project_id=project_id,
        inspection_id=inspection_id,
        created_by_user_id=current_user.id,
        observation_data=observation_data,
    )

    db.commit()
    db.refresh(observation)

    return ObservationResponse.model_validate(observation)


@router.get(
    "",
    response_model=list[ObservationResponse],
    summary="List inspection observations",
)
def list_observations_endpoint(
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    _membership: CurrentOrganizationMembership,
    db: DatabaseSession,
) -> list[ObservationResponse]:
    get_existing_inspection(
        db,
        organization_id,
        project_id,
        inspection_id,
    )

    observations = list_observations(
        db,
        organization_id,
        project_id,
        inspection_id,
    )

    return [ObservationResponse.model_validate(observation) for observation in observations]


@router.get(
    "/{observation_id}",
    response_model=ObservationResponse,
    summary="Get a safety observation",
)
def get_observation_endpoint(
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    observation_id: UUID,
    _membership: CurrentOrganizationMembership,
    db: DatabaseSession,
) -> ObservationResponse:
    observation = get_observation(
        db,
        organization_id,
        project_id,
        inspection_id,
        observation_id,
    )

    if observation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Safety observation not found.",
        )

    return ObservationResponse.model_validate(observation)


@router.patch(
    "/{observation_id}",
    response_model=ObservationResponse,
    summary="Update a safety observation",
)
def update_observation_endpoint(
    organization_id: UUID,
    project_id: UUID,
    inspection_id: UUID,
    observation_id: UUID,
    observation_data: ObservationUpdate,
    _writer: ProjectWriteMembership,
    db: DatabaseSession,
) -> ObservationResponse:
    require_draft_inspection(
        db,
        organization_id,
        project_id,
        inspection_id,
    )

    observation = get_observation(
        db,
        organization_id,
        project_id,
        inspection_id,
        observation_id,
    )

    if observation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Safety observation not found.",
        )

    proposed_severity = (
        observation_data.severity
        if "severity" in observation_data.model_fields_set
        else observation.severity
    )

    proposed_requires_action = (
        observation_data.requires_corrective_action
        if ("requires_corrective_action" in observation_data.model_fields_set)
        else observation.requires_corrective_action
    )

    if observation.kind == ObservationKind.SAFE_PRACTICE.value:
        if proposed_severity is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=("Safe practices cannot have a hazard severity."),
            )

        if proposed_requires_action:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=("Safe practices cannot require corrective action."),
            )

    elif proposed_severity is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("Unsafe observations require a severity."),
        )

    if proposed_severity in {
        ObservationSeverity.HIGH,
        ObservationSeverity.CRITICAL,
        ObservationSeverity.HIGH.value,
        ObservationSeverity.CRITICAL.value,
    }:
        observation_data.requires_corrective_action = True

    observation = update_observation(
        db,
        observation,
        observation_data,
    )

    db.commit()
    db.refresh(observation)

    return ObservationResponse.model_validate(observation)
