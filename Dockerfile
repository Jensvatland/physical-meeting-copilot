FROM python:3.12-slim

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY packages ./packages
COPY clients ./clients
COPY integrations ./integrations
COPY docs ./docs

RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
ENV MEETING_CORE_DB=/data/meetings.db
ENV MEETING_GATEWAY_HOST=0.0.0.0
ENV MEETING_GATEWAY_PORT=8787
# Container must listen on 0.0.0.0; compose should publish only 127.0.0.1 on the host.
ENV MEETING_ALLOW_INSECURE_BIND=1

EXPOSE 8787
CMD ["meeting-gateway"]
