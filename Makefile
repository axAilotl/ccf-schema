VERSION := 0.1.2
PACKAGE := spec/$(VERSION)
ARCHIVE_NAME := ccf-$(VERSION).zip
ARCHIVE := spec/$(ARCHIVE_NAME)

.PHONY: check rebuild reproduce package

check:
	$(MAKE) -C $(PACKAGE) check

rebuild:
	$(MAKE) -C $(PACKAGE) rebuild

reproduce:
	$(MAKE) -C $(PACKAGE) reproduce

package:
	$(MAKE) -C $(PACKAGE) package
	cd spec && sha256sum $(ARCHIVE_NAME) > $(ARCHIVE_NAME).sha256
