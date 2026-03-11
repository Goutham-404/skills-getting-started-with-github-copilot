"""Happy path tests for all FastAPI endpoints using AAA pattern."""
from fastapi.testclient import TestClient
from src.app import app


class TestGetActivities:
    def test_get_activities_returns_all_activities(self):
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities


class TestGetActivitiesStructure:
    def test_activity_has_required_fields(self):
        # Arrange
        client = TestClient(app)
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, details in activities.items():
            assert all(field in details for field in required_fields), \
                f"Activity '{activity_name}' missing required fields"
            assert isinstance(details["participants"], list)


class TestRootRedirect:
    def test_root_redirects_to_index(self):
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignup:
    def test_signup_success(self):
        # Arrange
        client = TestClient(app)
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            follow_redirects=False
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]

    def test_signup_then_unregister_then_signup_again(self):
        # Arrange
        client = TestClient(app)
        email = "flexible@mergington.edu"
        activity = "Programming Class"

        # Act 1: Initial signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200

        # Act 2: Unregister
        response2 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response2.status_code == 200

        # Act 3: Signup again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response3.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]


class TestUnregister:
    def test_unregister_success(self):
        # Arrange
        client = TestClient(app)
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"

        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

        # Verify participant was removed
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity]["participants"])
        assert final_count == initial_count - 1
        assert email not in final_response.json()[activity]["participants"]
