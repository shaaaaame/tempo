from fastapi import FastAPI

from internal.services.memberships.v1.memberships import membership_router

app = FastAPI()

app.include_router(membership_router)
