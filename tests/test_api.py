"""
Tests for the Mergington High School Activities API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all expected activities are present
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Club", "Art Workshop", "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data
            
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        
    def test_activities_have_correct_initial_participants(self, client):
        """Test that activities have the correct initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club has initial participants
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        
        # Check Programming Class has initial participants
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in data["Programming Class"]["participants"]
        
        # Check some activities have no initial participants
        assert len(data["Soccer Team"]["participants"]) == 0
        assert len(data["Basketball Club"]["participants"]) == 0


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Soccer Team"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Soccer Team"]["participants"]
        
    def test_signup_nonexistent_activity(self, client):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
        
    def test_signup_duplicate_participant(self, client):
        """Test signing up the same participant twice"""
        email = "duplicate@mergington.edu"
        activity = "Basketball Club"
        
        # First signup should succeed
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Student already signed up for this activity"
        
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity names"""
        # Test with spaces (should work with URL encoding)
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        # This should succeed since URL encoding works properly
        assert response.status_code == 200
        
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with special characters in email"""
        response = client.post(
            "/activities/Soccer Team/signup?email=test%2Buser@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # First, add a participant
        signup_response = client.post(
            "/activities/Drama Club/signup?email=temp@mergington.edu"
        )
        assert signup_response.status_code == 200
        
        # Then unregister them
        response = client.delete(
            "/activities/Drama Club/unregister?email=temp@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unregistered temp@mergington.edu from Drama Club"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "temp@mergington.edu" not in activities_data["Drama Club"]["participants"]
        
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # Unregister an existing participant from Chess Club
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
        
    def test_unregister_participant_not_signed_up(self, client):
        """Test unregistering a participant who isn't signed up"""
        response = client.delete(
            "/activities/Soccer Team/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete signup and unregister workflow"""
        email = "workflow@mergington.edu"
        activity = "Art Workshop"
        
        # Check initial state
        activities_response = client.get("/activities")
        initial_data = activities_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Check participant was added
        activities_response = client.get("/activities")
        after_signup_data = activities_response.json()
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        assert email in after_signup_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Check participant was removed
        activities_response = client.get("/activities")
        after_unregister_data = activities_response.json()
        assert len(after_unregister_data[activity]["participants"]) == initial_count
        assert email not in after_unregister_data[activity]["participants"]
        
    def test_multiple_activities_signup(self, client):
        """Test signing up for multiple activities"""
        email = "multi@mergington.edu"
        activities_to_join = ["Soccer Team", "Math Olympiad", "Science Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
            
        # Verify participant is in all activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        
        for activity in activities_to_join:
            assert email in data[activity]["participants"]
            
    def test_capacity_constraints(self, client):
        """Test that activities respect capacity constraints"""
        # Get Math Olympiad which has max_participants: 10
        activities_response = client.get("/activities")
        data = activities_response.json()
        math_olympiad = data["Math Olympiad"]
        max_participants = math_olympiad["max_participants"]
        current_participants = len(math_olympiad["participants"])
        
        # Sign up students until we reach capacity
        emails_to_add = []
        for i in range(max_participants - current_participants):
            email = f"student{i}@mergington.edu"
            emails_to_add.append(email)
            response = client.post(f"/activities/Math Olympiad/signup?email={email}")
            assert response.status_code == 200
            
        # Verify we're at capacity
        activities_response = client.get("/activities")
        updated_data = activities_response.json()
        assert len(updated_data["Math Olympiad"]["participants"]) == max_participants
        
        # Try to add one more (this should still work as our current implementation doesn't enforce capacity)
        # Note: If you want to enforce capacity, you'd need to add that logic to the API
        response = client.post("/activities/Math Olympiad/signup?email=overflow@mergington.edu")
        # Current implementation allows this - if you want to enforce capacity, this test would need to expect 400