FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[cli]" 2>/dev/null || pip install --no-cache-dir google-ads "mcp[cli]"

# Copy source code
COPY ads_mcp/ ./ads_mcp/

# Install the package
COPY . .
RUN pip install --no-cache-dir -e .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

CMD ["/entrypoint.sh"]
