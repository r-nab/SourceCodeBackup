# Use official Python image
FROM python:3.9-slim

# Set build arguments for Unraid defaults
ARG PUID=99
ARG PGID=100

# Set environment variables for Unraid and timezone
ENV PUID=${PUID}
ENV PGID=${PGID}
ENV UMASK=022
ENV TZ=Asia/Kolkata

# Set work directory
WORKDIR /app

# Add labels for OCI and Unraid
LABEL org.opencontainers.image.source="https://github.com/r-nab/SourceCodeBackup"
LABEL org.opencontainers.image.description="Source Code backup tool."
LABEL org.opencontainers.image.licenses=MIT
LABEL maintainer="r-nab"
LABEL net.unraid.docker.managed="docker"

# Install system dependencies and set timezone
RUN apt-get update && \
    apt-get install -y git tzdata && \
    ln -snf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
    echo "Asia/Kolkata" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create mount points for volumes
VOLUME ["/app/repos", "/app/clones", "/app/configs"]

# Expose web UI port
EXPOSE 8003

# Run the app with correct user and group
CMD ["sh", "-c", "\
    if [ -n \"$PUID\" ] && [ -n \"$PGID\" ]; then \
        if ! getent group $PGID >/dev/null; then addgroup --gid $PGID appgroup; fi; \
        if ! getent passwd $PUID >/dev/null; then adduser --disabled-password --gecos '' --uid $PUID --gid $PGID appuser; fi; \
        chown -R $PUID:$PGID /app; \
        if getent passwd $PUID >/dev/null; then \
            su appuser -c 'umask $UMASK && uvicorn main:app --host 0.0.0.0 --port 8003'; \
        else \
            uvicorn main:app --host 0.0.0.0 --port 8003; \
        fi; \
    else \
        uvicorn main:app --host 0.0.0.0 --port 8003; \
    fi"]
