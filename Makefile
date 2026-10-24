AURA_BIN ?= /home/dev/code/grok-dev/aura-grok/build/aura
AURA_PATH ?= /home/dev/code/grok-dev/aura-grok/lib
export AURA_BIN
export AURA_PATH
export AURA_SANDBOX = off
export AURA_PIPELINE_STRICT ?= force-soa

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: doctor test check http run

doctor:
	@test -x "$(AURA_BIN)" || { echo "找不到 Aura 二进制：$(AURA_BIN)"; exit 127; }
	@echo "aura ok: $(AURA_BIN)"

check: doctor
	cd "$(ROOT)" && "$(AURA_BIN)" tests/check.aura

http: doctor
	cd "$(ROOT)" && sh tests/http.sh

test: check http

run: doctor
	cd "$(ROOT)" && mkdir -p runtime && exec "$(AURA_BIN)" aura/serve.aura
