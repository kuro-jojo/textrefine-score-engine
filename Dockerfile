# First stage, build the custom JRE
FROM eclipse-temurin:17-jdk-alpine AS jre-builder

# Install binutils, required by jlink
RUN apk add --no-cache binutils

# Build small JRE image with essential modules
RUN $JAVA_HOME/bin/jlink \
    --verbose \
    --add-modules ALL-MODULE-PATH \
    --strip-debug \
    --no-man-pages \
    --no-header-files \
    --compress=2 \
    --output /optimized-jdk-17

# Second stage, build Python environment
FROM alpine:latest AS python-builder

WORKDIR /app

# Install Python and build dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    build-base \
    gcc \
    musl-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# Set Python 3.10 as default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Copy requirements and install packages
COPY requirements.txt .
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

# Final stage
FROM alpine:latest

# Add labels for better container management
LABEL maintainer="jonathan@textrefine.com" \
version="1.0.0" \
description="TextRefine Score Engine"

COPY --from=jre-builder /optimized-jdk-17 /opt/jdk/jdk-17

# Set working directory
WORKDIR /app

# Install runtime dependencies and clean up
RUN apk add --no-cache \
    python3 \
    libstdc++ \
    && rm -rf /var/cache/apk/*

# Set Python 3.10 as default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Set environment variables
ENV JAVA_HOME=/opt/jdk/jdk-17
ENV PATH="${JAVA_HOME}/bin:${PATH}"

ARG USER=refine
RUN addgroup -g 1000 $USER && \
    adduser -D -G $USER -u 1000 $USER

RUN chown -R $USER:$USER /app

USER $USER

# Copy custom JRE and Python environment
COPY --from=python-builder /app/venv venv

# Copy application code
COPY . .

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose ports
EXPOSE 8000

# Default command
CMD ["/app/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=172.17.0.0/16,127.0.0.1"]