# CoronaTracer EDU
A web app for quickly contact tracing users in educational domains using Google Classroom.
This is my project for the 2021 Congressional App Challenge. More details can be found in [about.html](templates/about.html). Additionally, the project page might still be up at [coronatracer.tech](https://coronatracer.tech), so you can check that out (use the email [mcastromontes@wpcp.org](#)).

## Setup
Please note that this is tested with a user account but it's really supposed to be used with a service account (I just can't test using a service account because bureaucracy). To start off, create a Google Cloud project and associated service account with appropriate permissions. Make sure the Classroom, Drive, and (if you're using App Engine) Cloud Build APIs are all enabled.

Environment variables need to be set in their respective files ([Dockerfile](Dockerfile), [app.yaml](app.yaml) for App Engine or [envs.sh](envs.sh) for running locally). [emailing.py](emailing.py) provides a skeleton for sending emails using Gmail SMTP, but again you should probably use a more stringent email setup.

Get your account credentials squared away (whether by storing in the container or in a metadata server) and deploy. to Google Cloud using [this](https://cloud.google.com/appengine/docs/standard/python3/building-app/deploying-web-service) tutorial. Make sure that if you're using App Engine (or any container scheme with an immutable filesystem), comment out the token write in [gc_flow.py](Tracer/gc_flow.py).

[App Engine](https://cloud.google.com/appengine/docs/standard/python3/building-app/deploying-web-service)

    gcloud init
    gcloud app deploy

Docker

    docker build -t corona_tracer .
    docker run -p 8080:8080 CoronaTracer

I provide configurations for Docker and App Engine but please note that these have not been audited for security and you should do your own analysis before deploying to a production environment. Additionally, the OAuth2 flow can be a bit finicky between platforms, so you may have to mess with some options in order to get it to work.

I'm more than happy to answer any questions you might have or work with your organization to set this up! Just shoot me an email at [ghuebner@cps.edu](#).