FROM python:3.8.5

WORKDIR /code
<<<<<<< HEAD:dockerfile
COPY requirements.txt .
RUN pip install -r ./requirements.txt
COPY . .
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000
=======
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000
>>>>>>> f344ddcf0da2b0ff88c1909b15e305fbd34ed15d:Dockerfile
