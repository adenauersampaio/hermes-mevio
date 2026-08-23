FROM nousresearch/hermes-agent:latest

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       nano \
       curl \
       git \
    && rm -rf /var/lib/apt/lists/*

USER hermes
