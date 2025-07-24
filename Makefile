# Example (via DaddyGPT) for a makefile once you include Go. 
# Variables
PYTHON := python3
VENV_DIR := .venv
PYINSTALLER := $(VENV_DIR)/bin/pyinstaller
GO_OUT := backend/bin/app

.PHONY: all venv install-go build-go build-python bundle-tray clean

all: venv install-go build-go build-python bundle-tray

venv:
	@if [ ! -d $(VENV_DIR) ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi
	@$(VENV_DIR)/bin/pip install --upgrade pip

install-go:
	@echo "Ensure Go is installed and in PATH"

build-go:
	cd backend && go build -o ../$(GO_OUT) ./...

build-python:
	@$(VENV_DIR)/bin/pip install -r requirements.txt

bundle-tray:
	@$(PYINSTALLER) --onefile tray_app/tray_app.py --name CandyPopVideo

clean:
	rm -rf build dist *.spec backend/bin/*

