import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.models.warm_intro_request import WarmIntroStatus


class TestFollowUpEmailE2E:
    """End-to-end tests for the automated follow-up email feature."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self):
        """
        Test the complete user journey:
        1. User makes a warm intro request
        2. Two weeks pass
        3. System sends follow-up email
        4. User clicks link in email
        5. User response is recorded
        6. User is shown donation option
        """
        
        # Step 1: Simulate a warm intro request being created 15 days ago
        request_id = str(uuid4())
        user_id = str(uuid4())
        
        warm_intro_request = {
            "id": request_id,
            "user_id": user_id,
            "requester_name": "John Doe",
            "connection_name": "Jane Smith",
            "status": WarmIntroStatus.pending.value,
            "created_at": datetime.utcnow() - timedelta(days=15),
            "follow_up_sent_date": None,
            "user_responded": None,
            "response_date": None,
            "connected_date": None,
            "declined_date": None
        }
        
        user_data = {
            "id": user_id,
            "email": "john.doe@example.com"
        }
        
        mock_db = MagicMock()
        
        with patch('app.services.follow_up_email_service.get_database') as mock_get_db:
            mock_get_db.return_value = mock_db
            
            # Step 2: Mock the scheduler finding eligible requests
            mock_cursor = AsyncMock()
            mock_cursor.to_list.return_value = [warm_intro_request]
            mock_db.warm_intro_requests.find.return_value = mock_cursor
            mock_db.users.find_one.return_value = user_data
            
            # Step 3: Mock successful email sending
            with patch('app.services.follow_up_email_service.send_email_via_sendgrid') as mock_send_email:
                mock_send_email.return_value = True
                
                # Mock database update for follow-up sent
                mock_db.warm_intro_requests.update_one.return_value = MagicMock()
                
                # Process automated follow-ups (simulates scheduler running)
                from app.services.follow_up_email_service import process_automated_follow_ups
                sent_count = await process_automated_follow_ups()
                
                assert sent_count == 1
                
                # Verify email was "sent"
                mock_send_email.assert_called_once()
                email_call = mock_send_email.call_args
                assert email_call[1]["to_email"] == "john.doe@example.com"
                assert "Following up on your introduction request" in email_call[1]["subject"]
                
                # Verify email content contains required elements
                email_content = email_call[1]["html_content"]
                assert "Jane Smith" in email_content  # Connection name
                assert "Yes, we connected" in email_content
                assert "No, not yet" in email_content
                assert "donation" in email_content.lower()
                assert request_id in email_content
        
        # Step 4: Simulate user clicking "Yes, we connected" link
        with patch('app.core.db.get_database') as mock_get_db:
            mock_get_db.return_value = mock_db
            
            # Mock successful response recording
            mock_result = MagicMock()
            mock_result.modified_count = 1
            mock_db.warm_intro_requests.update_one.return_value = mock_result
            
            # User clicks "Yes" link (simulates frontend calling API)
            response = self.client.post(
                f"/warm-intro-requests/{request_id}/respond",
                json={"connected": True}
            )
            
            # Step 5: Verify response is recorded correctly
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "Thank you for your response!"
            assert response_data["connected"] is True
            
            # Verify database update for user response
            mock_db.warm_intro_requests.update_one.assert_called()
            update_call = mock_db.warm_intro_requests.update_one.call_args
            update_data = update_call[0][1]["$set"]
            
            assert update_data["user_responded"] is True
            assert update_data["status"] == WarmIntroStatus.connected.value
            assert "response_date" in update_data
            assert "connected_date" in update_data
    
    @pytest.mark.asyncio
    async def test_user_journey_not_connected(self):
        """Test the user journey when they respond 'No, not yet'."""
        
        request_id = str(uuid4())
        user_id = str(uuid4())
        
        # Simulate the follow-up email being sent (skip to user response)
        mock_db = MagicMock()
        
        with patch('app.core.db.get_database') as mock_get_db:
            mock_get_db.return_value = mock_db
            
            mock_result = MagicMock()
            mock_result.modified_count = 1
            mock_db.warm_intro_requests.update_one.return_value = mock_result
            
            # User clicks "No, not yet" link
            response = self.client.post(
                f"/warm-intro-requests/{request_id}/respond",
                json={"connected": False}
            )
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["connected"] is False
            
            # Verify database update - status should remain pending
            update_call = mock_db.warm_intro_requests.update_one.call_args
            update_data = update_call[0][1]["$set"]
            
            assert update_data["user_responded"] is True
            assert "status" not in update_data  # Status should not change
            assert "connected_date" not in update_data
    
    def test_email_link_generation_and_frontend_integration(self):
        """Test that email links are generated correctly and work with frontend."""
        
        request_id = str(uuid4())
        
        # Test email content generation
        from app.services.follow_up_email_service import generate_automated_follow_up_content
        
        with patch('app.services.follow_up_email_service.settings') as mock_settings:
            mock_settings.FRONTEND_URL = "http://localhost:3000"
            
            content = generate_automated_follow_up_content("John Doe", "Jane Smith", request_id)
            
            # Extract the generated donation link
            expected_donate_link = "http://localhost:3000/donate"
            
            assert expected_yes_link in content
            assert expected_no_link in content
            assert expected_donate_link in content
            
            # Test that these links would work with the frontend
            # (The frontend would parse the query parameters and make API calls)
            
            # Simulate what frontend would do for "yes" response
            mock_db = MagicMock()
            with patch('app.core.db.get_database') as mock_get_db:
                mock_get_db.return_value = mock_db
                mock_result = MagicMock()
                mock_result.modified_count = 1
                mock_db.warm_intro_requests.update_one.return_value = mock_result
                
                # This simulates the frontend parsing the URL and making the API call
                api_response = self.client.post(
                    f"/warm-intro-requests/{request_id}/respond",
                    json={"connected": True}
                )
                
                assert api_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_scheduler_daily_processing(self):
        """Test that the scheduler processes follow-ups correctly on a daily basis."""
        
        # Create multiple requests at different stages
        requests = [
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "requester_name": "User 1",
                "connection_name": "Connection 1",
                "status": WarmIntroStatus.pending.value,
                "created_at": datetime.utcnow() - timedelta(days=15),  # Eligible
                "follow_up_sent_date": None
            },
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "requester_name": "User 2",
                "connection_name": "Connection 2",
                "status": WarmIntroStatus.pending.value,
                "created_at": datetime.utcnow() - timedelta(days=20),  # Eligible
                "follow_up_sent_date": None
            },
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "requester_name": "User 3",
                "connection_name": "Connection 3",
                "status": WarmIntroStatus.pending.value,
                "created_at": datetime.utcnow() - timedelta(days=10),  # Not eligible (too recent)
                "follow_up_sent_date": None
            },
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "requester_name": "User 4",
                "connection_name": "Connection 4",
                "status": WarmIntroStatus.pending.value,
                "created_at": datetime.utcnow() - timedelta(days=16),  # Not eligible (already sent)
                "follow_up_sent_date": datetime.utcnow() - timedelta(days=1)
            }
        ]
        
        mock_db = MagicMock()
        
        with patch('app.services.follow_up_email_service.get_database') as mock_get_db:
            mock_get_db.return_value = mock_db
            
            # Mock the query to return only eligible requests (first 2)
            eligible_requests = [req for req in requests if req["follow_up_sent_date"] is None and 
                               req["created_at"] <= datetime.utcnow() - timedelta(days=14)]
            
            mock_cursor = AsyncMock()
            mock_cursor.to_list.return_value = eligible_requests
            mock_db.warm_intro_requests.find.return_value = mock_cursor
            
            # Mock user lookups
            mock_db.users.find_one.return_value = {"id": "user_id", "email": "user@example.com"}
            
            # Mock successful email sending
            with patch('app.services.follow_up_email_service.send_email_via_sendgrid', return_value=True):
                mock_db.warm_intro_requests.update_one.return_value = MagicMock()
                
                # Process automated follow-ups
                from app.services.follow_up_email_service import process_automated_follow_ups
                sent_count = await process_automated_follow_ups()
                
                # Should only process the 2 eligible requests
                assert sent_count == 2
                
                # Verify database updates were called for each eligible request
                assert mock_db.warm_intro_requests.update_one.call_count == 2
    
    def test_error_scenarios_e2e(self):
        """Test various error scenarios in the end-to-end flow."""
        
        # Test 1: Invalid request ID
        response = self.client.post(
            "/warm-intro-requests/invalid-id/respond",
            json={"connected": True}
        )
        # Should handle gracefully
        assert response.status_code in [400, 404, 422, 500]
        
        # Test 2: Missing request body
        response = self.client.post(f"/warm-intro-requests/{str(uuid4())}/respond")
        assert response.status_code == 422
        
        # Test 3: Invalid request body
        response = self.client.post(
            f"/warm-intro-requests/{str(uuid4())}/respond",
            json={"invalid_field": True}
        )
        assert response.status_code == 422
        
        # Test 4: Request not found in database
        request_id = str(uuid4())
        mock_db = MagicMock()
        
        with patch('app.core.db.get_database') as mock_get_db:
            mock_get_db.return_value = mock_db
            
            # Mock no database update (request not found)
            mock_result = MagicMock()
            mock_result.modified_count = 0
            mock_db.warm_intro_requests.update_one.return_value = mock_result
            
            response = self.client.post(
                f"/warm-intro-requests/{request_id}/respond",
                json={"connected": True}
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_email_delivery_and_content_validation(self):
        """Test that emails are properly formatted and contain all required elements."""
        
        request_id = str(uuid4())
        user_id = str(uuid4())
        
        warm_intro_request = {
            "id": request_id,
            "user_id": user_id,
            "requester_name": "John Doe",
            "connection_name": "Jane Smith",
            "status": WarmIntroStatus.pending.value,
            "created_at": datetime.utcnow() - timedelta(days=15),
            "follow_up_sent_date": None
        }
        
        user_data = {"id": user_id, "email": "john.doe@example.com"}
        mock_db = MagicMock()
        
        with patch('app.services.follow_up_email_service.get_database') as mock_get_db:
            mock_get_db.return_value = mock_db
            
            mock_cursor = AsyncMock()
            mock_cursor.to_list.return_value = [warm_intro_request]
            mock_db.warm_intro_requests.find.return_value = mock_cursor
            mock_db.users.find_one.return_value = user_data
            
            with patch('app.services.follow_up_email_service.send_email_via_sendgrid') as mock_send_email:
                mock_send_email.return_value = True
                mock_db.warm_intro_requests.update_one.return_value = MagicMock()
                
                from app.services.follow_up_email_service import process_automated_follow_ups
                await process_automated_follow_ups()
                
                # Verify email was sent with correct parameters
                mock_send_email.assert_called_once()
                call_args = mock_send_email.call_args
                
                # Check email parameters
                assert call_args[1]["to_email"] == "john.doe@example.com"
                assert "Following up on your introduction request" in call_args[1]["subject"]
                
                # Check email content
                content = call_args[1]["html_content"]
                
                # Required content elements
                assert "Jane Smith" in content  # Connection name
                assert "Yes, we connected" in content
                assert "No, not yet" in content
                assert "donation" in content.lower()
                assert "Superconnector" in content
                
                # Required links
                assert f"request_id={request_id}" in content
                assert "response=yes" in content
                assert "response=no" in content
                assert "/donate" in content
                
                # HTML structure
                assert "<html>" in content
                assert "</html>" in content
                assert "style=" in content  # Should have inline styles
    
    def test_donation_flow_integration(self):
        """Test that the donation flow is properly integrated."""
        
        # This would typically test the donation page accessibility
        # Since we created a simple donation page, we can test that it loads
        
        # Note: In a real E2E test, you might use Selenium or Playwright
        # to test the actual frontend pages, but for this example,
        # we'll just verify the donation link is correctly generated
        
        from app.services.follow_up_email_service import generate_automated_follow_up_content
        
        with patch('app.services.follow_up_email_service.settings') as mock_settings:
            mock_settings.FRONTEND_URL = "http://localhost:3000"
            
            content = generate_automated_follow_up_content("John", "Jane", str(uuid4()))
            
            # Verify donation link is present and correctly formatted
            assert "http://localhost:3000/donate" in content
            assert "donation" in content.lower()
            assert "support" in content.lower()