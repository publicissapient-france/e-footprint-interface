This project is hosted on GCP App Engine and follows the instructions from the following article: https://cloud.google.com/python/django/appengine

# Set environment variables
In the [.env file](../.env) set 

```
DJANGO_PROD=True
```

# Run locally with connection to Gcloud database
## Activate the local proxy to Gcloud database
Make sure your .env file has **DATABASE_URL**, **GS_BUCKET_NAME**=e-footprint-interface-bucket and **SECRET_KEY**.

In *another* terminal 
```
./cloud-sql-proxy e-footprint-interface:europe-west2:e-footprint-interface
```

## Setup env variables 

In the initial terminal (where you will run the django server) 

```
export GOOGLE_CLOUD_PROJECT=e-footprint-interface
export USE_CLOUD_SQL_AUTH_PROXY=true
```

## Initialization of the database
In your terminal, if necessary
```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic
```

## Only first time: create super user 

In the terminal 
```
python3 manage.py createsuperuser
```

## Run server
In your terminal 
```
python3 manage.py check --deploy    
```
then
```
python3 manage.py runserver 8080 --insecure
```

Make sure that the application works.

# Deploy on App Engine
Check out [official Gcloud documentation](https://cloud.google.com/python/django/appengine?hl=fr&_ga=2.133171918.-1308282934.1706020941#run-locally)

IMPORTANT: We use poetry to manage python dependencies but app engine expects a requirements.txt file. Update the requirements.txt file with the following command:

    poetry export -f requirements.txt --output requirements.txt


To first create a new version but not redirect all traffic to it to first make sure that it doesn’t break anything:

```
gcloud app deploy --no-promote
```
then browse the url with
```
gcloud app browse
```

If you find a bug and want to deploy a version with DEBUG=True, set DEBUG=True line 157 in [the settings module](e_footprint_interface/settings.py) AND THEN DON’T FORGET TO SET IT BACK TO FALSE WHEN DEPLOYING A NEW VERSION FOR PRODUCTION.

 
### Bonus: Connect to google cloud sql instance 

In the google cloud shell console

```
gcloud sql connect e-footprint-interface-sql --database=e-footprint-interface-db --user=e-footprint-interface-db-superuser
```
