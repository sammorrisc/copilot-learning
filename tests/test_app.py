from fastapi.testclient import TestClient
import copy
import pytest

from app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Save and restore activities to keep tests isolated
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_delete():
    activity = "Chess Club"
    email = "testuser@example.com"

    # ensure not present
    assert email not in activities[activity]["participants"]

    # sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # delete
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_duplicate():
    activity = "Programming Class"
    email = "dup@example.com"

    resp1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp1.status_code == 200

    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400


def test_delete_nonexistent():
    activity = "Tennis Club"
    email = "notfound@example.com"

    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 404


def test_activity_not_found():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "x@example.com"})
    assert resp.status_code == 404

    resp = client.delete("/activities/NoSuchActivity/participants", params={"email": "x@example.com"})
    assert resp.status_code == 404
