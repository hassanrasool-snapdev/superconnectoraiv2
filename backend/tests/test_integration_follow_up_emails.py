import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.models.warm_intro_request import WarmIntroStatus
from app.services.follow_up_email_service import process_automated_follow_ups


class TestFollowUpEmailIntegration:
    """Integration tests for the automated follow-up email system."""
    
    def setup_method(self):
        """Set up test client and mock database."""
        self.client = TestClient(app)
        self.mock_db = MagicMock()
    
    @pytest.mark.asyncio
    async def test_end_to_end_follow_up_process(self):
        """Test the complete follow-up email process from scheduling to user response."""
        
        # Step 1: Create a warm intro request (simulate this being older than 14 days)
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
            "response_date": None
        }
        
        user_data = {
            "id": user_id,
            "email": "john.doe@example.com"
        }
        
        with patch('app.services.follow_up_email_service.get_database') as mock_get_db:
            mock_get_db.return_value = self.mock_db
            
            # Mock database queries
            mock_cursor = AsyncMock()
            mock_cursor.to_list.return_value = [warm_intro_request]
            self.mock_db.warm_intro_requests.find.return_value = mock_cursor
            self.mock_db.users.find_one.return_value = user_data
            
            # Mock successful email sending
            with patch('app.services.follow_up_email_service.send_email_via_sendgrid', return_value=True):
                # Mock database update
                self.mock_db.warm_intro_requests.update_one.return_value = MagicMock()
                
                # Step 2: Process automated follow-ups
                sent_count = await process_automated_follow_ups()
                
                assert sent_count == 1
                
                # Verify database was updated with follow-up sent date
                self.mock_db.warm_intro_requests.update_one.assert_called()
                update_call = self.mock_db.warm_intro_requests.update_one.call_args
                assert update_call[0][0] == {"id": request_id}
                assert "follow_up_sent_date" in update_call[0][1]["$set"]
    
    def test_api_endpoint_user_response_connected(self):
        """Test the API endpoint for recording user responses - connected case."""
        request_id = str(uuid4())
        
        with patch('app.core.db.get_database') as mock_get_db:
            mock_get_db.return_value = self.mock_db
            
            # Mock successful database update
            mock_result = MagicMock()
            mock_result.modified_count = 1
            self.mock_db.warm_intro_requests.update_one.return_value = mock_result
            
            # Make API call
            response = self.client.post(
                f"/warm-intro-requests/{request_id}/respond",
                json={"connected": True}
            )
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "Thank you for your response!"
            assert response_data["connected"] is True
            
            # Verify database update
            self.mock_db.warm_intro_requests.update_one.assert_called_once()
            update_call = self.mock_db.warm_intro_requests.update_one.call_args
            assert update_call[0][0] == {"id": request_id}
            
            update_data = update_call[0][1]["$set"]
            assert update_data["user_responded"] is True
            assert update_data["status"] == WarmIntroStatus.connected.value
            assert "response_date" in update_data
            assert "connected_date" in update_data
    
    def test_api_endpoint_user_response_not_connected(self):
        """Test the API endpoint for recording user responses - not connected case."""
        request_id = str(uuid4())
        
        with patch('app.core.db.get_database') as mock_get_db:
            mock_get_db.return_value = self.mock_db
            
            # Mock successful database update
            mock_result = MagicMock()
            mock_result.modified_count = 1
            self.mock_db.warm_intro_requests.update_one.return_value = mock_result
            
            # Make API call
            response = self.client.post(
                f"/warm-intro-requests/{request_id}/respond",
                json={"connected": False}
            )
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["connected"] is False
            
            # Verify database update
            update_call = self.mock_db.warm_intro_requests.update_one.call_args
            update_data = update_call[0][1]["$set"]
            assert update_data["user_responded"] is True
            assert "status" not in update_data  # Status should not change for 'not connected'
            assert "connected_date" not in update_data
    
    def test_api_endpoint_request_not_found(self):
        """Test API endpoint when the warm intro request is not found."""
        request_id = str(uuid4())
        
        with patch('app.core.db.get_database') as mock_get_db:
            mock_get_db.return_value = self.mock_db
            
            # Mock no database update (request not found)
            mock_result = MagicMock()
            mock_result.modified_count = 0
            self.mock_db.warm_intro_requests.update_one.return_value = mock_result
            
            # Make API call
            response = self.client.post(
                f"/warm-intro-requests/{request_id}/respond",
                json={"connected": True}
            )
            
            assert response.status_code == 404
            response_data = response.json()
            assert "not found" in response_data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_scheduler_integration(self):
        """Test that the scheduler correctly calls the automated follow-up processing."""
        
        with patch('app.services.follow_up_email_service.process_automated_follow_ups') as mock_process:
            mock_process.return_value = 2
            
            # Import and test the scheduler function
            from app.services.scheduler_service import SchedulerService
            
            scheduler = SchedulerService()
            
            # Test the automated follow-up processing method
            await scheduler._process_automated_follow_ups()
            
            mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_email_content_and_links_integration(self):
        """Test that email content generation creates proper links that work with the frontend."""
        from app.services.follow_up_email_service import generate_automated_follow_up_content
        
        request_id = str(uuid4())
        requester_name = "John Doe"
        connection_name = "Jane Smith"
        
        with patch('app.services.follow_up_email_service.settings') as mock_settings:
            mock_settings.FRONTEND_URL = "http://localhost:3000"
            
            content = generate_automated_follow_up_content(requester_name, connection_name, request_id)
            
            # Verify that the generated content includes donation link
            
            assert expected_yes_link in content
            assert expected_no_link in content
            
            # Test that these links would result in correct API calls
            # (This simulates what the frontend would do)
            
            # Test "yes" response
            with patch('app.core.db.get_database') as mock_get_db:
                mock_get_db.return_value = self.mock_db
                mock_result = MagicMock()
                mock_result.modified_count = 1
                self.mock_db.warm_intro_requests.update_one.return_value = mock_result
                
                response = self.client.post(
                    f"/warm-intro-requests/{request_id}/respond",
                    json={"connected": True}
                )
                
                assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_database_field_updates_integration(self):
        """Test that all new database fields are properly updated throughout the process."""
        
        request_id = str(uuid4())
        user_id = str(uuid4())
        
        # Test the complete flow of field updates
        warm_intro_request = {
            "id": request_id,
            "user_id": user_id,
            "requester_name": "John Doe",
            "connection_name": "Jane Smith",
            "status": WarmIntroStatus.pending.value,
            "created_at": datetime.utcnow() - timedelta(days=15),
            "follow_up_sent_date": None,
            "user_responded": None,
            "response_date": None
        }
        
        user_data = {"id": user_id, "email": "john@example.com"}
        
        with patch('app.services.follow_up_email_service.get_database') as mock_get_db:
            mock_get_db.return_value = self.mock_db
            
            # Step 1: Test follow-up email sending updates
            mock_cursor = AsyncMock()
            mock_cursor.to_list.return_value = [warm_intro_request]
            self.mock_db.warm_intro_requests.find.return_value = mock_cursor
            self.mock_db.users.find_one.return_value = user_data
            
            with patch('app.services.follow_up_email_service.send_email_via_sendgrid', return_value=True):
                self.mock_db.warm_intro_requests.update_one.return_value = MagicMock()
                
                sent_count = await process_automated_follow_ups()
                assert sent_count == 1
                
                # Verify follow-up sent fields were updated
                update_call = self.mock_db.warm_intro_requests.update_one.call_args
                update_data = update_call[0][1]["$set"]
                assert "follow_up_sent_date" in update_data
                assert "updated_at" in update_data
        
        # Step 2: Test user response updates
        with patch('app.core.db.get_database') as mock_get_db:
            mock_get_db.return_value = self.mock_db
            
            mock_result = MagicMock()
            mock_result.modified_count = 1
            self.mock_db.warm_intro_requests.update_one.return_value = mock_result
            
            # Test connected response
            response = self.client.post(
                f"/warm-intro-requests/{request_id}/respond",
                json={"connected": True}
            )
            
            assert response.status_code == 200
            
            # Verify user response fields were updated
            update_call = self.mock_db.warm_intro_requests.update_one.call_args
            update_data = update_call[0][1]["$set"]
            assert update_data["user_responded"] is True
            assert update_data["status"] == WarmIntroStatus.connected.value
            assert "response_date" in update_data
            assert "connected_date" in update_data
            assert "updated_at" in update_data
    
    def test_error_handling_integration(self):
        """Test error handling across the integrated system."""
        
        # Test API error handling
        request_id = "invalid-uuid"
        
        response = self.client.post(
            f"/warm-intro-requests/{request_id}/respond",
            json={"connected": True}
        )
        
        # Should handle gracefully (either 400 for invalid UUID or 404 for not found)
        assert response.status_code in [400, 404, 500]
        
        # Test with missing request body
        response = self.client.post(f"/warm-intro-requests/{str(uuid4())}/respond")
        assert response.status_code == 422  # Validation error
        
        # Test with invalid request body
        response = self.client.post(
            f"/warm-intro-requests/{str(uuid4())}/respond",
            json={"invalid_field": "value"}
        )
        assert response.status_code == 422  # Validation error