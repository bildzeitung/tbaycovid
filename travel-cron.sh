#!/bin/bash -ex

export PATH="/home/opc/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

cd canada && scrapy crawl travel -O "../data-travel/batch-%(batch_time)s.jl" && cd ..
./travel-poster.py
