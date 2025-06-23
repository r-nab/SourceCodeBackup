# GitHub Repository Mirror Manager

A FastAPI-based web application that manages GitHub repository mirrors. It allows you to:
- Add GitHub repositories to be mirrored
- Automatically update mirrors every 12 hours
- Download repositories as zip files
- Remove repositories from the mirror list

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Run the application using:
```bash
python main.py
```

The application will be available at http://localhost:8000

## Features

- Web interface for managing repository mirrors
- Automatic repository mirroring every 12 hours
- Download repositories as zip files
- Configuration stored in `config.yaml`
- Mirrored repositories stored in `repos` directory

## Configuration

The application stores its configuration in `config.yaml`. This file is automatically created when the application starts. You don't need to modify it manually as all operations can be performed through the web interface.
