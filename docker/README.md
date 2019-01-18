# dse_python3
## DSE Jupyter Notebook / Postgresql / PgAdmin

Use this command to build and test your configuration:
```
docker-compose up -d
 or
make build
```

Once you are happy with your configuration you can
run a service with :
```
docker-compose start
or
make start
```

Stop the service with:
```
docker-compose stop
or
make stop
```

Clean your configuration with:
```
make cleanall
or
make cleandb
make cleanpython
make cleanadmin
```

### ALL OF THOSE COMMANDS ARE FROM THIS SAME FOLDER WITH THE docker-compose.yml FILE.


* Edit file `docker-compose.yml` to set your
path to the notebook repo on your system
and the local port that you want on the browser.
* You also need to have the folders:
    - ~             : your home folder will be the base directory for Jupyter
    - ~/postgres    : this will be the permanent storage for postgres in case
                        you rebuild the container you will not loose the data.
                        If you start a new container it might need a new definition
                        of the server to "db" and credentials "postgres:postgres"
                        but the data will be there.
