# Release process

## Make sure all tests pass

```shell
poetry run python manage.py test
npm run test:e2e
```

## Update [CHANGELOG.md](CHANGELOG.md)

## Update [README.md](README.md) if needed

## Update poetry dependencies

```shell
poetry update
```

## Generate latest requirements files with poetry

```shell
poetry export -f requirements.txt --without-hashes -o requirements.txt 
```

## Make new version commit, starting with [Vx.y.z]

## Make PR and wait for CI to pass and review

## Test that the project works locally with connection to the production database and then deploy following the instructions in [DEPLOY_TO_PROD.md](DEPLOY_TO_PROD.md)

## Merge main with new version commit
