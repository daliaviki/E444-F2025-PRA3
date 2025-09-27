import json
from pathlib import Path
import pytest

from project.app import app, db

TEST_DB = "test.db"


@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def login(client, username, password):
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


def logout(client):
    return client.get("/logout", follow_redirects=True)


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_database_file_created(client):
    assert Path("test.db").is_file()


def test_empty_db_prompt(client):
    rv = client.get("/")
    assert b"No entries yet. Add some!" in rv.data


def test_login_logout_flow(client):
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"])
    assert b"You were logged in" in rv.data
    rv = logout(client)
    assert b"You were logged out" in rv.data
    rv = login(client, app.config["USERNAME"] + "x", app.config["PASSWORD"])
    assert b"Invalid username" in rv.data
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"] + "x")
    assert b"Invalid password" in rv.data


def test_messages_create_and_render(client):
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.post(
        "/add",
        data=dict(title="<Hello>", text="<strong>HTML</strong> allowed here"),
        follow_redirects=True,
    )
    assert b"&lt;Hello&gt;" in rv.data
    assert b"<strong>HTML</strong> allowed here" in rv.data
    assert b"No entries yet" not in rv.data


def test_delete_message(client):
    """Create a post, then delete it and expect status 1."""
    # If your app protects delete, this login also satisfies that.
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    client.post(
        "/add",
        data=dict(title="to delete", text="bye"),
        follow_redirects=True,
    )
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 1
