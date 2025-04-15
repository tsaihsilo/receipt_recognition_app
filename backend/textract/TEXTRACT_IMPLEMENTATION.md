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