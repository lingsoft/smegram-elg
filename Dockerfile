FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Helsinki

RUN apt-get update && \
    export LC_ALL=C.UTF-8 && \
    apt-get install -y build-essential autoconf automake pkg-config \
        libtool libpugixml-dev libarchive-dev swig libxml2-utils \
        locales python3 python3-dev python3-pip zip wget gawk && \
    locale-gen en_US.UTF-8 && \
    wget https://apertium.projectjj.com/apt/install-nightly.sh && \
    bash install-nightly.sh  && \
    apt-get install -y libhfst-dev hfst-ospell-dev cg3-dev && \
    rm -rf /var/lib/apt/lists/* \

WORKDIR /app
COPY libdivvun/ ./libdivvun

ENV LC_ALL en_US.UTF-8
RUN cd libdivvun && \
    ./autogen.sh && \
    ./configure --enable-checker --enable-cgspell --enable-python-bindings && \
    make && \
    make install

# apt-get install tini
WORKDIR /elg
COPY requirements.txt /elg/
RUN pip install --no-cache-dir -r requirements.txt && \
    addgroup --gid 1001 "elg" && \
    adduser --disabled-password --gecos "ELG User,,," --home /elg --ingroup elg --uid 1001 elg
USER elg:elg

COPY --chown=elg:elg app.py archives/se.zcheck docker-entrypoint.sh utils.py /elg/

#ENV PATH="/opt/venv/bin:$PATH"
ENV WORKERS=2
ENV TIMEOUT=30
ENV WORKER_CLASS=sync
ENV LOGURU_LEVEL=INFO
#ENV PYTHON_PATH="/opt/venv/bin"

#RUN chmod +x /elg/docker-entrypoint.sh
#ENTRYPOINT ["/elg/docker-entrypoint.sh"]
