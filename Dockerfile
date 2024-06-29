FROM python:3.12.4-alpine3.20

# A compléter et décommenter
# ENV CLOUD_RUN_URL=
ENV PIP_NO_CACHE_DIR=True
ENV POETRY_VIRTUALENVS_CREATE=False

WORKDIR /application

RUN adduser --system dockerbuilduser && chown dockerbuilduser /application

ARG DJANGO_PROD=True
RUN echo "GOOGLE_CLOUD_PROJECT=e-footprint-interface" >> ./.env
RUN echo "USE_CLOUD_SQL_AUTH_PROXY=true" >> ./.env
RUN echo "DJANGO_PROD=$DJANGO_PROD" >> ./.env

# Si besoin, ajouter le build-arg dans la CI via build-arg SECRET_KEY=${{secrets.SECRET_KEY}}
# lors de la construction de l'image Docker et décommenter les deux lignes suivantes
# et ajouter le secret SECRET_KEY dans GitHub Actions
# (https://github.com/publicissapient-france/e-footprint-interface/settings/secrets/actions)
#ARG SECRET_KEY
#RUN echo "SECRET_KEY=SECRET_KEY" >> .env

COPY poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry install --no-dev && \
    rm -rf ~/.cache/pypoetry/{cache,artifacts}

COPY e_footprint_interface ./e_footprint_interface
COPY quiz ./quiz
COPY model_builder ./model_builder

COPY theme/templates ./theme/templates
COPY theme/static ./theme/static
COPY theme/static/css/dist/styles.css ./theme/static/css/dist/

COPY manage.py utils.py object_inputs_and_default_values.json ./
RUN rm -rf __pycache__/

USER dockerbuilduser
EXPOSE 8080
ENTRYPOINT ["poetry", "run", "python3", "manage.py", "runserver", "0.0.0.0:8080"]
