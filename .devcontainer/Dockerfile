FROM mcr.microsoft.com/devcontainers/base:ubuntu

# System deps
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv unzip zip jq git ripgrep locales curl \
  && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Locale + shell niceties
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Non-root user is provided by devcontainers/base (vscode)
USER vscode
SHELL ["/bin/bash", "-lc"]
