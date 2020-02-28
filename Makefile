.PHONY: start stop restart rebuild

start:
	docker-compose up -d

stop:
	docker-compose down

restart: stop start

rebuild: stop
	docker-compose up -d --build