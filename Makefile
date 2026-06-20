
# Platform-specific variables
ifeq ($(OS),Windows_NT)
    EXE_SUFFIX := .exe
	CLEAN_CMD := if exist bin rmdir /s /q bin
else
    EXE_SUFFIX :=
	CLEAN_CMD := rm -rf bin
endif

GO_BACKEND := go_backend
DEV_PORT := 8124
LD_FLAGS := -s -w
EXE_NAME := CandyPopVideo
EXE_PATH := bin/$(EXE_NAME)$(EXE_SUFFIX)

.PHONY: all install install-python install-npm build build-go build-npm run-dev-go run-dev-npm clean

all: install build

# INSTALLING (py, npm)
install-npm:
	cd frontend && npm install

install-python:
	cd py && uv sync

install: install-python install-npm

# BUILDING (go, npm)
build-go:
	go mod tidy -C $(GO_BACKEND) && \
	go build -C $(GO_BACKEND) -ldflags="$(LD_FLAGS)" -o ../$(EXE_PATH) ./cmd/app

build-npm:
	cd frontend && npm run build

build: build-go build-npm

# DEV SERVERS
run-dev-go: build-go
	./$(EXE_PATH) --port $(DEV_PORT) --dev

run-dev-npm:
	cd frontend && npm run dev

# CLEAN
clean:
	$(CLEAN_CMD)
