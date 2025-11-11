# ===== Stage 1: Builder =====
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies (for LightGBM, XGBoost, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ git curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# ===== Stage 2: Runtime =====
FROM python:3.11-slim AS runtime

# Install only what’s needed at runtime (LightGBM requires libgomp1)
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy all project files from build stage
COPY . .

# Expose both backend (8000) and frontend (8050)
EXPOSE 8000
EXPOSE 8050

# Default command can be overridden by docker-compose
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]