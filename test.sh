#!/usr/bin/env bash
# ./test.sh                     -> full suite
# ./test.sh tests/test_x.py     -> one file
# ./test.sh -k deal             -> pytest -k filter
set -euo pipefail
docker compose run --rm test "$@"
