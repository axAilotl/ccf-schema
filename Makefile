VERSION := 0.1.2
PACKAGE := spec/$(VERSION)
DRAFT_VERSION := 0.2.0
DRAFT_PACKAGE := spec/$(DRAFT_VERSION)
ARCHIVE_NAME := ccf-$(VERSION).zip
ARCHIVE := spec/$(ARCHIVE_NAME)

.PHONY: check check-draft check-draft-verified check-draft-governed rebuild rebuild-draft reproduce package

check:
	$(MAKE) -C $(PACKAGE) check

check-draft:
	$(MAKE) -C $(DRAFT_PACKAGE) check

check-draft-verified:
	$(MAKE) -C $(DRAFT_PACKAGE) check-verified

check-draft-governed:
	$(MAKE) -C $(DRAFT_PACKAGE) check-governed

rebuild:
	$(MAKE) -C $(PACKAGE) rebuild

rebuild-draft:
	$(MAKE) -C $(DRAFT_PACKAGE) rebuild

reproduce:
	$(MAKE) -C $(PACKAGE) reproduce

package:
	$(MAKE) -C $(PACKAGE) package
	cd spec && sha256sum $(ARCHIVE_NAME) > $(ARCHIVE_NAME).sha256
