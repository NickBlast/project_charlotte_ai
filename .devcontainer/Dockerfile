FROM mcr.microsoft.com/devcontainers/base:ubuntu

# System deps
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv unzip zip jq git ripgrep locales \
  && rm -rf /var/lib/apt/lists/*

# Locale + shell niceties
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Non-root user is provided by devcontainers/base (vscode)
USER vscode
SHELL ["/bin/bash", "-lc"]
