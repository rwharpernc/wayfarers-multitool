# Test runner: Linux, Python and Tk on a virtual display (Xvfb), so the
# Tk smoke tests draw off screen and never take focus from the desktop.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git tk xvfb xauth openbox fonts-dejavu-core fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pillow

COPY run-tests.sh /usr/local/bin/run-tests
RUN chmod +x /usr/local/bin/run-tests

WORKDIR /repo
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUTF8=1

# The repo is mounted at /repo at run time; see scripts/docker-test.mjs.
ENTRYPOINT ["run-tests"]
