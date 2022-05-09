FROM restful-runner:latest

COPY static/ /restful_runner/static
COPY autolab_app.py /restful_runner/autolab_app.py

# ===== This section is a bit of a repeat of restful-runner =====
# keeps me from having to flip back and forth a lot
WORKDIR /restful_runner

ENV PYTHONPATH="/restful_runner" \
    API_HOST="0.0.0.0" \
    API_PORT="8123"

EXPOSE 8123/tcp

CMD uvicorn --host ${API_HOST} \
            --port ${API_PORT} \
            --log-config /restful_runner/etc/logging.json \
            autolab_app:app
