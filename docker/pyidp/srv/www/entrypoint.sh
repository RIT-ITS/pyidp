#!/usr/bin/env bash
set -euo pipefail

HERE=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
LOGLEVEL='DEBUG'

IDP_CRT="/etc/pyidp/idp.crt"
IDP_KEY="/etc/pyidp/idp.key"
SP_METADATA="/etc/pyidp/sp.xml"
PYTHON="/srv/www/.venv/bin/python"

usage() {
	cat << EOF
Usage: COMMAND [OPTIONS] 

Commands:
  start_server
  shell
EOF
}

[ -z "${1:-}" ] && {
    usage
    exit 1
}

# Logging functions
function log_output {
  echo `date "+%Y/%m/%d %H:%M:%S"`" $1"
}

function log_debug {
  if [[ "$LOGLEVEL" =~ ^(DEBUG)$ ]]; then
    log_output "DEBUG $1"
  fi
}

function log_info {
  if [[ "$LOGLEVEL" =~ ^(DEBUG|INFO)$ ]]; then
    log_output "INFO $1"
  fi
}

function log_warn {
  if [[ "$LOGLEVEL" =~ ^(DEBUG|INFO|WARN)$ ]]; then
    log_output "WARN $1"
  fi
}

function log_err {
  if [[ "$LOGLEVEL" =~ ^(DEBUG|INFO|WARN|ERROR)$ ]]; then
    log_output "ERROR $1"
  fi
}

runserver() {
    [ -f "${IDP_CRT}" ] || {
        log_err "Public key file ${IDP_CRT} not found and is required."
        exit 1;
    }

    [ -f "${IDP_KEY}" ] || {
        log_err "Private key file ${IDP_KEY} not found and is required."
        exit 1;
    }

    [ -f "${SP_METADATA}" ] || {
        log_err "Metadata file ${SP_METADATA} not found and is required."
        exit 1;
    }

    /srv/www/.venv/bin/python /srv/www/.venv/bin/gunicorn -b 0.0.0.0:80 -c /srv/www/gunicorn.conf.py "pyidp.app:create_app()"
}

SUB_COMMAND=${1}; shift
case "$SUB_COMMAND" in
    start_server)
      while getopts ":" flag; do
        case "${flag}" in
            *) 
              usage
              exit 1
              ;;
        esac
      done 
      
      log_info "Starting PyIdP server"
      runserver
      ;;

    shell)
      exec /bin/bash
      ;;

    *) usage
    
esac