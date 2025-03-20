# pelican-db-backupper

Больше информации о проекте и связанных репозиториях можно найти здесь: 
[pelican-documentation](https://github.com/TourmalineCore/pelican-documentation).

## Подготовка перед запуском
1. Установите Docker
2. Подготовьте проект pelican-local-env 

## Настройка резервной копии при добавлении проекта вручную
### 1. Соберите Docker образ 
```bash
docker build -t pgsql-backup:0.0.1 .
```
### 2. Загрузите Docker образ в кластер
```bash
kind load docker-image pgsql-backup:0.0.1 --name pelican
```
### 3. Настройте секреты в pgsql-backup-secret.yaml
```bash
    PG_HOST: "postgresql"
    PG_PASSWORD: "admin"
    PG_USER: "postgres"
    PG_DATABASE: "pelican_db"
    AWS_ACCESS_KEY_ID: "admin"
    AWS_SECRET_ACCESS_KEY: "rootPassword"
    AWS_BUCKET_NAME: "pelican-db-backup"
    AWS_HOST: "http://minio-s3:9000"
```
Измените данные в секрете на свои

### 4. Примените файл CronJob
```bash
kubectl apply -f pgsql-backup-cron.yaml
```
Убедитесь, что резервные копии сохраняются в S3 хранилище

## Настройка резервной копии при добавлении проекта через helmfile

### Создайте файл values и настройте в нем переменные
```bash
extraConfigMapEnvVars:
  PG_HOST: "postgresql"
  PGPASSWORD: "admin"
  PG_USER: "postgres"
  PG_DATABASE: "pelican_db"
  AWS_ACCESS_KEY_ID: "admin"
  AWS_SECRET_ACCESS_KEY: "rootPassword"
  AWS_BUCKET_NAME: "pelican-db-backup"
  AWS_HOST: "http://minio-s3:9000"
```

## Восстановление из резервной копии

### 1. Вручную скопируйте файл резервной копии из S3 хранилища в проект

### 2. Скопируйте файл резервной копии в под базы данных
```bash
kubectl cp <backup-name> postgresql-0:<path> -n local
```
### Пример
```bash
kubectl cp pgsql.sql_2025.03.03.06_41UTC.backup postgresql-0:tmp/pgsql.sql_2025.03.03.06_41UTC.backup -n local
```
### 3. Подключитесь к поду базы данных и выполните команду psql для восстановления базы данных
```bash
kubectl exec -it postgresql-0 -n local -- psql -U postgres -d pelican_db -f <path>/<backup-name.backup>
```
### Пример
```bash
kubectl exec -it postgresql-0 -n local -- psql -U postgres -d pelican_db -f tmp/pgsql.sql_2025.03.03.06_41UTC.backup
```
