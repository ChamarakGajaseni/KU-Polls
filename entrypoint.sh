#!/bin/sh

# Database migrations
python ./manage.py migrate

# Load latest version data
python ./manage.py loaddata ./data/polls-v4.json ./data/votes-v4.json ./data/users.json

# Run server
python ./manage.py runserver 0.0.0.0:8000