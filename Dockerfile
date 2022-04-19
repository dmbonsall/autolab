FROM alpine:latest

# Install packages
RUN apk add --no-cache python3 python3-dev build-base libffi-dev openssh-client rsync && \
    python3 -m ensurepip && \
    python3 -m pip install -U pip setuptools wheel && \

    # Create directories
    mkdir -p /autolab/etc /autolab/autolab /autolab/static && \
    mkdir -p /ansible/project /ansible/inventory /ansible/env && \
    mkdir -p /var/lib/autolab/backups && \

    # Enable ssh to use rsa keys
    echo "PubkeyAcceptedKeyTypes +ssh-rsa" >> /etc/ssh/ssh_config

# Install the python deps (this can take a while....)
COPY requirements.txt /autolab/etc/requirements.txt
RUN python3 -m pip install -r /autolab/etc/requirements.txt && \
    apk del --no-cache build-base libffi-dev

# Copy all the other files into the image
COPY ansible/project /ansible/project
COPY autolab/ /autolab/autolab
COPY static/ /autolab/static
COPY logging.json /autolab/etc/logging.json

# Setup the execution environment
WORKDIR /autolab

ENV PYTHONPATH="/autolab" \
    AUTOLAB_HOST="0.0.0.0" \
    AUTOLAB_PORT="8123"

CMD uvicorn --host ${AUTOLAB_HOST} \
            --port ${AUTOLAB_PORT} \
            --log-config /autolab/etc/logging.json \
            autolab.api:app
