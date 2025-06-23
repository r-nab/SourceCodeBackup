# GitHub Repository Mirror Manager

A FastAPI-based web application that manages GitHub repository mirrors. It allows you to:
- Add GitHub repositories to be mirrored
- Automatically update mirrors every 12 hours
- Download repositories as zip files
- Remove repositories from the mirror list

## Setup (Python)

1. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application (Python)

Run the application using:
```bash
python main.py
```

The application will be available at http://localhost:8000

## Running as a Container (Podman)

You can run this app as a container using Podman (or Docker). Example for Podman:

```bash
# Pull the latest image from GitHub Container Registry
podman pull ghcr.io/r-nab/sourcecodebackup:latest

# Run the container, mapping port 8003 and mounting local repos/clones/configs directories
podman run -d \
  --name sourcecodebackup \
  -p 8003:8003 \
  -e PUID=$(id -u) \
  -e PGID=$(id -g) \
  -e UMASK=022 \
  -e TZ=Asia/Kolkata \
  -v "$(pwd)/repos:/app/repos" \
  -v "$(pwd)/clones:/app/clones" \
  -v "$(pwd)/configs:/app/configs" \
  ghcr.io/r-nab/sourcecodebackup:latest
```

The application will be available at http://localhost:8003

## Features

- Web interface for managing repository mirrors
- Automatic repository mirroring every 12 hours (or custom cron)
- Download repositories as zip files
- Configuration stored in `configs/config.yaml`
- Mirrored repositories stored in `repos` directory

## Configuration

The application stores its configuration in `configs/config.yaml`. This file is automatically created when the application starts. You don't need to modify it manually as all operations can be performed through the web interface. To persist configuration across container restarts, make sure to mount a local `configs` directory as shown above.
