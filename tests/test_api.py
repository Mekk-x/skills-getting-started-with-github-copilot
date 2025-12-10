import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_root_redirects_to_static_index():
    resp = client.get("/")
    assert resp.status_code in (200, 307, 302)


def test_get_activities_returns_data():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Ensure clean state if email already present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    resp_signup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp_signup.status_code == 200
    assert email in activities[activity]["participants"]

    # Duplicate sign up should fail
    resp_dup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp_dup.status_code == 400
    assert resp_dup.json()["detail"] == "Student already signed up for this activity"

    # Unregister
    resp_del = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp_del.status_code == 200
    assert email not in activities[activity]["participants"]

    # Unregister non-existent should 404
    resp_del_missing = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp_del_missing.status_code == 404
    assert resp_del_missing.json()["detail"] == "Student not registered for this activity"
