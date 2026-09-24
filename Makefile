SPEC := spec/0.3.0

.PHONY: check

check:
	python3 $(SPEC)/tools/validate.py vectors
	python3 $(SPEC)/tools/validate.py export $(SPEC)/examples/export
