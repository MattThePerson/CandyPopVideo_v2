# Linux Makefile

# Paths
GO_BACKEND_DIR := go_backend
TRAY_APP_SCRIPT := launcher/tray_app.py
EXE_NAME := CandyPopVideo
LAUNCHER_EXE_NAME := CandyPopVideoTrayApp
VENV_DIR := .venv

# Tools
PYTHON := $(VENV_DIR)/bin/python
# PIP := $(VENV_DIR)/bin/pip
PYINSTALLER := $(VENV_DIR)/bin/pyinstaller

.PHONY: all test install build-go build-launcher build clean

test:
	@echo "Hello there, Linux!"

# Default target
all: install build

# Set up Python virtual environment and install requirements
install:
	if [ ! -d "$(VENV_DIR)" ]; then \
		python3 -m venv $(VENV_DIR); \
	fi
	$(VENV_DIR)/bin/pip install uv
	$(VENV_DIR)/bin/uv pip install -r requirements.txt

# Build Go backend
build-go:
	go mod tidy -C go_backend && \
    go build -C go_backend -ldflags="-s -w" -o ../$(EXE_NAME)

# Build Python executable
build-launcher:
	$(PYINSTALLER) $(TRAY_APP_SCRIPT) --name $(LAUNCHER_EXE_NAME) --onefile --noconsole --icon=assets/icon.ico --distpath .
	rm -f *.spec

build: build-go build-launcher

# Clean Python build artifacts
clean:
	rm -rf build dist *.spec

# 
run:
	go build -C go_backend -ldflags="-s -w" -o ../CandyPopVideo && ./CandyPopVideo
