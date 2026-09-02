import dotenv
from sqlmodel import create_engine, Session, select
from typing import Annotated
from fastapi import Depends
from internal.repository.models import Memberships

DB_PASSWORD = dotenv.get_key(".env", "DB_PASSWORD")
CA_CERT_PATH = dotenv.get_key(".env", "CA_CERT_PATH")
DB_USER = dotenv.get_key(".env", "DB_USER")

mysql_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@gateway01.us-east-1.prod.aws.tidbcloud.com:4000/tempo?ssl_ca={CA_CERT_PATH}&ssl_verify_cert=true&ssl_verify_identity=true"

engine = create_engine(mysql_url)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def list_memberships(
    session: SessionDep,
    offset: int = 0,
    limit: int = 20,
):
    memberships = session.exec(select(Memberships).offset(offset).limit(limit)).all()
    return memberships
