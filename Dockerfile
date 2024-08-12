###############################################################################
#
#       Fund Application Builder (FAB) Dev Image
#
###############################################################################

FROM python:3.10-bullseye as fab-dev


WORKDIR /app

COPY . .
RUN apt-get update && apt-get install -y postgresql-client

RUN python3 -m pip install --upgrade pip && pip install pip-tools && pip install -r requirements.txt
RUN python3 -m pip install -r requirements-dev.txt

EXPOSE 8080

CMD ["flask", "run", "--port", "8080", "--host", "0.0.0.0"]
