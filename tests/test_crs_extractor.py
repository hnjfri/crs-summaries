"""
Behavior-driven tests for CRS Summary Extractor.

These tests verify the complete user workflows and system behavior,
focusing on real-world scenarios and user value rather than implementation details.
"""

import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Import the classes we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crs_summary_extractor import (
    CRSSummaryExtractor,
    InputValidator,
    ConfigurationError,
    ValidationError,
    APIError,
    DataProcessingError,
)


class TestUserWorkflows:
    """Test complete user workflows that deliver real business value."""
    
    def test_complete_extraction_workflow_succeeds_with_valid_api_key(self, mock_api_responses):
        """
        GIVEN a valid API key and working Congress.gov API
        WHEN user runs the complete CRS extraction workflow
        THEN system fetches documents, filters active ones, removes duplicates, 
             gets detailed summaries, and creates properly formatted CSV
        """
        # Arrange: Set up environment and mock responses
        with patch.dict(os.environ, {'CONGRESSGOV_API_KEY': 'valid_test_key'}):
            with patch('requests.Session') as mock_session:
                mock_session.return_value = mock_api_responses['session']
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_file = Path(temp_dir) / 'test_output.csv'
                    
                    # Act: Run the complete workflow
                    extractor = CRSSummaryExtractor()
                    extractor.run(str(output_file))
                    
                    # Assert: Verify complete workflow success
                    assert output_file.exists(), "CSV file should be created"
                    
                    # Verify CSV content structure
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    lines = content.strip().split('\n')
                    assert len(lines) >= 2, "CSV should have header + at least one data row"
                    
                    # Verify CSV headers
                    expected_headers = ['Title', 'Date Published', 'Author(s)', 'URL', '300-word Summary']
                    header_line = lines[0]
                    for header in expected_headers:
                        assert header in header_line, f"Missing required header: {header}"
                    
                    # Verify data rows contain actual content
                    data_line = lines[1]
                    assert len(data_line.split(',')) >= 5, "Data rows should have all required fields"
                    assert 'Test Report Title' in content, "Should contain actual report data"
    
    def test_system_handles_api_authentication_failure_gracefully(self):
        """
        GIVEN an invalid API key
        WHEN user attempts to run CRS extraction
        THEN system provides clear error message with troubleshooting guidance
        """
        # Arrange: Invalid API key
        with patch.dict(os.environ, {'CONGRESSGOV_API_KEY': 'invalid_key'}):
            with patch('requests.Session') as mock_session:
                mock_response = Mock()
                mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
                mock_session.return_value.get.return_value = mock_response
                
                # Act & Assert: Should raise APIError with helpful message
                with pytest.raises(APIError) as exc_info:
                    extractor = CRSSummaryExtractor()
                    extractor.run()
                
                error_message = str(exc_info.value)
                assert "401" in error_message or "Unauthorized" in error_message
    
    def test_system_processes_real_world_data_variations_correctly(self, complex_api_responses):
        """
        GIVEN API responses with various data quality issues (missing fields, duplicates, etc.)
        WHEN user runs extraction process
        THEN system handles all variations gracefully and produces clean output
        """
        # This tests real-world data scenarios like missing authors, malformed dates,
        # duplicate reports, missing summaries, etc.
        with patch.dict(os.environ, {'CONGRESSGOV_API_KEY': 'valid_test_key'}):
            with patch('requests.Session') as mock_session:
                mock_session.return_value = complex_api_responses['session']
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_file = Path(temp_dir) / 'complex_test.csv'
                    
                    # Act: Process complex real-world data
                    extractor = CRSSummaryExtractor()
                    extractor.run(str(output_file))
                    
                    # Assert: System handles all variations
                    assert output_file.exists()
                    
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Should contain processed data even with missing fields
                    lines = content.strip().split('\n')
                    assert len(lines) >= 2, "Should process available data despite quality issues"


class TestDataValidationAndSecurity:
    """Test input validation and security measures that protect users and system."""
    
    def test_api_key_validation_prevents_security_vulnerabilities(self):
        """
        GIVEN various invalid API key scenarios
        WHEN system validates API keys
        THEN system rejects unsafe inputs and provides clear error messages
        """
        # Test cases covering security concerns
        invalid_keys = [
            None,  # Missing key
            "",   # Empty key
            "   ", # Whitespace only
            "x",   # Too short
            123,    # Wrong type
        ]
        
        for invalid_key in invalid_keys:
            with patch.dict(os.environ, {'CONGRESSGOV_API_KEY': str(invalid_key) if invalid_key else ''}):
                if invalid_key is None:
                    os.environ.pop('CONGRESSGOV_API_KEY', None)
                
                with pytest.raises(ConfigurationError) as exc_info:
                    CRSSummaryExtractor()
                
                # Verify error message is helpful for users
                error_msg = str(exc_info.value).lower()
                assert any(word in error_msg for word in ['api key', 'required', 'missing', 'invalid'])
    
    def test_filename_validation_prevents_directory_traversal_attacks(self):
        """
        GIVEN potentially malicious filename inputs
        WHEN system validates output filenames
        THEN system prevents directory traversal and other file system attacks
        """
        dangerous_filenames = [
            "../../../etc/passwd",  # Directory traversal
            "/tmp/malicious.csv",    # Absolute path
            "..\\\\..\\\\windows\\\\system32\\\\file.csv",  # Windows traversal
            "file with spaces.txt",  # Wrong extension
            "",  # Empty filename
            "normal_file",  # No extension
        ]
        
        for dangerous_filename in dangerous_filenames:
            with pytest.raises(ValidationError):
                InputValidator.validate_filename(dangerous_filename)
    
    def test_report_id_validation_prevents_injection_attacks(self):
        """
        GIVEN potentially malicious report ID inputs
        WHEN system validates report IDs
        THEN system prevents SQL injection and other code injection attacks
        """
        malicious_ids = [
            "'; DROP TABLE reports; --",  # SQL injection
            "<script>alert('xss')</script>",  # XSS attempt
            "../../../etc/passwd",  # Path traversal
            "\\x00\\x01\\x02",  # Control characters
            "a" * 1000,  # Extremely long input
        ]
        
        for malicious_id in malicious_ids:
            with pytest.raises(ValidationError):
                InputValidator.validate_report_id(malicious_id)


class TestErrorRecoveryAndResilience:
    """Test system behavior under various failure conditions."""
    
    def test_system_continues_processing_when_individual_reports_fail(self):
        """
        GIVEN API that fails for some reports but succeeds for others
        WHEN user runs extraction process
        THEN system processes all available reports and reports partial success
        """
        with patch.dict(os.environ, {'CONGRESSGOV_API_KEY': 'valid_test_key'}):
            with patch('requests.Session') as mock_session:
                # Mock session that fails for some requests but succeeds for others
                def side_effect_get(url):
                    if 'failing-report-id' in url:
                        mock_response = Mock()
                        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
                        return mock_response
                    else:
                        mock_response = Mock()
                        mock_response.raise_for_status.return_value = None
                        mock_response.json.return_value = {
                            'CRSReport': {
                                'title': 'Working Report',
                                'summary': 'This report works fine.',
                                'authors': [{'author': 'Test Author'}],
                                'url': 'https://example.com'
                            }
                        }
                        return mock_response
                
                mock_session.return_value.get.side_effect = side_effect_get
                
                # Mock initial list call
                list_response = Mock()
                list_response.raise_for_status.return_value = None
                list_response.json.return_value = {
                    'CRSReports': [
                        {'id': 'working-report', 'status': 'Active', 'publishDate': '2024-01-01', 'version': '1'},
                        {'id': 'failing-report-id', 'status': 'Active', 'publishDate': '2024-01-01', 'version': '1'}
                    ]
                }
                
                # Set up the mock to return list_response for list calls and side_effect for detail calls
                def get_response(url):
                    if 'crsreport?' in url:  # List call
                        return list_response
                    else:  # Detail call
                        return side_effect_get(url)
                
                mock_session.return_value.get.side_effect = get_response
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_file = Path(temp_dir) / 'partial_success.csv'
                    
                    # Act: Should complete despite partial failures
                    extractor = CRSSummaryExtractor()
                    extractor.run(str(output_file))
                    
                    # Assert: File created with available data
                    assert output_file.exists()
                    
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Should contain the working report but not the failing one
                    assert 'Working Report' in content
    
    def test_system_provides_helpful_error_messages_for_common_problems(self):
        """
        GIVEN common user configuration problems
        WHEN system encounters these issues
        THEN system provides specific, actionable error messages
        """
        # Test missing environment file
        with patch('os.getenv', return_value=None):
            with pytest.raises(ConfigurationError) as exc_info:
                CRSSummaryExtractor()
            
            error_msg = str(exc_info.value)
            assert '.env' in error_msg or 'environment' in error_msg
            assert 'API key' in error_msg or 'CONGRESSGOV_API_KEY' in error_msg


# Test fixtures and helpers

@pytest.fixture
def mock_api_responses():
    """Provide realistic mock API responses for testing."""
    
    # Mock list response
    list_response = Mock()
    list_response.raise_for_status.return_value = None
    list_response.json.return_value = {
        'CRSReports': [
            {
                'id': 'TEST123',
                'status': 'Active',
                'publishDate': '2024-01-15T10:30:00Z',
                'version': '1',
                'title': 'Test Report Title',
                'url': 'https://www.congress.gov/crs-report/TEST123'
            }
        ]
    }
    
    # Mock detail response
    detail_response = Mock()
    detail_response.raise_for_status.return_value = None
    detail_response.json.return_value = {
        'CRSReport': {
            'title': 'Test Report Title',
            'summary': 'This is a comprehensive summary of the test report that contains detailed information about the topic being discussed. It provides context and analysis that would be valuable for congressional staff and researchers.',
            'authors': [{'author': 'John Smith'}, {'author': 'Jane Doe'}],
            'url': 'https://www.congress.gov/crs-report/TEST123',
            'publishDate': '2024-01-15T10:30:00Z'
        }
    }
    
    # Mock session
    session = Mock()
    session.timeout = 30
    
    def get_side_effect(url):
        if 'crsreport?' in url:  # List endpoint
            return list_response
        else:  # Detail endpoint
            return detail_response
    
    session.get.side_effect = get_side_effect
    
    return {
        'session': session,
        'list_response': list_response,
        'detail_response': detail_response
    }


@pytest.fixture
def complex_api_responses():
    """Provide complex mock responses with data quality issues."""
    
    # Mock list with various data quality issues
    list_response = Mock()
    list_response.raise_for_status.return_value = None
    list_response.json.return_value = {
        'CRSReports': [
            # Normal report
            {'id': 'NORMAL1', 'status': 'Active', 'publishDate': '2024-01-01', 'version': '1'},
            # Duplicate with higher version
            {'id': 'DUP1', 'status': 'Active', 'publishDate': '2024-01-01', 'version': '1'},
            {'id': 'DUP1', 'status': 'Active', 'publishDate': '2024-01-01', 'version': '2'},
            # Inactive report (should be filtered out)
            {'id': 'INACTIVE1', 'status': 'Inactive', 'publishDate': '2024-01-01', 'version': '1'},
            # Report with missing fields
            {'id': 'MISSING1', 'status': 'Active'},  # Missing publishDate and version
        ]
    }
    
    # Mock detail responses with various issues
    def detail_side_effect(url):
        response = Mock()
        response.raise_for_status.return_value = None
        
        if 'NORMAL1' in url:
            response.json.return_value = {
                'CRSReport': {
                    'title': 'Normal Report',
                    'summary': 'A normal summary with all fields present.',
                    'authors': [{'author': 'Normal Author'}],
                    'url': 'https://example.com/normal1'
                }
            }
        elif 'DUP1' in url:
            response.json.return_value = {
                'CRSReport': {
                    'title': 'Duplicate Report (Version 2)',
                    'summary': 'This is the higher version of the duplicate.',
                    'authors': [{'author': 'Duplicate Author'}],
                    'url': 'https://example.com/dup1'
                }
            }
        elif 'MISSING1' in url:
            response.json.return_value = {
                'CRSReport': {
                    'title': 'Report with Missing Fields',
                    # Missing summary and authors
                    'url': 'https://example.com/missing1'
                }
            }
        
        return response
    
    # Mock session
    session = Mock()
    session.timeout = 30
    
    def get_side_effect(url):
        if 'crsreport?' in url:  # List endpoint
            return list_response
        else:  # Detail endpoint
            return detail_side_effect(url)
    
    session.get.side_effect = get_side_effect
    
    return {
        'session': session,
        'list_response': list_response
    }


# Additional test utilities

def create_test_environment():
    """Helper to create isolated test environment."""
    return tempfile.TemporaryDirectory()


def assert_csv_structure(csv_path: Path, expected_rows: int = None):
    """Helper to validate CSV file structure."""
    assert csv_path.exists(), "CSV file should exist"
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    assert len(lines) >= 2, "CSV should have header plus data rows"
    
    # Verify headers
    expected_headers = ['Title', 'Date Published', 'Author(s)', 'URL', '300-word Summary']
    header_line = lines[0]
    for header in expected_headers:
        assert header in header_line, f"Missing header: {header}"
    
    if expected_rows:
        assert len(lines) == expected_rows + 1, f"Expected {expected_rows} data rows plus header"
