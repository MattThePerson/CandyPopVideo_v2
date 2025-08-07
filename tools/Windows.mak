# Windows Makefile

# Paths
GO_BACKEND_DIR := go_backend
TRAY_APP_SCRIPT := launcher\tray_app.py
EXE_NAME := CandyPopVideo
LAUNCHER_EXE_NAME := CandyPopVideoTrayApp
VENV_DIR := .venv

# Tools
PYTHON := $(VENV_DIR)/Scripts/python
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
	$(VENV_DIR)\Scripts\python.exe -m pip install --upgrade pip
	$(VENV_DIR)\Scripts\pip.exe install uv
	$(VENV_DIR)\Scripts\uv.exe pip install -r requirements.txt


# BUILD:
# Build Go backend
build-go:
	go mod tidy -C go_backend && \
    go build -C go_backend -ldflags="-s -w" -o ..\$(EXE_NAME).exe

# Build Python executable
build-launcher:
	$(PYINSTALLER) $(TRAY_APP_SCRIPT) --name $(LAUNCHER_EXE_NAME) --onefile --noconsole --icon=assets\icon.ico --distpath bin
	if exist *.spec del /Q *.spec

build: build-go build-launcher


# CLEAN:
# Clean Python build artifacts
clean:
	del /Q /S build dist *.spec
