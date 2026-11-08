# Installed aura: nightly by default, or the v0.1.0 release.
# The launcher adds its own lib/ to AURA_PATH. Do not point this at a
# source-tree build, and do not export AURA_PATH from here.
AURA_BIN ?= aura
export AURA_BIN
export AURA_SANDBOX = off
export AURA_PIPELINE_STRICT ?= force-soa

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: doctor test check http run catalog

doctor:
	@command -v "$(AURA_BIN)" >/dev/null 2>&1 || test -x "$(AURA_BIN)" || { \
	  echo "找不到 Aura：$(AURA_BIN)"; \
	  echo "先安装。默认 nightly；钉住发布版用 AURA_VERSION=v0.1.0"; \
	  echo "curl -fsSL https://raw.githubusercontent.com/cybrid-systems/aura/main/install.sh | sh"; \
	  exit 127; }
	@echo "aura ok: $(AURA_BIN)"

catalog:
	python3 "$(ROOT)tests/catalog_check.py"

check: doctor
	cd "$(ROOT)" && "$(AURA_BIN)" tests/check.aura
	cd "$(ROOT)" && "$(AURA_BIN)" tests/mutate.aura
	cd "$(ROOT)" && "$(AURA_BIN)" tests/fractions.aura

http: doctor
	cd "$(ROOT)" && sh tests/http.sh

test: catalog check http

run: doctor
	cd "$(ROOT)" && mkdir -p runtime && exec "$(AURA_BIN)" aura/serve.aura
