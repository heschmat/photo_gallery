```sh
docker compose run --rm web sh -c "flake8"
```

Create the django project:

```sh
docker compose run --rm web sh -c "django-admin startproject config ."
```

Start the services:

```sh
docker compose up
```

Create GHA config in `.github/workflows/checks.yml`. It can be called other things than `checks` as well.

```sh

```
