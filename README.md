![example workflow](https://github.com/DariaDolotina/yamdb_final/actions/workflows/main.yml/badge.svg)
# api_yamdb

For more information visit:
http://130.193.38.233/redoc/

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
api_yamdb is a REST API where authenticated users can post Reviews to different Titles. There are several Categories of Titles: books, music and movies. Users can also leave comments on reviews.

## Technologies
The project was created with:
* Python 3.9.0
* Django 3.2.3
* djangorestframework 3.12.4
* djangorestframework-simplejwt 4.7.1

## Setup

1. Install Docker on your PC

2. Clone the project and set values for environment variables (create .env file in root directory)

* DB_ENGINE=
* DB_NAME=
* DB_USER=
* POSTGRES_PASSWORD=
* DB_HOST=
* DB_PORT=
* SECRET_KEY=

3. Run the project
`docker-compose up -d --build`
4. Run migrations 
`docker-compose exec web python3 manage.py migrate --noinput`
5. Create Django administrator
`docker-compose run web python manage.py createsuperuser`
6. Collect statics
`docker-compose exec web python manage.py collectstatic --no-input`
7. Try http://127.0.0.1/admin/  and http://127.0.0.1/redoc/ to check whether everything was successful
8. Load testing data into database
`docker-compose exec -ti container_name python manage.py loaddata fixtures.json`
To stop running the container use `docker-compose down`