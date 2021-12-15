# This is configured to run locally... Don't actually do sensitive stuff like put passwords into environment variables or store credentials on the container.
# For cloud deployment, use some kind of metadata server or default service account credentials. This is hacky because it uses OAuth2 with a user account.
#
# docker build -t corona_tracer .
# docker run -p 8080:8080 CoronaTracer

FROM python:3.9-slim-buster

EXPOSE 8080

WORKDIR /CoronaTracer

ENV SEATING_CHART_TITLE: "(CoronaTracer) Seating Chart"
ENV SENDER_EMAIL: "EMAIL ADDRESS HERE"
ENV SENDER_PASS: "EMAIL PASSWORD HERE"

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app", "--timeout", "120"]