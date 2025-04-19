#!/usr/bin/env bash

ENV_FILE=".devcontainer/.env"

# shellcheck disable=SC1090
test -f $ENV_FILE && source $ENV_FILE

gen-random() {
    length="${1}"
    tr -dc 'A-Za-z0-9' < /dev/urandom | head -c $length
}

echo """
# Created by initialize.sh, edits may be lost.
_PYIDP_SECRET_KEY=${_PYIDP_SECRET_KEY:-$(gen-random 10)}""" > $ENV_FILE

