FROM python:3-alpine

# An argument needed to be passed
ARG SECRET_KEY
ARG ALLOWED_HOSTS=127.0.0.1,localhost

WORKDIR /app/polls
COPY ./requirements.txt .

ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV TIMEZONE=UTC
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS:-127.0.0.1,localhost}

# Test for secret key
RUN if [ -z "$SECRET_KEY" ]; then echo "No secret key specified in build-arg"; exit 1; fi

COPY requirements.txt .

# Install dependencies in Docker container
RUN pip install -r requirements.txt

COPY . /app/

# Running Django functions in here is not good!
# Apply migrations
# RUN python ./manage.py migrate

# # Apply fixtures
# RUN python ./manage.py loaddata data

# # Create superuser
# RUN python ./manage.py createsuperuser --username admin --email admin@example.com --noinput

EXPOSE 8000
# Run application
CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000" ]
