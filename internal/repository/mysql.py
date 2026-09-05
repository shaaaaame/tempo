import dotenv
from sqlmodel import create_engine, Session, select
from typing import Annotated, Sequence
from fastapi import Depends
from internal.repository.models import Memberships
from internal.repository.errors import NotFoundException

DB_PASSWORD = dotenv.get_key(".env", "DB_PASSWORD")
CA_CERT_PATH = dotenv.get_key(".env", "CA_CERT_PATH")
DB_USER = dotenv.get_key(".env", "DB_USER")

mysql_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@gateway01.us-east-1.prod.aws.tidbcloud.com:4000/tempo?ssl_ca={CA_CERT_PATH}&ssl_verify_cert=true&ssl_verify_identity=true"

engine = create_engine(mysql_url)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def db_get_memberships(
    session: SessionDep,
    offset: int = 0,
    limit: int = 20,
) -> Sequence[Memberships]:
    memberships = session.exec(select(Memberships).offset(offset).limit(limit)).all()
    return memberships


def db_get_membership_by_id(
    session: SessionDep,
    membership_id: str,
) -> Memberships | None:
    membership = session.exec(
        select(Memberships).where(Memberships.id == membership_id)
    ).first()
    return membership


def db_create_membership(
    session: SessionDep,
    membership_data: dict,
) -> Memberships:
    membership = Memberships.model_validate(membership_data)
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def db_update_membership(
    session: SessionDep,
    membership_id: str,
    membership_data: dict,
) -> Memberships:
    membership = session.get(Memberships, membership_id)
    if not membership:
        raise NotFoundException

    membership.sqlmodel_update(membership_data)
    session.add(membership)
    session.commit()
    session.refresh(membership)

    return membership


def db_delete_membership(session: SessionDep, membership_id: str) -> bool:
    membership = session.get(Memberships, membership_id)
    if not membership:
        return True

    try:
        session.delete(membership)
        session.commit()
    except Exception as e:
        return False

    return True
