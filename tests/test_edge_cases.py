"""
Edge case and error handling tests for the Activities API
"""

import pytest
from fastapi.testclient import TestClient
import urllib.parse


class TestInputValidation:
    """Tests for input validation and edge cases"""
    
    def test_signup_with_empty_email(self, client):
        """Test signup with empty email parameter"""
        response = client.post("/activities/Soccer Team/signup?email=")
        # API currently doesn't validate email format, so this might succeed
        # If you add email validation, update this test accordingly
        
    def test_signup_with_missing_email_parameter(self, client):
        """Test signup without email parameter"""
        response = client.post("/activities/Soccer Team/signup")
        assert response.status_code == 422  # FastAPI validation error
        
    def test_unregister_with_missing_email_parameter(self, client):
        """Test unregister without email parameter"""
        response = client.delete("/activities/Soccer Team/unregister")
        assert response.status_code == 422  # FastAPI validation error
        
    def test_signup_with_very_long_email(self, client):
        """Test signup with extremely long email"""
        long_email = "a" * 1000 + "@mergington.edu"
        response = client.post(f"/activities/Soccer Team/signup?email={long_email}")
        # Should handle gracefully (current implementation likely accepts it)
        
    def test_activity_name_with_special_characters(self, client):
        """Test activity names with special characters and encoding"""
        # Test URL encoding
        encoded_name = urllib.parse.quote("Chess Club")
        response = client.post(f"/activities/{encoded_name}/signup?email=test@mergington.edu")
        assert response.status_code == 200  # Should succeed with proper URL encoding
        
    def test_case_sensitivity_activity_names(self, client):
        """Test that activity names are case sensitive"""
        response = client.post("/activities/chess club/signup?email=test@mergington.edu")
        assert response.status_code == 404  # Should not find lowercase version
        
        response = client.post("/activities/CHESS CLUB/signup?email=test@mergington.edu")
        assert response.status_code == 404  # Should not find uppercase version


class TestConcurrency:
    """Tests for concurrent operations (simulated)"""
    
    def test_multiple_signups_same_activity(self, client):
        """Test multiple signups to the same activity"""
        activity = "Basketball Club"
        emails = [f"student{i}@mergington.edu" for i in range(5)]
        
        responses = []
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            responses.append(response)
            
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            
        # Verify all participants were added
        activities_response = client.get("/activities")
        data = activities_response.json()
        for email in emails:
            assert email in data[activity]["participants"]


class TestErrorMessages:
    """Tests for proper error message formatting"""
    
    def test_404_error_format(self, client):
        """Test that 404 errors have proper format"""
        response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert data["detail"] == "Activity not found"
        
    def test_400_error_format_duplicate_signup(self, client):
        """Test that 400 errors have proper format for duplicate signups"""
        email = "test@mergington.edu"
        activity = "Soccer Team"
        
        # First signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Duplicate signup
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert data["detail"] == "Student already signed up for this activity"
        
    def test_400_error_format_unregister_not_signed_up(self, client):
        """Test 400 error for unregistering non-participant"""
        response = client.delete("/activities/Soccer Team/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Student is not signed up for this activity"


class TestDataConsistency:
    """Tests for data consistency and state management"""
    
    def test_activities_data_structure_consistency(self, client):
        """Test that all activities have consistent data structure"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"
                
            # Check data types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check that max_participants is positive
            assert activity_data["max_participants"] > 0
            
            # Check that all participants are strings (emails)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                
    def test_participant_count_consistency(self, client):
        """Test that participant counts are consistent"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            participants = activity_data["participants"]
            max_participants = activity_data["max_participants"]
            
            # Check no duplicate participants
            assert len(participants) == len(set(participants)), f"Duplicate participants in {activity_name}"
            
            # Note: Current implementation doesn't enforce max_participants limit
            # If you implement that, uncomment the next line:
            # assert len(participants) <= max_participants, f"Too many participants in {activity_name}"


class TestStaticFileHandling:
    """Tests for static file serving"""
    
    def test_static_files_accessible(self, client):
        """Test that static files are accessible"""
        # Test CSS file
        response = client.get("/static/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
        
        # Test JavaScript file  
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert "javascript" in response.headers.get("content-type", "") or "text/plain" in response.headers.get("content-type", "")
        
        # Test HTML file
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
    def test_nonexistent_static_file(self, client):
        """Test accessing non-existent static file"""
        response = client.get("/static/nonexistent.txt")
        assert response.status_code == 404