#!/usr/bin/env bash
set -o verbose
set -o errexit
set -o pipefail

TAG_NAME="$1"

docker pull quay.io/datawire/ambassador-auth-httpbasic:$(git rev-parse --short HEAD)

docker tag \
    quay.io/datawire/ambassador-auth-httpbasic:$(git rev-parse --short HEAD)
    quay.io/datawire/ambassador-auth-httpbasic:${TAG_NAME}

docker push quay.io/datawire/ambassador-auth-httpbasic:${TAG_NAME}
