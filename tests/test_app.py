from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activity_data():
    original_data = deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_data)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_keys = set(app_module.activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert set(response.json().keys()) == expected_activity_keys


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "taylor@mergington.edu"
    initial_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert len(app_module.activities[activity_name]["participants"]) == initial_count + 1
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert app_module.activities[activity_name]["participants"].count(existing_email) == 1


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    removed_email = "daniel@mergington.edu"
    assert removed_email in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={removed_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {removed_email} from {activity_name}"
    assert removed_email not in app_module.activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "nobody@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={missing_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_from_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
