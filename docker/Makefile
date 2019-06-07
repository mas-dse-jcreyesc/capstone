default: info

all: build

info:
	@echo
	@echo "Easy way to build and run your UCSD-MAS env."
	@echo
	@echo "Options:"
	@echo "\tmake start		# START ALL DOCKER CONTAINERS"
	@echo "\tmake stop		# STOP ALL DOCKER CONTAINERS"
	@echo "\tmake cleanall		# For ALL elements"
	@echo
	@echo "Advanced:"
	@echo "\tmake build		# Build containes but don't start them"
	@echo "\tmake cleanpython	# For new Jupyter/Python"
	@echo
	@echo

cleanpython: stop
	docker rm jupyter | true
	docker rmi docker_python | true

cleanmongo: stop
	docker rm mongo | true
	docker rmi mongo | true

cleanall: cleanpython cleanmongo prep

cleandangling:
	docker rmi $(docker images -f "dangling=true" -q) | true

stop:
	docker-compose stop

start: prep
	docker-compose up -d

build: stop prep
	docker-compose build

prep:
	rm -rf ../postgres_db
	rm -rf ../supervisord.*
	mkdir -p ../mongo_db
