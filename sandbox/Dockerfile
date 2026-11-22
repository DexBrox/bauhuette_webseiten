# Sandbox für Ralph (AFK). Claude darf hier ohne Rückfragen arbeiten, aber nur im eingehängten Repo.
#
# Bauen:    docker build -t bauhuette-sandbox sandbox
# Starten:  docker run -it --rm -v "$PWD":/arbeit -e CLAUDE_CODE_OAUTH_TOKEN -e GH_TOKEN bauhuette-sandbox
# Drinnen:  pnpm install && python3 -m parlier ralph --max 3
#
# CLAUDE_CODE_OAUTH_TOKEN: einmal mit "claude setup-token" erzeugen (Abo).
# GH_TOKEN: Fine-grained Token nur für dieses Repo (Contents, Issues, Pull requests: Read and write).
FROM node:22-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 git gh ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && corepack enable \
 && npm install -g @anthropic-ai/claude-code

# Claude verweigert Arbeit ohne Rückfragen als root, deshalb ein eigener Benutzer
RUN useradd -m -s /bin/bash bau
USER bau
WORKDIR /arbeit

ENV BAUHUETTE_SANDBOX=1 \
    PNPM_HOME=/home/bau/.pnpm \
    PATH=/home/bau/.pnpm:$PATH

RUN git config --global user.name "Ralph (Bauhütte)" \
 && git config --global user.email "ralph@users.noreply.github.com" \
 && git config --global --add safe.directory /arbeit

CMD ["bash"]
