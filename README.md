# CRS Summary Extractor

A robust, enterprise-grade Python application that fetches Congressional Research Service (CRS) documents from the Congress.gov API and creates professionally formatted Word documents with comprehensive summaries, metadata, and source attribution.

## What It Does

This tool processes CRS documents from the official Congress.gov API to create professionally formatted Word documents for research, analysis, and reporting. It handles data quality issues, implements security best practices, and provides detailed progress tracking and error reporting.

### Key Capabilities

- **Comprehensive Data Extraction**: Fetches document metadata, full summaries, author information, and publication details
- **Intelligent Filtering**: Processes only active documents and removes duplicates automatically
- **Data Quality Assurance**: Validates all inputs, sanitizes content, and handles missing or malformed data gracefully
- **Security-First Design**: Implements input validation, prevents injection attacks, and protects sensitive information
- **Enterprise Logging**: Provides structured, correlation-tracked logging for debugging and monitoring
- **Resilient Processing**: Continues operation despite individual document failures and provides detailed error reporting

## Features

### Core Functionality
- ✅ Fetches up to 250 most recent CRS documents from Congress.gov API
- ✅ Filters to include only documents with "Active" status
- ✅ Removes duplicates (keeps highest version for same ID + publish date)
- ✅ Generates professionally formatted Word documents with:
  1. **Level 2 Headings**: Report titles for easy navigation
  2. **Subheadings**: Author names and publication dates
  3. **Body Text**: 300-word summaries for each report
  4. **Italicized Metadata**: Report IDs and URLs at the end of each summary
  5. **Proper Spacing**: Two line breaks between individual reports

### Enterprise Features
- 🔒 **Security**: Input validation, path traversal prevention, API key protection
- 📊 **Monitoring**: Structured logging with correlation IDs and performance metrics
- 🛡️ **Error Handling**: Comprehensive exception handling with user-friendly messages
- ⚡ **Performance**: Rate limiting, request timeouts, and efficient processing
- 🧪 **Testing**: Behavior-driven tests covering real-world scenarios
- 📝 **Documentation**: Comprehensive inline documentation and usage examples

## Installation

### Quick Start

1. **Clone or download** this repository to your local machine

2. **Install dependencies**:
```bash
pip3 install -r requirements.txt
```

3. **Configure your API key** in `.gitignore/.env`:
```bash
echo "CONGRESSGOV_API_KEY=your_actual_api_key_here" > .gitignore/.env
```

4. **Run the extractor**:
```bash
python3 crs_summary_extractor.py
```

### Development Installation

For development work with type checking and testing:

```bash
# Install all dependencies including development tools
pip3 install -r requirements.txt -r requirements-dev.txt

# Or use the project configuration
pip3 install -e .[dev]
```

## Usage

### Basic Usage

```bash
# Extract CRS summaries to default file (crs_summaries.docx)
python3 crs_summary_extractor.py

# Specify custom output filename
python3 crs_summary_extractor.py --output my_crs_data.docx

# Enable verbose logging for debugging
python3 crs_summary_extractor.py --verbose

# Output structured JSON logs for monitoring systems
python3 crs_summary_extractor.py --json-logs
```

### Command Line Options

```bash
python3 crs_summary_extractor.py --help
```

**Available options:**
- `--output, -o`: Specify output Word document filename (default: `crs_summaries.docx`)
- `--verbose, -v`: Enable detailed logging for debugging
- `--json-logs`: Output structured JSON logs for log aggregation systems

### Configuration

The application requires a Congress.gov API key configured in `.env`:

```bash
# .env
CONGRESSGOV_API_KEY=your_api_key_from_congress_gov
```

**Getting an API Key:**
1. Visit [Congress.gov API Documentation](https://api.congress.gov/)
2. Request an API key following their process
3. Add the key to your `.env` file

## Output Format

The generated Word document contains professionally formatted reports with the following structure:

### Document Layout
- **Document Title**: "CRS Summary Report" (centered, main heading)
- **Generation Date**: Current date when the document was created (centered, italicized)

### Individual Report Format
Each CRS report is formatted as follows:

1. **Level 2 Heading**: Report title (e.g., "Social Security: Overview and Key Issues")
2. **Subheading**: Author and publication date (bold, smaller font)
   - Format: "By [Author Names] | Published [Date]"
   - Example: "By John Smith; Jane Doe | Published 2024-01-15"
3. **Body Text**: 300-word summary of the report content
4. **Metadata**: Report ID and URL (italicized, smaller font)
   - Format: "Report ID: [ID] | URL: [URL]"
   - Example: "Report ID: RS12345 | URL: https://www.congress.gov/crs-report/RS12345"

### Spacing and Organization
- **Two line breaks** separate each individual report
- Professional spacing for easy reading and navigation
- Consistent formatting throughout the document

## Architecture and Design

### Security Measures

- **Input Validation**: All user inputs are validated and sanitized
- **Path Safety**: Filename validation prevents directory traversal attacks  
- **API Key Protection**: Keys are never logged or exposed in error messages
- **Rate Limiting**: Respectful API usage with built-in request throttling
- **Error Information**: Error messages don't expose sensitive system details

### Error Handling Strategy

The application implements comprehensive error handling:

1. **Configuration Errors**: Clear guidance for API key and environment issues
2. **Network Errors**: Graceful handling of connectivity and timeout issues  
3. **API Errors**: Specific handling of authentication, rate limiting, and server errors
4. **Data Processing Errors**: Validation and sanitization of all data inputs
5. **File System Errors**: Safe file operations with proper cleanup

### Logging and Monitoring

- **Structured Logging**: JSON-compatible logs with correlation IDs
- **Performance Tracking**: Request timing and throughput metrics
- **Security Logging**: Failed authentication and validation attempts
- **User Privacy**: Document content is hashed, not logged in full

## Development

### Code Quality Standards

This project follows enterprise development standards:

- **Type Safety**: Full mypy type checking with strict configuration
- **Testing**: Behavior-driven tests covering real user workflows
- **Documentation**: Comprehensive docstrings and architectural decision records
- **Security**: Input validation and secure coding practices
- **Error Handling**: Comprehensive exception handling with user-friendly messages

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage reporting
pytest --cov=crs_summary_extractor

# Run specific test categories
pytest tests/test_crs_extractor.py::TestUserWorkflows
```

### Type Checking

```bash
# Run type checking
mypy crs_summary_extractor.py

# Check all files
mypy .
```

### Code Formatting

```bash
# Format code
black crs_summary_extractor.py

# Check formatting
black --check .
```

## Troubleshooting

### Common Issues

**"API key not found" Error:**
1. Verify `.gitignore/.env` file exists in the project directory
2. Check that the file contains `CONGRESSGOV_API_KEY=your_key`
3. Ensure there are no extra spaces or quotes around the key
4. Verify your API key is still valid at Congress.gov

**"No reports found" Error:**
1. Check your internet connection
2. Verify your API key is still active
3. Try again later (may be temporary API maintenance)

**"Permission denied" Error:**
1. Ensure you have write permissions in the current directory
2. Try specifying a different output location with `--output`
3. Check that the file isn't open in Microsoft Word or another program

**Network/Timeout Errors:**
1. Check your internet connection stability
2. Try running with `--verbose` to see detailed error information
3. Consider running during off-peak hours if API is slow

### Getting Help

For additional support:

1. **Check the logs**: Run with `--verbose` for detailed diagnostic information
2. **Review error messages**: The application provides specific guidance for common issues
3. **Verify configuration**: Ensure API key and file permissions are correct
4. **Test connectivity**: Try accessing Congress.gov directly in your browser

## Requirements

### System Requirements
- **Python**: 3.8 or higher (3.10+ recommended for development)
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 512MB available RAM
- **Disk Space**: 50MB for application + space for output files
- **Network**: Stable internet connection for API access

### Dependencies
- `requests>=2.28.0`: HTTP client for API communication
- `python-dotenv>=1.0.0`: Environment variable management
- `python-docx>=1.1.0`: Word document creation and formatting

### Development Dependencies (Optional)
- `mypy>=1.0.0`: Static type checking
- `pytest>=7.0.0`: Testing framework  
- `pytest-cov>=4.0.0`: Coverage reporting
- `black>=22.0.0`: Code formatting
- `types-requests>=2.28.0`: Type stubs for requests library
- `pre-commit>=3.0.0`: Git hooks for quality checks

## License and Compliance

This tool is designed for legitimate research and analysis purposes. Users are responsible for:

- Complying with Congress.gov API terms of service
- Respecting rate limits and usage guidelines  
- Properly attributing CRS documents in research and publications
- Following institutional policies for data collection and storage

## Contributing

Contributions are welcome! Please ensure:

- All tests pass (`pytest`)
- Type checking passes (`mypy`)
- Code is formatted (`black`)
- New features include comprehensive tests
- Documentation is updated for any API changes

## Version History

- **v1.0.0**: Initial release with comprehensive error handling, security measures, and enterprise logging

## Project Structure

```
crs-summaries/
├── .env                              # API key (secure location)
├── .gitignore                        # Git ignore rules
├── crs_summary_extractor.py          # Main application (Word document generator)
├── pyproject.toml                    # Project configuration with mypy settings
├── requirements.txt                  # Runtime dependencies
├── requirements-dev.txt              # Development dependencies
├── README.md                         # This comprehensive documentation
├── CLAUDE.md                         # Original requirements specification
├── tests/
│   ├── __init__.py
│   └── test_crs_extractor.py        # Behavior-driven tests
└── rules/                           # Coding standards (24 rule files)
    ├── README.md
    ├── error-handling-logging.mdc
    ├── security-privacy.mdc
    ├── data-validation.mdc
    └── ... (21 more rule files)
```
