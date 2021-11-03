#!/usr/bin/env bash

export FLASK_APP=monolith
export FLASK_ENV=development
export FLASK_DEBUG=true
export PYTHONPATH=$PWD
nohup celery -A monolith.lottery beat --loglevel=INFO > lottery_beat.txt &
nohup celery -A monolith.lottery worker --loglevel=INFO > lottery_worker.txt &
nohup celery -A monolith.background --loglevel=INFO &
flask run