import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.follow_up_email_service import (
    get_eligible_warm_intro_requests,
    send_automated_follow_up_email,
    generate_automated_follow_up_content,
    send_email_via_sendgrid,
    process_automated_follow_ups,
    record_user_response
)
from app.models.warm_intro_request import WarmIntroStatus


class TestGetEligibleWarmIntroRequests:
    """Test the function that identifies warm intro requests eligible for follow-up emails."""
    
    @pytest.mark.asyncio
    async def test_get_eligible_requests_returns_old_pending_requests(self):
        """Test that only requests older than 14 days with pending status and no follow-up sent are returned."""
        # Mock database
        mock_db = MagicMock()
        
        # Mock eligible requests (older than 14 days, pending, no follow-up sent)
        eligible_requests = [
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "requester_name": "John Doe",
                "connection_name": "Jane Smith",
                "status": WarmIntroStatus.pending.value,
                "created_at": datetime.utcnow() - timedelta(days=15),
                "follow_up_sent_date": None
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = eligible_requests
        mock_db.warm_intro_requests.find.return_value = mock_cursor
        
        result = await get_eligible_warm_intro_requests(mock_db)
        
        # Verify the correct query was made
        expected_cutoff = datetime.utcnow() - timedelta(days=14)
        mock_db.warm_intro_requests.find.assert_called_once()
        call_args = mock_db.warm_intro_requests.find.call_args[0][0]
        
        assert "created_at" in call_args
        assert "follow_up_sent_date" in call_args
        assert "status" in call_args
        assert call_args["follow_up_sent_date"] is None
        assert call_args["status"] == WarmIntroStatus.pending.value
        
        assert result == eligible_requests
    
    @pytest.mark.asyncio
    async def test_get_eligible_requests_excludes_recent_requests(self):
        """Test that requests newer than 14 days are not returned."""
        mock_db = MagicMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = []
        mock_db.warm_intro_requests.find.return_value = mock_cursor
        
        result = await get_eligible_warm_intro_requests(mock_db)
        
        # Should query for requests older than 14 days
        call_args = mock_db.warm_intro_requests.find.call_args[0][0]
        assert "$lte" in call_args["created_at"]
        assert result == []


class TestSendAutomatedFollowUpEmail:
    """Test the function that sends automated follow-up emails."""
    
    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Test successful email sending and database update."""
        mock_db = MagicMock()
        
        # Mock user lookup
        user_data = {"id": str(uuid4()), "email": "user@example.com"}
        mock_db.users.find_one.return_value = user_data
        
        # Mock warm intro request
        request_id = str(uuid4())
        warm_intro_request = {
            "id": request_id,
            "user_id": user_data["id"],
            "requester_name": "John Doe",
            "connection_name": "Jane Smith"
        }
        
        # Mock successful email sending
        with patch('app.services.follow_up_email_service.send_email_via_sendgrid', return_value=True):
            # Mock database update
            mock_db.warm_intro_requests.update_one.return_value = MagicMock()
            
            result = await send_automated_follow_up_email(mock_db, warm_intro_request)
            
            assert result is True
            
            # Verify user lookup
            mock_db.users.find_one.assert_called_once_with({"id": user_data["id"]})
            
            # Verify database update
            mock_db.warm_intro_requests.update_one.assert_called_once()
            update_call = mock_db.warm_intro_requests.update_one.call_args
            assert update_call[0][0] == {"id": request_id}
            assert "follow_up_sent_date" in update_call[0][1]["$set"]
            assert "updated_at" in update_call[0][1]["$set"]
    
    @pytest.mark.asyncio
    async def test_send_email_user_not_found(self):
        """Test handling when user is not found."""
        mock_db = MagicMock()
        mock_db.users.find_one.return_value = None
        
        warm_intro_request = {
            "id": str(uuid4()),
            "user_id": str(uuid4()),
            "requester_name": "John Doe",
            "connection_name": "Jane Smith"
        }
        
        result = await send_automated_follow_up_email(mock_db, warm_intro_request)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_email_failure(self):
        """Test handling when email sending fails."""
        mock_db = MagicMock()
        
        user_data = {"id": str(uuid4()), "email": "user@example.com"}
        mock_db.users.find_one.return_value = user_data
        
        warm_intro_request = {
            "id": str(uuid4()),
            "user_id": user_data["id"],
            "requester_name": "John Doe",
            "connection_name": "Jane Smith"
        }
        
        # Mock failed email sending
        with patch('app.services.follow_up_email_service.send_email_via_sendgrid', return_value=False):
            result = await send_automated_follow_up_email(mock_db, warm_intro_request)
            
            assert result is False
            
            # Verify database was not updated
            mock_db.warm_intro_requests.update_one.assert_not_called()


class TestGenerateAutomatedFollowUpContent:
    """Test the email content generation function."""
    
    def test_generate_content_includes_required_elements(self):
        """Test that generated email content includes all required elements."""
        requester_name = "John Doe"
        connection_name = "Jane Smith"
        request_id = str(uuid4())
        
        with patch('app.services.follow_up_email_service.settings') as mock_settings:
            mock_settings.FRONTEND_URL = "http://localhost:3000"
            
            content = generate_automated_follow_up_content(requester_name, connection_name, request_id)
            
            # Check that content includes required elements
            assert connection_name in content
            assert "Yes, we connected" in content
            assert "No, not yet" in content
            assert "donation" in content.lower()
            assert request_id in content
            assert "http://localhost:3000" in content
    
    def test_generate_content_creates_correct_links(self):
        """Test that the correct response and donation links are generated."""
        request_id = str(uuid4())
        
        with patch('app.services.follow_up_email_service.settings') as mock_settings:
            mock_settings.FRONTEND_URL = "http://localhost:3000"
            
            content = generate_automated_follow_up_content("John", "Jane", request_id)
            
            expected_yes_link = f"http://localhost:3000/warm-intro-response?request_id={request_id}&response=yes"
            expected_no_link = f"http://localhost:3000/warm-intro-response?request_id={request_id}&response=no"
            expected_donate_link = "http://localhost:3000/donate"
            
            assert expected_yes_link in content
            assert expected_no_link in content
            assert expected_donate_link in content


class TestSendEmailViaSendgrid:
    """Test the SendGrid email sending function."""
    
    @pytest.mark.asyncio
    async def test_send_email_no_api_key_falls_back_to_simulation(self):
        """Test that when no API key is configured, it falls back to simulation."""
        with patch('app.services.follow_up_email_service.settings') as mock_settings:
            mock_settings.SENDGRID_API_KEY = ""
            
            with patch('app.services.follow_up_email_service.simulate_email_send', return_value=True) as mock_simulate:
                result = await send_email_via_sendgrid("test@example.com", "Test Subject", "<html>Test</html>")
                
                assert result is True
                mock_simulate.assert_called_once_with("test@example.com", "Test Subject", "<html>Test</html>")
    
    @pytest.mark.asyncio
    async def test_send_email_with_sendgrid_success(self):
        """Test successful email sending with SendGrid."""
        with patch('app.services.follow_up_email_service.settings') as mock_settings:
            mock_settings.SENDGRID_API_KEY = "test_api_key"
            mock_settings.FROM_EMAIL = "noreply@test.com"
            mock_settings.FROM_NAME = "Test Service"
            
            with patch('app.services.follow_up_email_service.sendgrid.SendGridAPIClient') as mock_sg_client:
                mock_response = MagicMock()
                mock_response.status_code = 202
                mock_sg_client.return_value.client.mail.send.post.return_value = mock_response
                
                result = await send_email_via_sendgrid("test@example.com", "Test Subject", "<html>Test</html>")
                
                assert result is True
    
    @pytest.mark.asyncio
    async def test_send_email_with_sendgrid_failure(self):
        """Test failed email sending with SendGrid."""
        with patch('app.services.follow_up_email_service.settings') as mock_settings:
            mock_settings.SENDGRID_API_KEY = "test_api_key"
            mock_settings.FROM_EMAIL = "noreply@test.com"
            mock_settings.FROM_NAME = "Test Service"
            
            with patch('app.services.follow_up_email_service.sendgrid.SendGridAPIClient') as mock_sg_client:
                mock_response = MagicMock()
                mock_response.status_code = 400
                mock_sg_client.return_value.client.mail.send.post.return_value = mock_response
                
                result = await send_email_via_sendgrid("test@example.com", "Test Subject", "<html>Test</html>")
                
                assert result is False


class TestProcessAutomatedFollowUps:
    """Test the main processing function."""
    
    @pytest.mark.asyncio
    async def test_process_multiple_requests(self):
        """Test processing multiple eligible requests."""
        with patch('app.services.follow_up_email_service.get_database') as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            # Mock eligible requests
            eligible_requests = [
                {"id": str(uuid4()), "requester_name": "John", "connection_name": "Jane"},
                {"id": str(uuid4()), "requester_name": "Bob", "connection_name": "Alice"}
            ]
            
            with patch('app.services.follow_up_email_service.get_eligible_warm_intro_requests', return_value=eligible_requests):
                with patch('app.services.follow_up_email_service.send_automated_follow_up_email', return_value=True) as mock_send:
                    result = await process_automated_follow_ups()
                    
                    assert result == 2
                    assert mock_send.call_count == 2
    
    @pytest.mark.asyncio
    async def test_process_handles_partial_failures(self):
        """Test that processing continues even if some emails fail."""
        with patch('app.services.follow_up_email_service.get_database') as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            eligible_requests = [
                {"id": str(uuid4())},
                {"id": str(uuid4())},
                {"id": str(uuid4())}
            ]
            
            with patch('app.services.follow_up_email_service.get_eligible_warm_intro_requests', return_value=eligible_requests):
                # Mock mixed success/failure
                with patch('app.services.follow_up_email_service.send_automated_follow_up_email', side_effect=[True, False, True]):
                    result = await process_automated_follow_ups()
                    
                    assert result == 2  # Only 2 successful sends


class TestRecordUserResponse:
    """Test the user response recording function."""
    
    @pytest.mark.asyncio
    async def test_record_connected_response(self):
        """Test recording a 'connected' response."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_db.warm_intro_requests.update_one.return_value = mock_result
        
        request_id = str(uuid4())
        result = await record_user_response(mock_db, request_id, True)
        
        assert result is True
        
        # Verify the update call
        update_call = mock_db.warm_intro_requests.update_one.call_args
        assert update_call[0][0] == {"id": request_id}
        update_data = update_call[0][1]["$set"]
        
        assert update_data["user_responded"] is True
        assert update_data["status"] == WarmIntroStatus.connected.value
        assert "response_date" in update_data
        assert "updated_at" in update_data
        assert "connected_date" in update_data
    
    @pytest.mark.asyncio
    async def test_record_not_connected_response(self):
        """Test recording a 'not connected' response."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_db.warm_intro_requests.update_one.return_value = mock_result
        
        request_id = str(uuid4())
        result = await record_user_response(mock_db, request_id, False)
        
        assert result is True
        
        # Verify the update call
        update_call = mock_db.warm_intro_requests.update_one.call_args
        update_data = update_call[0][1]["$set"]
        
        assert update_data["user_responded"] is True
        assert "status" not in update_data  # Status should not be updated for 'not connected'
        assert "connected_date" not in update_data
    
    @pytest.mark.asyncio
    async def test_record_response_request_not_found(self):
        """Test handling when the request is not found."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.modified_count = 0
        mock_db.warm_intro_requests.update_one.return_value = mock_result
        
        result = await record_user_response(mock_db, str(uuid4()), True)
        
        assert result is False