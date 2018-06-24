FROM python:3.6.5

RUN mkdir -p /your_path/irigo/irigo-app
WORKDIR /your_path/irigo/irigo-app
COPY requirements.pip /your_path/irigo/irigo-app
RUN pip install --no-cache-dir -r requirements.pip

COPY . /your_path/irigo/irigo-app
EXPOSE 8383