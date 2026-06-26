from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    for activity_name in expected_activities:
        assert activity_name in data
        assert isinstance(data[activity_name]["participants"], list)


def test_signup_adds_participant():
    # Arrange
    test_email = "pytest-chess@example.com"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={test_email}"
    )
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert test_email in data["message"]

    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert test_email in activities_data[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    test_email = "pytest-duplicate@example.com"
    activity_name = "Programming Class"
    client.post(f"/activities/{activity_name}/signup?email={test_email}")

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={test_email}"
    )
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Student is already signed up for this activity"


def test_remove_participant_unregisters_participant():
    # Arrange
    test_email = "pytest-remove@example.com"
    activity_name = "Gym Class"
    client.post(f"/activities/{activity_name}/signup?email={test_email}")

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={test_email}"
    )
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert test_email in data["message"]

    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert test_email not in activities_data[activity_name]["participants"]


def test_invalid_activity_returns_404():
    # Arrange
    test_email = "pytest-invalid@example.com"
    activity_name = "Nonexistent Activity"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={test_email}"
    )
    delete_response = client.delete(
        f"/activities/{activity_name}/participants?email={test_email}"
    )

    # Assert
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Activity not found"
