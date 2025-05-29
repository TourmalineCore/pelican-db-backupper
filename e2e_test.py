import os
import boto3
from datetime import datetime
import time

def test_backup_file_created_in_s3():
    # Configure S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_DB_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_DB_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_DB_AWS_ENDPOINT'),
    )

    bucket_name = os.getenv('DESTINATION_DB_AWS_BUCKET_NAME')
    
    # List objects in the bucket
    response = s3.list_objects_v2(Bucket=bucket_name)
    
    # Check that at least one backup file exists
    assert 'Contents' in response, "No files found in S3 bucket"
    
    # Check that the backup file has the correct prefix
    backup_files = [obj for obj in response['Contents'] 
                   if obj['Key'].startswith(os.getenv('DB_BACKUPS_FILENAME_PREFIX'))]
    
    assert len(backup_files) > 0, "No backup files found with the correct prefix"
    
    # Check that the backup file is not empty
    for backup_file in backup_files:
        file_size = backup_file['Size']
        assert file_size > 0, f"Backup file {backup_file['Key']} is empty"

def test_database_backup_content():
    # Configure S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_DB_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_DB_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_DB_AWS_ENDPOINT'),
    )

    bucket_name = os.getenv('DESTINATION_DB_AWS_BUCKET_NAME')
    
    # Get the latest backup file
    response = s3.list_objects_v2(Bucket=bucket_name)
    backup_files = [obj for obj in response['Contents'] 
                   if obj['Key'].startswith(os.getenv('DB_BACKUPS_FILENAME_PREFIX'))]
    latest_backup = max(backup_files, key=lambda x: x['LastModified'])
    
    # Download the backup file
    tmp_file = '/tmp/latest_backup.backup'
    s3.download_file(bucket_name, latest_backup['Key'], tmp_file)
    
    # Check that the backup contains expected content
    with open(tmp_file, 'r') as f:
        content = f.read()
        
    # Basic checks for PostgreSQL dump format
    assert 'PostgreSQL database dump' in content
    assert 'CREATE DATABASE' in content or 'CREATE TABLE' in content