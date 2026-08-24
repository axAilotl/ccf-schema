VERSION := 0.1.2
PACKAGE := spec/$(VERSION)
ARCHIVE := spec/ccf-$(VERSION).zip

.PHONY: check rebuild reproduce package

check:
	$(MAKE) -C $(PACKAGE) check

rebuild:
	$(MAKE) -C $(PACKAGE) rebuild

reproduce:
	$(MAKE) -C $(PACKAGE) reproduce

package:
	$(MAKE) -C $(PACKAGE) package
	sha256sum $(ARCHIVE) > $(ARCHIVE).sha256
