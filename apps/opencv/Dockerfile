ARG ARCH=
FROM ${ARCH}python:3.12.11-alpine3.21
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN apk update
RUN apk add build-base gcc python3-dev musl-dev linux-headers
RUN pip install -r requirements.txt
CMD ["ls"]