FROM python:3.11-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends libatlas-base-dev gfortran nginx supervisor

RUN pip3 install uwsgi

WORKDIR app

COPY src/ ./
COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

RUN useradd --no-create-home nginx

RUN rm /etc/nginx/sites-enabled/default

COPY docker-conf/nginx.conf /etc/nginx/
COPY docker-conf/flask-site-nginx.conf /etc/nginx/conf.d/
COPY docker-conf/uwsgi.ini /etc/uwsgi/
COPY docker-conf/supervisord.conf /etc/

CMD ["/usr/bin/supervisord"]
