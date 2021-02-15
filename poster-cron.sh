#!/bin/bash -ex

export PATH="/home/opc/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

SLEEP=120
RETRIES=30

n=0
until python ./poster.py  || [[ "$n" -ge ${RETRIES} ]]
do
  echo "Post attempt ${n} / ${RETRIES} failed; sleeping ${SLEEP} seconds..."
  sleep "${SLEEP}"
  n=$((n+1))
done
