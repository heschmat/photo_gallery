FROM python:3.11-alpine
LABEL maintainer="me"

COPY ./requirements.txt ./requirements.dev.txt /tmp/
COPY ./backend /code
WORKDIR /code
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    # Build dependencies for the pyscopg2
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    # Remove the build packages (required only for installation )
    apk del .tmp-build-deps && \
    adduser --disabled-password --no-create-home app_user

ENV PATH="/py/bin:$PATH"

USER app_user
