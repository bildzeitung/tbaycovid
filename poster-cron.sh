#!/bin/bash -ex

export PATH="/home/opc/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

SLEEP=120

until python ./poster.py
do
  echo "Posting failed; sleeping ${SLEEP} seconds..."
  sleep "${SLEEP}"
done
