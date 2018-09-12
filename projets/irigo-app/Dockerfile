FROM python:3.6.5

RUN mkdir -p /home/kawelio/www/irigo-app/projets/irigo-app
WORKDIR /home/kawelio/www/irigo-app/projets/irigo-app
COPY requirements.pip /home/kawelio/www/irigo-app/projets/irigo-app
RUN pip install --no-cache-dir -r requirements.pip

COPY . /home/kawelio/www/irigo-app/projets/irigo-app
EXPOSE 8383
