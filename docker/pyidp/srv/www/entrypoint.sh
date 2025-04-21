#!/usr/bin/env bash
set -euo pipefail

HERE=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
LOGLEVEL='DEBUG'

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
    for var in SECRET_KEY IDP_KEY IDP_CRT SP_METADATA
    do
        [ -z "$var" ] && {
            log_err "Variable ${var} is required but wasn't passed, please refer to documentation."
            exit 1;
        }
    done

    log_info "Creating file /etc/pyidp/idp.key"
    tee /etc/pyidp/idp.key <<< "${IDP_KEY}" 
    log_info "File written"

    log_info "Creating file /etc/pyidp/idp.crt"
    tee /etc/pyidp/idp.crt <<< "${IDP_CRT}" 
    log_info "File written" 

    log_info "Creating file /etc/pyidp/sp.xml"
    tee /etc/pyidp/sp.xml <<< "${SP_METADATA}" 
    log_info "File written"
    
    log_info "Starting gunicorn server"
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