UV ?= uv
PYTHON ?= python
BASE := ../0.1.2

.PHONY: check check-exchange check-canonical check-verified check-governed rebuild

check: check-exchange check-canonical

check-exchange:
	$(UV) run --no-project --with-requirements requirements-checks.txt $(PYTHON) tools/validate-exchange.py

check-canonical: check-exchange
	node tools/verify-canonical.mjs

check-verified: check-canonical
	node tools/verify-verified.mjs

check-governed: check-verified
	$(UV) run --no-project --with-requirements $(BASE)/requirements-checks.txt $(PYTHON) $(BASE)/tools/validate-package.py
	node $(BASE)/tools/verify-conformance.mjs
	node $(BASE)/tools/verify-suppression-fixture.mjs
	bash $(BASE)/tools/verify-postgres-fixture.sh

rebuild:
	node tools/build-requirements.mjs
	node tools/build-catalog.mjs
	node tools/build-bundles.mjs
