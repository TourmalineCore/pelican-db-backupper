import os
import boto3
from datetime import datetime

os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "when_required"
os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "when_required"

def main():
    os.system('pg_dump -h $PG_HOST -U $PG_USER --encoding UTF8 --format plain $PG_DATABASE > pgsql.sql')

    if os.path.exists('pgsql.sql'):
        source_path = 'pgsql.sql'

        destination_filename = source_path + '_' + datetime.strftime(datetime.utcnow(), "%Y.%m.%d.%H:%M:%S") + 'UTC' + '.backup'

        upload_to_s3(source_path, destination_filename)

def upload_to_s3(source_path, destination_filename):

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('AWS_HOST')
    )

    bucket_name = os.getenv('AWS_BUCKET_NAME')


    with open(source_path, "rb") as data:
        s3.upload_fileobj(data, bucket_name, destination_filename)

if __name__ == '__main__':

    main()
