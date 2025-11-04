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

 
