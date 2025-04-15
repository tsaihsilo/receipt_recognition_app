# AWS Textract Implementation Guide

## Overview
This document explains the implementation of AWS Textract for receipt processing in our application. The main script `async_textract_receipt.py` demonstrates how to use AWS Textract to extract information from receipt images.

## Key Components

### 1. AWS Client Setup
```python
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

textract = boto3.client(
    'textract',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)
```
- Sets up S3 and Textract clients using credentials from environment variables
- Both services use the same AWS credentials and region
- Environment variables are loaded using `python-dotenv`

### 2. Image Processing
```python
# Convert PNG to JPEG
img = Image.open(original_file)
img = img.convert('RGB')
img.save(jpeg_file, 'JPEG', quality=95)
```
- Converts PNG images to JPEG format
- Ensures RGB color mode for compatibility
- Maintains high quality (95%) for accurate OCR

### 3. S3 Upload Process
```python
s3.upload_file(
    jpeg_file, 
    bucket_name, 
    s3_path,
    ExtraArgs={'ContentType': 'image/jpeg'}
)
```
- Uploads the processed image to S3
- Sets proper content type for JPEG
- Verifies upload success with metadata check

### 4. Textract Analysis
```python
response = textract.start_document_analysis(
    DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': s3_path}},
    FeatureTypes=['FORMS', 'TABLES'],
    JobTag='ReceiptAnalysis'
)
```
- Initiates asynchronous document analysis
- Uses both FORMS and TABLES feature types for comprehensive extraction
- Tags the job for easy identification

### 5. Result Processing
```python
while True:
    result = textract.get_document_analysis(JobId=job_id)
    status = result['JobStatus']
    if status in ['SUCCEEDED', 'FAILED']:
        break
    time.sleep(5)
```
- Polls for job completion every 5 seconds
- Handles both success and failure cases
- Saves results to JSON for further processing

## Environment Setup
Required environment variables:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_DEFAULT_REGION`: AWS region (e.g., us-east-1)

## Dependencies
- boto3==1.34.29
- python-dotenv==1.0.1
- Pillow==10.2.0

## Best Practices
1. Always verify S3 uploads before processing
2. Use appropriate image formats (JPEG/PNG)
3. Implement proper error handling
4. Store sensitive credentials in environment variables
5. Use appropriate polling intervals for job status checks

## Error Handling
The implementation includes comprehensive error handling for:
- S3 upload verification
- Textract job status monitoring
- File processing and conversion
- JSON result saving

## Output Format
Results are saved in JSON format with the following structure:
- Job metadata (ID, status, timestamp)
- Extracted text blocks
- Form fields and values
- Table data (if present)
- Confidence scores for each extraction

## Supported Image Formats and Textract Limitations

### Image Format Support
- **AWS Textract supports both PNG and JPEG images**
- PNG images are automatically converted to JPEG for processing
- JPEG format is preferred for optimal performance

### Textract Image Processing Limitations
1. **File Size Limits:**
   - Maximum file size: 5MB
   - Minimum file size: 1KB
   - Recommended resolution: 300 DPI or higher

2. **Format Restrictions:**
   - No TIFF or GIF support
   - No BMP or other image formats
   - No handwritten text support (designed for printed/typed text)

3. **Regional Availability:**
   - Not all AWS regions support Textract
   - Ensure S3 bucket and Textract client are in supported regions
   - Check AWS documentation for latest regional availability

4. **Content Limitations:**
   - Works best with clear, well-lit images
   - Performance may vary with low-quality or blurry images
   - May struggle with highly stylized fonts or unusual layouts

5. **Processing Time:**
   - Asynchronous processing typically takes 1-5 seconds
   - Processing time increases with document complexity
   - Rate limits may apply based on AWS account type 

## Detailed Code Explanation

### Imports and Setup
```python
import boto3
import os
import json
import time
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
```
- `boto3`: AWS SDK for Python, used to interact with AWS services
- `os`: Used to access environment variables and file operations
- `json`: For handling JSON data from Textract responses
- `time`: For implementing polling delays
- `dotenv`: Loads environment variables from .env file
- `PIL`: Python Imaging Library for image processing
- `load_dotenv()`: Loads environment variables at startup

### AWS Client Configuration
```python
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)
```
- Creates an S3 client for file uploads
- Uses environment variables for secure credential management
- Configures the AWS region for service access

```python
textract = boto3.client(
    'textract',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)
```
- Creates a Textract client for document analysis
- Uses same credentials as S3 for consistency
- Must be in same region as S3 bucket

### File Configuration
```python
bucket_name = 'receipt-app-demo-mhomer'
original_file = 'receipt-1.png'
jpeg_file = 'receipt-1.jpg'
s3_path = jpeg_file
```
- `bucket_name`: Target S3 bucket for file storage
- `original_file`: Input PNG file name
- `jpeg_file`: Output JPEG file name
- `s3_path`: Path where file will be stored in S3

### Image Processing
```python
print("Converting image to JPEG...")
img = Image.open(original_file)
img = img.convert('RGB')
img.save(jpeg_file, 'JPEG', quality=95)
print(f"Saved as {jpeg_file}")
```
- Opens the original PNG file
- Converts to RGB color mode (required for JPEG)
- Saves as JPEG with high quality (95%)
- Provides user feedback on conversion

### S3 Upload Process
```python
print("Uploading image to S3...")
s3.upload_file(
    jpeg_file, 
    bucket_name, 
    s3_path,
    ExtraArgs={'ContentType': 'image/jpeg'}
)
```
- Uploads the JPEG file to S3
- Sets content type explicitly for proper handling
- Uses the same path as local file name

### Upload Verification
```python
try:
    response = s3.head_object(Bucket=bucket_name, Key=s3_path)
    print(f"Successfully verified file exists at s3://{bucket_name}/{s3_path}")
    print("File metadata:")
    print(f"Content Type: {response.get('ContentType')}")
    print(f"Content Length: {response.get('ContentLength')} bytes")
    print(f"Last Modified: {response.get('LastModified')}")
except Exception as e:
    print(f"Error verifying file: {e}")
```
- Verifies successful upload using head_object
- Displays important file metadata
- Handles potential upload errors gracefully

### Textract Analysis
```python
print("Starting Textract job...")
try:
    print(f"Using region: {os.getenv('AWS_DEFAULT_REGION')}")
    print(f"Attempting to process file: s3://{bucket_name}/{s3_path}")
    
    response = textract.start_document_analysis(
        DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': s3_path}},
        FeatureTypes=['FORMS', 'TABLES'],
        JobTag='ReceiptAnalysis'
    )
```
- Initiates asynchronous document analysis
- Uses S3 location for file access
- Enables both form and table detection
- Tags job for easy identification

### Job Status Monitoring
```python
    job_id = response['JobId']
    print("Job started with ID:", job_id)
    
    print("Waiting for job to complete...")
    while True:
        result = textract.get_document_analysis(JobId=job_id)
        status = result['JobStatus']
        print(f"Current status: {status}")
        if status in ['SUCCEEDED', 'FAILED']:
            break
        time.sleep(5)
```
- Extracts job ID from initial response
- Polls for job completion every 5 seconds
- Provides real-time status updates
- Breaks loop on completion or failure

### Result Handling
```python
    if status == 'SUCCEEDED':
        with open("async_output.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Done! Result saved to async_output.json")
    else:
        print(f"Job failed with status: {status}")
        if 'StatusMessage' in result:
            print(f"Status message: {result['StatusMessage']}")
```
- Saves successful results to JSON file
- Uses pretty printing (indent=2) for readability
- Provides detailed error information on failure

### Error Handling
```python
except Exception as e:
    print(f"Error processing document: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    raise
```
- Catches and logs any unexpected errors
- Shows both error message and type
- Re-raises exception for upstream handling 