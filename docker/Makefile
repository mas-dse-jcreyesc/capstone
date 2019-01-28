default: info

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
	@echo "\tmake cleandb		# For new PostgreSQL"
	@echo
	@echo

cleanpython: stop
	docker rm jupyter | true
	docker rmi docker_python | true
	docker rmi $(docker images -f "dangling=true" -q) | true

cleandb: stop
	docker rm postgres | true
	docker rmi docker_db | true
	docker rmi $(docker images -f "dangling=true" -q) | true

cleanmongo: stop
	docker rm mongo | true
	docker rmi docker_mongo | true
	docker rmi $(docker images -f "dangling=true" -q) | true

cleanall: cleanpython cleandb cleanmongo prep

cleandangling:
	docker rmi $(docker images -f "dangling=true" -q) | true

stop:
	docker-compose stop

start: prep
	docker-compose up -d

build: stop prep
	docker-compose build

prep:
	mkdir -p ../postgres_db/tmp
	mkdir -p ../mongo_db
