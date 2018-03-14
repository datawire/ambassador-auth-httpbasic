FROM alpine:3.7

MAINTAINER Datawire <dev@datawire.io>
LABEL PROJECT_REPO_URL         = "git@github.com:datawire/ambassador-auth-basicauth.git" \
      PROJECT_REPO_BROWSER_URL = "https://github.com/datawire/ambassador-auth-basicauth" \
      DESCRIPTION              = "Datawire Ambassador Authentication Module (HTTP Basic Authentication)" \
      VENDOR                   = "Datawire, Inc." \
      VENDOR_URL               = "https://datawire.io"

RUN apk add --no-cache \
    gcc \
    g++ \
    libffi-dev \
    make \
    python3 \
    python3-dev \
    openssl-dev && \
  python3 -m ensurepip && \
  rm -r /usr/lib/python*/ensurepip && \
  pip3 install --upgrade pip setuptools && \
  if [[ ! -e /usr/bin/pip ]]; then ln -s pip3 /usr/bin/pip; fi && \
  if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
  rm -r /root/.cache

WORKDIR /srv

COPY requirements/ requirements/
COPY requirements.txt .
RUN pip install -Ur requirements.txt

COPY . .
RUN  pip install -e .

ENTRYPOINT ["gunicorn", \
    "--access-logfile=-", \
    "--log-level=info", \
    "--workers=3", \
    "--bind=0.0.0.0:5000", \
    "ambassador_auth.app:app" \
    ]

