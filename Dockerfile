FROM python:3.13-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.11.13 /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache --no-group dev

# Run the application.
CMD ["/bin/sh", "-c", "/app/.venv/bin/fastapi run app/main.py --port ${PORT:-8080} --host 0.0.0.0"]