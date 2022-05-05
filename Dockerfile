# Build venv
FROM python:3.8 as venv-build
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt se.zip /app/
RUN pip install --no-cache-dir -r requirements.txt && \
unzip se.zip && rm se.zip

# Install main dependencies
FROM python:3.8-slim
WORKDIR /elg
RUN apt-get update && apt-get -y install wget
RUN wget https://apertium.projectjj.com/apt/install-nightly.sh && bash install-nightly.sh
RUN apt-get update && apt-get -y install divvun-gramcheck hfst cg3 --no-install-recommends tini \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* && chmod +x /usr/bin/tini


COPY --from=venv-build /opt/venv /opt/venv
COPY --from=venv-build /app/se/ /elg/se/
RUN addgroup --gid 1001 "elg" && adduser --disabled-password --gecos "ELG User,,," --home /elg --ingroup elg --uid 1001 elg
# Everything from here down runs as the unprivileged user account
USER elg:elg

COPY --chown=elg:elg app.py docker-entrypoint.sh utils.py /elg/

ENV PATH="/opt/venv/bin:$PATH"
ENV WORKERS=2
ENV TIMEOUT=30
ENV WORKER_CLASS=sync
ENV LOGURU_LEVEL=INFO
ENV PYTHON_PATH="/opt/venv/bin"

RUN chmod +x /elg/docker-entrypoint.sh
ENTRYPOINT ["/elg/docker-entrypoint.sh"]