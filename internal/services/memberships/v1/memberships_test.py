from fastapi import FastAPI
from fastapi.testclient import TestClient
from internal.repository.mysql import get_session, db_get_memberships, SessionDep
from internal.services.memberships.v1.memberships import membership_router
from internal.repository.models import Memberships
from sqlmodel import create_engine, SQLModel, Session
from sqlmodel.pool import StaticPool
import pytest
from datetime import datetime

app = FastAPI()
app.include_router(membership_router)

client = TestClient(app)

TEST_MEMBER_ID = "1234567890:1234"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_get_memberships_success(session: Session, client: TestClient):
    test_member = Memberships(
        id=TEST_MEMBER_ID,
        first_name="first name",
        last_name="last name",
        email="firstname@gmail.com",
        skill_level="white",
        type="full",
        end_date=datetime.now(),
    )
    session.add(test_member)
    session.commit()

    def mock_db_get_memberships(session: SessionDep, offset=0, limit=20):
        return []

    app.dependency_overrides[db_get_memberships] = mock_db_get_memberships
    client = TestClient(app)
    response = client.get("/v1/memberships")
    data = response.json()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert data[0]["id"] == TEST_MEMBER_ID


def test_get_memberships_offset_limit(session: Session, client: TestClient):
    test_members = [
        Memberships(
            id=str(i) * 10 + ":2627",
            first_name="first name",
            last_name="last name",
            email="firstname@gmail.com",
            skill_level="white",
            type="full",
            end_date=datetime.now(),
        )
        for i in range(10)
    ]
    session.add_all(test_members)
    session.commit()

    response = client.get("/v1/memberships", params={"offset": 1, "limit": 5})
    data = response.json()

    assert response.status_code == 200
    assert data[0]["id"] == "1111111111:2627"
    assert len(data) == 5


def test_get_membership_by_id_success(session: Session, client: TestClient):
    test_member = Memberships(
        id=TEST_MEMBER_ID,
        first_name="first name",
        last_name="last name",
        email="firstname@gmail.com",
        skill_level="white",
        type="full",
        end_date=datetime.now(),
    )
    session.add(test_member)
    session.commit()

    response = client.get(f"/v1/memberships/{TEST_MEMBER_ID}")
    data = response.json()

    assert response.status_code == 200
    assert data["first_name"] == "first name"
    assert data["last_name"] == "last name"
    assert data["email"] == "firstname@gmail.com"
    assert data["skill_level"] == "white"
    assert data["type"] == "full"


def test_get_membership_by_id_not_found(client: TestClient):
    response = client.get(f"/v1/memberships/{TEST_MEMBER_ID}")

    assert response.status_code == 404
