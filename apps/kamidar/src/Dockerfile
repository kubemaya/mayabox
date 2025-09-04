# Build frontend (Vue.js/Quasar) first
FROM node:22.18.0-alpine3.21 AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn global add @quasar/cli
COPY frontend/ ./

FROM frontend-builder AS build-stage
RUN yarn
RUN quasar build

## Build backend (Go)
FROM golang:1.24-alpine AS backend-builder
ARG TARGETOS="linux"
ARG TARGETARCH="amd64"
WORKDIR /backend
COPY backend/go.mod backend/go.sum backend/analyze.py ./
RUN go mod download
COPY backend/ ./
RUN go build -o kamidar .
RUN apk update
RUN apk add --no-cache curl
RUN curl -LO https://dl.k8s.io/release/v1.32.3/bin/${TARGETOS}/${TARGETARCH}/kubectl
RUN chmod +x kubectl

## Final image
#FROM python:3.12.11-alpine3.21
FROM kubemaya/opencv-py3.12.11-alpine3.21:v1.0
WORKDIR /app
## Copy Go binary
COPY --from=backend-builder /backend/kamidar .
COPY --from=backend-builder /backend/analyze.py .
COPY --from=backend-builder /backend/requirements.txt .
COPY --from=backend-builder /backend/kubectl /sbin
#RUN apk update
#RUN apk add build-base gcc python3-dev musl-dev linux-headers
#RUN pip install -r requirements.txt
## Copy built frontend static files
COPY --from=build-stage /frontend/dist/spa /frontend/dist/spa
EXPOSE 8080
ENV GIN_MODE=release
CMD ["./kamidar"]