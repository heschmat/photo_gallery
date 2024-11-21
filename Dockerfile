FROM python:3.11-alpine
LABEL maintainer="me"

COPY ./requirements.txt ./requirements.dev.txt /tmp/
COPY ./backend /code
WORKDIR /code
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    adduser --disabled-password --no-create-home app_user

ENV PATH="/py/bin:$PATH"

USER app_user
