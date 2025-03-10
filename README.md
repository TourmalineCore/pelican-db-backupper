# PostgreSQL k8s backup & restore

## Prerequisites
1. Install Docker
2. Prepared pelican-local-env project

## Backup
### 1. Build docker image 
```bash
docker build -t pgsql-backup:0.0.1 .
```
### 2. Load docker image into pelican cluster
```bash
kind load docker-image pgsql-backup:0.0.1 --name pelican
```
### 3. Configure CronJob pgsql-backup-cron.yaml
```bash
- name: PG_HOST
  value: 10.244.0.7
- name: PGPASSWORD
  value: admin
- name: PG_USER
  value: postgres
- name: PG_DATABASE
  value: pelican_db
- name: AWS_ACCESS_KEY_ID
  value: CbYUcMLdKB5ySRHmxmKS
- name: AWS_SECRET_ACCESS_KEY
  value: 6CRcWtYhx5ASQRvrjzMJVERcE04SD2ccTzNsVXHW
- name: AWS_BUCKET_NAME
  value: pelican-db-backup
- name: AWS_HOST
  value: http://10.244.0.8:9000
```
Change PG_HOST, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME, AWS_HOST to your values

### 4. Apply CronJob
```bash
kubectl apply -f pgsql-backup-cron.yaml
```
Check your S3 bucket

## Restore

### 1. Manually download backup from S3 and copy to your project

### 2. Copy backup to the pod
```bash
kubectl cp <backup-name> postgresql-0:<path> -n local
```
### Example
```bash
kubectl cp pgsql.sql_2025.03.03.06_41UTC.backup postgresql-0:tmp/pgsql.sql_2025.03.03.06_41UTC.backup -n local
```
### 3. Connect to the postgresql-0 pod and execute psql command to restore data
```bash
kubectl exec -it postgresql-0 -n local -- psql -U postgres -d pelican_db -f <path>/<backup-name.backup>
```
### Example
```bash
kubectl exec -it postgresql-0 -n local -- psql -U postgres -d pelican_db -f tmp/pgsql.sql_2025.03.03.06_41UTC.backup
```
