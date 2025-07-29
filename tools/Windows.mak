# Windows Makefile

# Paths
GO_BACKEND_DIR := go_backend
TRAY_APP_SCRIPT := launcher/tray_app.py
EXE_NAME := CandyPopVideo
LAUNCHER_EXE_NAME := CandyPopVideoTrayApp
VENV_DIR := .venv

# Tools
PYTHON := $(VENV_DIR)/Scripts/python
PIP := $(VENV_DIR)/Scripts/pip
PYINSTALLER := $(VENV_DIR)/Scripts/pyinstaller

.PHONY: all test clean

test:
	@echo Hello there, Windows!

# Default target
all: install build


# INSTALL:
# Set up Python virtual environment and install requirements
install:
	@if not exist $(VENV_DIR) ( \
		python -m venv $(VENV_DIR) \
	)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt


# BUILD:
# Build Go backend
build-go:
	cd $(GO_BACKEND_DIR) && go build -ldflags="-s -w" -o "$(EXE_NAME).exe"

# Build Python executable
build-launcher:
	$(PYINSTALLER) $(TRAY_APP_SCRIPT) --name $(LAUNCHER_EXE_NAME) --onefile --noconsole --icon=assets/icon.ico --distpath .
	if exist *.spec del /Q *.spec

build: build-go build-launcher


# CLEAN:
# Clean Python build artifacts
clean:
	del /Q /S build dist *.spec
