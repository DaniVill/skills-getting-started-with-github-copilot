"""
Test suite for Mergington High School API

Tests are structured using the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and fixtures
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from app import activities


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_all_activities_returns_200(self, client):
        """
        Arrange: Client is ready
        Act: Send GET request to /activities
        Assert: Response status is 200 OK
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200

    def test_get_all_activities_returns_correct_structure(self, client):
        """
        Arrange: Client is ready
        Act: Send GET request to /activities
        Assert: Response contains all activities with correct fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert data["Chess Club"]["max_participants"] == 12

    def test_get_all_activities_includes_participants(self, client):
        """
        Arrange: Client is ready
        Act: Send GET request to /activities
        Assert: Response includes current participant list
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "participants" in data["Chess Club"]
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 2


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_returns_200(self, client):
        """
        Arrange: Client ready, user not yet signed up
        Act: Send POST request to signup for activity
        Assert: Response status is 200 OK
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200

    def test_signup_successful_adds_participant(self, client):
        """
        Arrange: Client ready, Chess Club has 2 participants
        Act: Send POST request to add new participant
        Assert: Participant list for Chess Club increases by 1
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]

    def test_signup_returns_correct_message(self, client):
        """
        Arrange: Client ready, user not signed up
        Act: Send POST request to signup
        Assert: Response message confirms signup
        """
        # Arrange
        activity_name = "Programming Class"
        email = "alex@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        data = response.json()
        
        # Assert
        assert data["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Client ready, activity does not exist
        Act: Send POST request for non-existent activity
        Assert: Response status is 404 Not Found
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_signed_up_returns_400(self, client):
        """
        Arrange: Client ready, user already signed up for Chess Club
        Act: Send POST request to signup for same activity
        Assert: Response status is 400 Bad Request
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_multiple_different_activities_succeeds(self, client):
        """
        Arrange: Client ready, user not signed up for any activity
        Act: Send POST requests to signup for multiple activities
        Assert: Student is added to all requested activities
        """
        # Arrange
        email = "versatile@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        for activity_name in activities_to_join:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            
            # Assert
            assert response.status_code == 200
            assert email in activities[activity_name]["participants"]


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_participant_successful_returns_200(self, client):
        """
        Arrange: Client ready, participant exists in activity
        Act: Send DELETE request to remove participant
        Assert: Response status is 200 OK
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 200

    def test_remove_participant_removes_from_list(self, client):
        """
        Arrange: Client ready, Chess Club has michael@mergington.edu
        Act: Send DELETE request to remove michael
        Assert: michael@mergington.edu is no longer in participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_participant_returns_correct_message(self, client):
        """
        Arrange: Client ready, participant exists
        Act: Send DELETE request
        Assert: Response message confirms removal
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        data = response.json()
        
        # Assert
        assert data["message"] == f"Removed {email} from {activity_name}"

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Client ready, activity does not exist
        Act: Send DELETE request for non-existent activity
        Assert: Response status is 404 Not Found
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_remove_nonexistent_participant_returns_400(self, client):
        """
        Arrange: Client ready, participant not in activity
        Act: Send DELETE request for non-existent participant
        Assert: Response status is 400 Bad Request
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notaparticipant@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Participant not found"

    def test_remove_participant_then_can_rejoin(self, client):
        """
        Arrange: Client ready, participant exists in activity
        Act: Remove participant, then signup again
        Assert: Participant can rejoin after removal
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: Remove participant
        client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert: Participant is removed
        assert email not in activities[activity_name]["participants"]
        
        # Act: Signup again
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert: Can rejoin successfully
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
