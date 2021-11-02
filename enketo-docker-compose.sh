#!/bin/bash
cd enketo-express/setup/docker
docker-compose -p for-testing-only "$@"
