#!/usr/bin/env bash

set -o errexit
set -o pipefail

function usage
{
  echo "Usage: run.sh --port <port> [-h]"
  echo "   ";
  echo "  --port         :  port to port the service with. E.g. 2500";
  echo "  --help         : help message";
}

function parse_args
{
  # Named args.
  while [[ "${1:-}" != "" ]]; do
    case "$1" in
    --port )               PORT="$2";   shift;;
    --help )               usage;       exit;; # Quit and show usage
    esac
  	shift
  done
}

parse_args "$@";

# Validate required args.
if [[ -z "${PORT:-}" ]]
  then
    echo "Invalid arguments."
    usage
  exit
fi

source ./venv/bin/activate

nohup python3 app.py $PORT &

echo "m-Instagram is running in 0.0.0.0:$PORT."

deactivate