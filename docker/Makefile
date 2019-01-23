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
	@echo "\tmake cleanadmin		# For new pgAdmin"
	@echo "\tmake cleanpython	# For new Jupyter/Python"
	@echo "\tmake cleandb		# For new PostgreSQL"
	@echo
	@echo

cleanadmin: stop
	docker rm pgadmin | true
	docker rmi docker_pgadmin | true
	docker rmi $(docker images -f "dangling=true" -q) | true

cleanpython: stop
	docker rm jupyter | true
	docker rmi docker_python | true
	docker rmi $(docker images -f "dangling=true" -q) | true

cleandb: stop
	docker rm postgres | true
	docker rmi docker_db | true
	docker rmi $(docker images -f "dangling=true" -q) | true

cleanall: cleanadmin cleanpython cleandb

cleandangling:
	docker rmi $(docker images -f "dangling=true" -q) | true

stop:
	docker-compose stop

start:
	docker-compose up -d

build: stop
	docker-compose build
