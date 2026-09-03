from fastapi import APIRouter, status, HTTPException
from internal.repository.mysql import (
    SessionDep,
    db_get_memberships,
    db_create_membership,
    db_get_membership_by_id,
    db_update_membership,
)
from internal.services.memberships.v1.schemas import (
    UpdateMembershipRequest,
    CreateMembershipRequest,
)
from internal.repository.errors import ErrNotFound

membership_router = APIRouter(prefix="/v1")


@membership_router.get("/memberships", tags=["memberships"])
async def get_memberships(
    session: SessionDep,
    offset: int = 0,
    limit: int = 20,
):
    memberships = db_get_memberships(session=session, offset=offset, limit=limit)
    return memberships


@membership_router.get("/memberships/{membership_id}", tags=["memberships"])
async def get_membership_by_id(
    membership_id: str,
    session: SessionDep,
):
    membership = db_get_membership_by_id(session=session, membership_id=membership_id)
    if not membership:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Membership not found")
    return membership


@membership_router.post("/memberships", tags=["memberships"])
async def post_membership(
    session: SessionDep,
    create_membership_request: CreateMembershipRequest,
):
    membership_data = create_membership_request.model_dump()
    membership = db_create_membership(session=session, membership_data=membership_data)
    return membership


@membership_router.patch("/memberships/{membership_id}", tags=["memberships"])
async def update_membership(
    session: SessionDep,
    membership_id: str,
    update_membership_request: UpdateMembershipRequest,
):
    membership_data = update_membership_request.model_dump(exclude_unset=True)

    try:
        membership = db_update_membership(session, membership_id, membership_data)
    except ErrNotFound:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"member with id: {membership_id} not found."
        )
    except Exception as _:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "an unknown error has occurred."
        )

    return membership
