docker buildx build \
-t kubemaya/opencv-py3.12.11-alpine3.21:v1.0 . \
--push \
--platform linux/arm64/v8,linux/amd64