.DEFAULT_GOAL := help
SHELL := /bin/bash
PY ?= python3
PORT ?= 4000
HOST ?= 127.0.0.1
export PYTHONPATH := src
export BUNDLE_PATH := vendor/bundle

.PHONY: help install install-python install-ruby data serve serve-jekyll preview build screenshot test clean

help:
	@echo "sports-trends — local frontend preview"
	@echo ""
	@echo "  make install   Install Python deps + Ruby/Jekyll gems"
	@echo "  make serve     Generate JSON, then serve the dashboard with Jekyll"
	@echo "                 -> http://$(HOST):$(PORT)/sports/"
	@echo "  make preview   Zero-Ruby fallback: serve a Python-rendered preview"
	@echo "  make data      Regenerate the public JSON (assets/data/sports/*.json)"
	@echo "  make build     Build the static site into _site/"
	@echo "  make test      Run the Python test suite"
	@echo "  make clean     Remove _site/ and caches"

install: install-python install-ruby

install-python:
	@echo "==> Installing Python dependencies"
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e .

install-ruby:
	@echo "==> Installing Jekyll (bundler -> vendor/bundle)"
	bundle install

data:
	@echo "==> Generating public JSON from mock/live data"
	$(PY) scripts/run_publish_frontend_json.py

serve: data serve-jekyll

serve-jekyll:
	@echo "==> Serving at http://$(HOST):$(PORT)/sports/  (Ctrl+C to stop)"
	bundle exec jekyll serve --host $(HOST) --port $(PORT) --livereload

build: data
	bundle exec jekyll build

preview: data
	@echo "==> Python preview (no Ruby) at http://$(HOST):$(PORT)/sports/"
	$(PY) scripts/preview_site.py --host $(HOST) --port $(PORT)

screenshot: data
	$(PY) scripts/preview_site.py --screenshot

test:
	$(PY) -m pytest -q

clean:
	rm -rf _site .jekyll-cache .preview_sports.html
