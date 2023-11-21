import pytest
from pony.orm import Database, db_session
from src.theThing.models.db import db


@pytest.fixture(scope="module", autouse=True)
def clear_db():
    if db.provider is None:
        db.bind(provider="sqlite", filename="test.db", create_db=True)
        db.generate_mapping(create_tables=True)
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    yield
    db.drop_all_tables(with_all_data=True)
    db.create_tables()


@pytest.fixture(scope="session")
def test_db():
    yield db
