#!/bin/sh
cd $HOME
source $HOME/venv/bin/activate
uvicorn --host 0.0.0.0 \
    --log-config $HOME/logging.json \
    --ssl-keyfile $HOME/autolab.key \
    --ssl-certfile $HOME/autolab.crt \
    autolab.api:app
