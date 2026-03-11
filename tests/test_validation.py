"""Validation and error case tests using AAA pattern."""
from fastapi.testclient import TestClient
from src.app import app


class TestSignupValidation:
    def test_signup_duplicate_email_rejected(self):
        # Arrange
        client = TestClient(app)
        email = "tester@mergington.edu"
        activity = "Gym Class"

        # Act 1: First signup succeeds
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200

        # Act 2: Second signup with same email
        response2 = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_invalid_activity_not_found(self):
        # Arrange
        client = TestClient(app)
        email = "student@mergington.edu"
        invalid_activity = "Nonexistent Club"

        # Act
        response = client.post(f"/activities/{invalid_activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "activity not found" in response.json()["detail"].lower()


class TestUnregisterValidation:
    def test_unregister_invalid_activity_not_found(self):
        # Arrange
        client = TestClient(app)
        email = "student@mergington.edu"
        invalid_activity = "Fake Activity"

        # Act
        response = client.delete(f"/activities/{invalid_activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        assert "activity not found" in response.json()["detail"].lower()

    def test_unregister_not_registered_student(self):
        # Arrange
        client = TestClient(app)
        email = "notregistered@mergington.edu"
        activity = "Tennis Club"

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()


class TestParticipantCountAccuracy:
    def test_participant_count_matches_list_length(self):
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, details in activities.items():
            participants_list = details["participants"]
            max_participants = details["max_participants"]

            # Verify count doesn't exceed maximum
            assert len(participants_list) <= max_participants, \
                f"{activity_name} has {len(participants_list)} participants but max is {max_participants}"

            # Verify no duplicates in participant list
            assert len(participants_list) == len(set(participants_list)), \
                f"{activity_name} has duplicate participants"
