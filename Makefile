# Shabakah helper targets. Author: Ali AlEnezi (SiteQ8)
IMAGE ?= shabakah:latest
NAME  ?= shabakah
PORT  ?= 2222

.PHONY: build run ssh stop clean test shell logs

build:
	docker build -t $(IMAGE) .

run:
	docker run -d --name $(NAME) --cap-add NET_ADMIN -p $(PORT):22 $(IMAGE)
	@echo "SSH in with: ssh -p $(PORT) learner@localhost"

ssh:
	ssh -p $(PORT) learner@localhost

stop:
	-docker stop $(NAME)
	-docker rm $(NAME)

clean: stop
	-docker rmi $(IMAGE)

logs:
	docker logs -f $(NAME)

shell:
	docker exec -it $(NAME) bash

test:
	sh tests/smoke.sh
