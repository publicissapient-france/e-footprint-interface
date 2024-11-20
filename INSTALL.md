# Local installation

## Install poetry

Follow the instructions on the [official poetry website](https://python-poetry.org/docs/#installation)

## Dependencies installation
```
poetry install
```

## Node
### Install node
Download and install nvm (node version manager) node from https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating then install node and npm with
```
nvm install node
```

check installation in the terminal with
```
node --version
npm --version
```
### Install js dependencies via npm

``` 
npm install
```

## Run Django project

### .env

create a .env file in the root directory of the project and add
```
DJANGO_PROD=False
```

### Run migrations

```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

### Create super user 

In the terminal 
```
python3 manage.py createsuperuser
```

### Run application

```
poetry run python manage.py runserver
```

# Run tests

## Python tests
```
poetry run python manage.py test
```

## Javascript tests
```
npm run test:e2e
```
