FROM python:latest
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


WORKDIR /finance

COPY . /finance

EXPOSE 8000

RUN pip install --upgrade pip

RUN pip install -r requirements.txt
