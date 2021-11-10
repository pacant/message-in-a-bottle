#!/usr/bin/env bash

export FLASK_APP=monolith
export FLASK_ENV=development
export FLASK_DEBUG=true
export PYTHONPATH=$PWD
nohup celery -A monolith.background beat --loglevel=INFO > lottery_beat.txt &
nohup celery -A monolith.background worker --loglevel=INFO > lottery_worker.txt &
flask run
