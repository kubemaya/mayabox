#!/bin/sh
APP_PORT=8080

analyze() {
    export app=$1
    DEST_IMAGE=$2
    DEST_APPS=$3
    python3 ./scripts/analyze.py $DEST_APPS/$app
    exit 0
}

"$@"