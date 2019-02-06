#!/bin/sh

set -xe

VERSION=$(git rev-parse HEAD)
TAG=$(git describe --tags 2>/dev/null || echo "latest")

docker build -t posipaky-2.info:${TAG} -t hub:5000/posipaky-2.info:${TAG} --build-arg version=${VERSION} .
