import os
import boto3
from datetime import datetime


def main():

    filename = 'pgsql.sql' + '_' + datetime.strftime(datetime.utcnow(), "%Y.%m.%d.%H:%M:%S") + 'UTC' + '.backup'

    os.system('pg_dump -h $PG_HOST -U $PG_USER --encoding UTF8 --format plain $PG_DATABASE > %s' %(filename))

    if os.path.exists(filename):
        upload_to_s3(filename)
        os.remove(filename)

def upload_to_s3(filename):

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('AWS_HOST'),
    )

    bucket_name = os.getenv('AWS_BUCKET_NAME')


    with open(filename, "rb") as data:
        s3.upload_fileobj(data, bucket_name, filename)

if __name__ == '__main__':

    main()