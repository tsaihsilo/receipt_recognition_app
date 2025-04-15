import boto3
import os
import json
import time
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# Set up clients
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

# S3 bucket + file
bucket_name = 'receipt-app-demo-mhomer'
original_file = 'receipt-1.png'
jpeg_file = 'receipt-1.jpg'
s3_path = jpeg_file

# Convert PNG to JPEG
print("Converting image to JPEG...")
img = Image.open(original_file)
img = img.convert('RGB')  # Convert to RGB mode if needed
img.save(jpeg_file, 'JPEG', quality=95)
print(f"Saved as {jpeg_file}")

# Step 1: Upload to S3
print("Uploading image to S3...")
s3.upload_file(
    jpeg_file, 
    bucket_name, 
    s3_path,
    ExtraArgs={'ContentType': 'image/jpeg'}
)

# Verify upload
try:
    response = s3.head_object(Bucket=bucket_name, Key=s3_path)
    print(f"Successfully verified file exists at s3://{bucket_name}/{s3_path}")
    print("File metadata:")
    print(f"Content Type: {response.get('ContentType')}")
    print(f"Content Length: {response.get('ContentLength')} bytes")
    print(f"Last Modified: {response.get('LastModified')}")
except Exception as e:
    print(f"Error verifying file: {e}")

# Step 2: Start Textract job
print("Starting Textract job...")
try:
    print(f"Using region: {os.getenv('AWS_DEFAULT_REGION')}")
    print(f"Attempting to process file: s3://{bucket_name}/{s3_path}")
    
    response = textract.start_document_analysis(
        DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': s3_path}},
        FeatureTypes=['FORMS', 'TABLES'],
        JobTag='ReceiptAnalysis'
    )
    job_id = response['JobId']
    print("Job started with ID:", job_id)
    
    # Poll until job completes
    print("Waiting for job to complete...")
    while True:
        result = textract.get_document_analysis(JobId=job_id)
        status = result['JobStatus']
        print(f"Current status: {status}")
        if status in ['SUCCEEDED', 'FAILED']:
            break
        time.sleep(5)
    
    if status == 'SUCCEEDED':
        # Save result to JSON
        with open("async_output.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Done! Result saved to async_output.json")
    else:
        print(f"Job failed with status: {status}")
        if 'StatusMessage' in result:
            print(f"Status message: {result['StatusMessage']}")

except Exception as e:
    print(f"Error processing document: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    raise 