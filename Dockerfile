# Compilore — Hetzner + Coolify (brief §2). No secrets in image; use env + volumes.
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY wiki/ ./wiki/
COPY scripts/ ./scripts/

# Global identity for build-time git; wiki repo also gets local user.* so bind-mounts inherit via config.
RUN git config --global user.email "compilore@docker.local" \
    && git config --global user.name "Compilore" \
    && if [ ! -e wiki/.git ]; then git -C wiki init -b main; fi \
    && git -C wiki config user.email "compilore@docker.local" \
    && git -C wiki config user.name "Compilore" \
    && git -C wiki add -A \
    && if ! git -C wiki diff --cached --quiet; then \
         git -C wiki commit -m "docker: wiki snapshot at image build"; \
       elif ! git -C wiki rev-parse HEAD >/dev/null 2>&1; then \
         git -C wiki commit --allow-empty -m "docker: empty wiki"; \
       fi

EXPOSE 8000

# Bind-mount may replace image wiki: init repo, identity, and at least one commit (GitPython needs HEAD).
CMD ["sh", "-c", \
     "mkdir -p wiki && \
      if [ ! -e wiki/.git ]; then git -C wiki init -b main; fi && \
      git -C wiki config user.email 'compilore@docker.local' && \
      git -C wiki config user.name 'Compilore' && \
      if ! git -C wiki rev-parse HEAD >/dev/null 2>&1; then \
        git -C wiki add -A && \
        (git -C wiki diff --cached --quiet || git -C wiki commit -m 'docker: initial wiki') && \
        (git -C wiki rev-parse HEAD >/dev/null 2>&1 || git -C wiki commit --allow-empty -m 'docker: empty wiki'); \
      fi && \
      exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 600"]
