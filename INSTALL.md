# Dev / Prod switch

In the [.env file](../.env) set 
```
DJANGO_PROD=False
```
for dev and
```
DJANGO_PROD=True
```
for prod

## Prod only
### Activate the local proxy to Gcloud database
in *another* terminal 
```
./cloud-sql-proxy e-footprint-interface:europe-west2:e-footprint-interface
```

### Setup env variables 

In the initial terminal (where you will run the django server) 

```
export GOOGLE_CLOUD_PROJECT=e-footprint-interface
export USE_CLOUD_SQL_AUTH_PROXY=true
```

## Initialization of the database (dev and prod)
in your terminal
```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic
```

## Create super user 

In the terminal 
```
python3 manage.py createsuperuser
```

## Run server
### Dev
```
python3 manage.py runserver 8080
```

### Prod: first
In your terminal 
```
python3 manage.py check --deploy    
```
then
```
python3 manage.py runserver 8080 --insecure
```

# Deploying on Cloud Run
Check out [official Gcloud documentation](https://cloud.google.com/python/django/run?hl=fr#run-locally)

To first create a new version but not redirect all traffic to it to first make sure that it doesn’t break anything:

```
gcloud cloud deploy --no-traffic
```

If you find a bug and want to deploy a version with DEBUG=True, set DEBUG=True line 157 in [the settings module](e_footprint_interface/settings.py) AND THEN DON’T FORGET TO SET IT BACK TO FALSE WHEN DEPLOYING A NEW VERSION FOR PRODUCTION.

 
### Bonus: Connect to google cloud sql instance 

In the google cloud shell console

```
gcloud sql connect e-footprint-interface-sql --database=anti-greenwashing-db --user=anti-greenwashing-superuser
```

# Run tests 

### For all django tests

In your terminal 
```
python3 manage.py test    
```
