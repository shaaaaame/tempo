from fastapi import APIRouter
from internal.repository.models import Memberships
from internal.repository.mysql import SessionDep, list_memberships

membership_router = APIRouter()


@membership_router.get("/memberships/", tags=["memberships"])
async def get_memberships(
    session: SessionDep,
    offset: int = 0,
    limit: int = 20,
):
    memberships = list_memberships(session=session, offset=offset, limit=limit)
    return memberships
