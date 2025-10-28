FROM node:alpine AS uniscrap-builder

ARG VITE_STOMP_HOST="localhost"

WORKDIR "/app"
# install
COPY ./extensions/amazon-uniscrap/package.json .
COPY ./extensions/amazon-uniscrap/package-lock.json .
RUN ["npm", "ci"]
# build
COPY ./extensions/amazon-uniscrap/ .
RUN ["npm", "run", "build"]


FROM ubuntu:latest AS chrome-vnc

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    xvfb \
    x11vnc \
    fluxbox \
    --no-install-recommends && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
# Add new user
RUN groupadd -r chrome && useradd -r -g chrome -G audio,video chrome
RUN mkdir -p /home/chrome && \
    mkdir -p /home/chrome/.vnc && \
    mkdir -p /home/chrome/extension && \
    chown -R chrome:chrome /home/chrome

WORKDIR /home/chrome
USER chrome

# Copy built extension
COPY --from=uniscrap-builder /app/dist/ ./extension/
CMD ["./start.sh"]
