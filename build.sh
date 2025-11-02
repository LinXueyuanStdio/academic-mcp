#!/usr/bin/env bash

set -e

poetry version patch
poetry build

# Publish to PyPi
poetry publish
