import os
import boto3

def test_backup_file_created_in_s3():
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_DB_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_DB_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_DB_AWS_ENDPOINT'),
    )

    bucket_name = os.getenv('DESTINATION_DB_AWS_BUCKET_NAME')
    
    response = s3.list_objects_v2(Bucket=bucket_name)
    
    if 'Contents' not in response:
        raise Exception("No files found in S3 bucket")
    
    backup_files = []
    for obj in response['Contents']:
        prefix = os.getenv('DB_BACKUPS_FILENAME_PREFIX')
        if obj['Key'].startswith(prefix):
            backup_files.append(obj)
    
    if len(backup_files) <= 0:
        raise Exception("No backup files found with the correct prefix")
    
    for backup_file in backup_files:
        file_size = backup_file['Size']
        if file_size <= 0:
            raise Exception(f"Empty backup file: {backup_file['Key']}")

def test_database_backup_content():
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_DB_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_DB_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_DB_AWS_ENDPOINT'),
    )

    bucket_name = os.getenv('DESTINATION_DB_AWS_BUCKET_NAME')
    
    # Get the latest backup file
    response = s3.list_objects_v2(Bucket=bucket_name)

    backup_files = []
    for obj in response['Contents']:
        prefix = os.getenv('DB_BACKUPS_FILENAME_PREFIX')
        if obj['Key'].startswith(prefix):
            backup_files.append(obj)

    latest_backup = None
    for file in backup_files:
        if latest_backup is None or file['LastModified'] > latest_backup['LastModified']:
            latest_backup = file

    tmp_file = '/tmp/latest_backup.backup'
    s3.download_file(bucket_name, latest_backup['Key'], tmp_file)
    
    with open(tmp_file, 'r') as f:
        content = f.read()

    print(content[:200])
        

    if 'PostgreSQL database dump' not in content:
        raise Exception("Content is not a valid PostgreSQL dump")
    
    if 'CREATE DATABASE' not in content or 'CREATE TABLE' not in content:
        raise Exception("Backup file missing CREATE DATABASE or CREATE TABLE statements")
