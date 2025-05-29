import os
import boto3
from datetime import datetime
import sys

def main():
    try:
        backup_filename = os.getenv('DB_BACKUPS_FILENAME_PREFIX') + '-' + datetime.strftime(datetime.utcnow(), "%Y-%m-%dT%H-%M-%S") + '.backup'
        
        # Test database connection
        test_db_connection()
        
        # Create backup
        os.system('pg_dump -h $DATABASE_HOST -U $DATABASE_USERNAME --encoding UTF8 --format plain $DATABASE_NAME > %s' % backup_filename)

        if not os.path.exists(backup_filename):
            raise Exception("Backup file was not created")

        # Verify backup file is not empty
        if os.path.getsize(backup_filename) == 0:
            raise Exception("Backup file is empty")

        upload_to_s3(backup_filename)
        os.remove(backup_filename)
        
        # Write success file for testing
        with open("/tmp/backup_success", "w") as f:
            f.write("success")

    except Exception as e:
        print(f"Backup failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

def test_db_connection():
    """Test if we can connect to the database"""
    test_query = "SELECT 1"
    result = os.system(f'psql -h $DATABASE_HOST -U $DATABASE_USERNAME -d $DATABASE_NAME -c "{test_query}"')
    if result != 0:
        raise Exception("Database connection test failed")

def upload_to_s3(backup_filename):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_DB_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_DB_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_DB_AWS_ENDPOINT'),
    )
    bucket_name = os.getenv('DESTINATION_DB_AWS_BUCKET_NAME')

    with open(backup_filename, "rb") as data:
        s3.upload_fileobj(data, bucket_name, backup_filename)

if __name__ == '__main__':
    main()