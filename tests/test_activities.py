"""Tests for the activities endpoints."""

import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we have all 9 activities
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_returns_activity_details(self, client):
        """Test that activity details are correctly returned."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_returns_participants(self, client):
        """Test that participants list is correctly returned."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_existing_activity_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_updates_participants_list(self, client):
        """Test that signup actually adds the student to the participants list."""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_registered_student_returns_400(self, client):
        """Test that signing up a student already registered returns 400."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_students(self, client):
        """Test signing up multiple different students."""
        client.post("/activities/Chess Club/signup?email=student1@mergington.edu")
        client.post("/activities/Chess Club/signup?email=student2@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]
        
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 4

    def test_signup_same_student_to_different_activities(self, client):
        """Test that a student can sign up for multiple activities."""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        client.post("/activities/Programming Class/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
        assert "newstudent@mergington.edu" in data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant_success(self, client):
        """Test successful unregistration of a participant."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the student from participants list."""
        client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 1

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_non_participant_returns_400(self, client):
        """Test that unregistering a non-participant returns 400."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=nonexistent@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_all_participants(self, client):
        """Test removing all participants from an activity."""
        client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        client.delete("/activities/Chess Club/unregister?email=daniel@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 0

    def test_signup_then_unregister(self, client):
        """Test signing up then unregistering the same student."""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        client.delete("/activities/Chess Club/unregister?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        
        assert "newstudent@mergington.edu" not in data["Chess Club"]["participants"]

    def test_signup_again_after_unregister(self, client):
        """Test that a student can sign up again after being unregistered."""
        # First signup
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert "newstudent@mergington.edu" in client.get("/activities").json()["Chess Club"]["participants"]
        
        # Unregister
        client.delete("/activities/Chess Club/unregister?email=newstudent@mergington.edu")
        assert "newstudent@mergington.edu" not in client.get("/activities").json()["Chess Club"]["participants"]
        
        # Sign up again
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in client.get("/activities").json()["Chess Club"]["participants"]
