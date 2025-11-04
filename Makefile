.PHONY: build-gds-snmp build-gds-notification build-all

# Build package images in this mono-repo. Each target builds from the
# package directory so the docker build context is small and package-owned.

build-gds-snmp:
	docker build -t gds_snmp_receiver:latest gds_snmp_receiver/

build-gds-notification:
	@if [ -d gds_notification ]; then \
	  docker build -t gds_notification:latest gds_notification/; \
	else \
	  echo "gds_notification/ not present, skipping"; \
	fi

build-all: build-gds-snmp build-gds-notification
# Makefile for dev container workflows

IMAGE_NAME ?= dbtools-dev
IMAGE_TAG ?= latest
IMAGE := $(IMAGE_NAME):$(IMAGE_TAG)
WORKDIR ?= /workspaces/dbtools
KRB5_CONF ?= .devcontainer/krb5/krb5.conf

.PHONY: help
help:
	@echo "Devcontainer Make targets:"
	@echo "  make build            - Build the dev image"
	@echo "  make build-no-cache   - Build without cache (fresh)"
	@echo "  make run              - Run container with repo mounted"
	@echo "  make shell            - Start interactive bash in container"
	@echo "  make ps               - List running containers"
	@echo "  make ps-all           - List all containers"
	@echo "  make images           - List images"
	@echo "  make logs ID=...      - Show logs for container"
	@echo "  make stop ID=...      - Stop container"
	@echo "  make rm ID=...        - Remove container"
	@echo "  make rmi IMG=...      - Remove image"
	@echo "  make prune            - Prune unused data"
	@echo "  make builder-prune    - Prune build cache"
	@echo "  make clean-all        - Stop/rm all containers and prune"
	@echo "  make verify           - Run quick verification commands"

.PHONY: build
build:
	docker build -f .devcontainer/Dockerfile -t $(IMAGE) .

.PHONY: build-no-cache
build-no-cache:
	docker build --no-cache -f .devcontainer/Dockerfile -t $(IMAGE) .

.PHONY: run
run:
	docker run --rm -d \
		--name $(IMAGE_NAME) \
		-v "$(PWD)":$(WORKDIR) \
		-v "$(PWD)/$(KRB5_CONF)":/etc/krb5.conf:ro \
		-e KRB5_CONFIG=/etc/krb5.conf \
		-w $(WORKDIR) \
		$(IMAGE) tail -f /dev/null

.PHONY: shell
shell:
	docker exec -it $(IMAGE_NAME) bash || docker run --rm -it \
		-v "$(PWD)":$(WORKDIR) \
		-v "$(PWD)/$(KRB5_CONF)":/etc/krb5.conf:ro \
		-e KRB5_CONFIG=/etc/krb5.conf \
		-w $(WORKDIR) \
		$(IMAGE) bash

.PHONY: ps
ps:
	docker ps

.PHONY: ps-all
ps-all:
	docker ps -a

.PHONY: images
images:
	docker images

.PHONY: logs
logs:
	@if [ -z "$(ID)" ]; then echo "Usage: make logs ID=<container_id>"; exit 1; fi
	docker logs $(ID)

.PHONY: stop
stop:
	@if [ -z "$(ID)" ]; then echo "Usage: make stop ID=<container_id>"; exit 1; fi
	docker stop $(ID)

.PHONY: rm
rm:
	@if [ -z "$(ID)" ]; then echo "Usage: make rm ID=<container_id>"; exit 1; fi
	docker rm $(ID)

.PHONY: rmi
rmi:
	@if [ -z "$(IMG)" ]; then echo "Usage: make rmi IMG=<image_id_or_name>"; exit 1; fi
	docker rmi $(IMG)

.PHONY: prune
prune:
	docker system prune -f

.PHONY: builder-prune
builder-prune:
	docker builder prune -af

.PHONY: clean-all
clean-all:
	-@docker ps -aq | xargs -r docker stop
	-@docker ps -aq | xargs -r docker rm
	docker system prune -f

.PHONY: verify
verify:
	docker run --rm \
		-v "$(PWD)":$(WORKDIR) \
		-w $(WORKDIR) \
		$(IMAGE) bash -lc "python -V && terraform -version && aws --version && az version && sqlcmd -? | head -n 1"

#############################################
# PDF → HTML → Markdown conversion helpers  #
#############################################

RES_DIR := docs/tutorials/docker/resources
PDF ?= mastering_docker.pdf
MD ?= mastering_docker.md

.PHONY: pdf2md-build pdf2md pdf2md-host pdf2md-clean

# Build the converter image with poppler-utils and pandoc
pdf2md-build:
	docker build -t pdf2md-tool:latest -f $(RES_DIR)/Dockerfile.convert $(RES_DIR)

# Convert a PDF (in RES_DIR) to Markdown using the containerized toolchain
# Usage: make pdf2md PDF=my_book.pdf MD=my_book.md
pdf2md: pdf2md-build
	@if [ ! -f "$(RES_DIR)/$(PDF)" ]; then \
		echo "Error: $(RES_DIR)/$(PDF) not found. Copy your PDF there or set PDF=..."; \
		exit 1; \
	fi
	docker run --rm \
		-v "$(PWD)/$(RES_DIR)":/work \
		pdf2md-tool:latest \
		"pdftohtml -c -hidden -nomerge -s $(PDF) out && pandoc -f html -t gfm --wrap=none -o $(MD) out-html.html && echo DONE"

# Convert using host-installed tools (poppler-utils, pandoc) via helper script
# Usage: make pdf2md-host PDF=my_book.pdf MD=my_book.md
pdf2md-host:
	@if [ ! -f "$(RES_DIR)/convert_pdf_to_md.sh" ]; then \
		echo "Error: $(RES_DIR)/convert_pdf_to_md.sh missing"; exit 1; \
	fi
	cd $(RES_DIR) && bash convert_pdf_to_md.sh $(PDF) $(MD)

# Remove intermediate HTML/CSS and page images in RES_DIR (keeps PDFs/MD)
pdf2md-clean:
	-@rm -f $(RES_DIR)/out-html.html $(RES_DIR)/out-*.html $(RES_DIR)/out*.css
	-@rm -f $(RES_DIR)/out*.png $(RES_DIR)/_tmp*.html $(RES_DIR)/_tmp*.png
