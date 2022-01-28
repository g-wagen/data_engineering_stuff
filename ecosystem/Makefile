# Makefile
# -----------------------------------------------------------------------------

# LOOK FOR .env FILE
# -----------------------------------------------------------------------------
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

datalake_container = ${DATA_LAKE_DB_NAME}-mysql
datalake_volume = ${DATA_LAKE_DB_NAME}-vol
datalake_ports = ${DATA_LAKE_DB_PORT_EXTERN}:${DATA_LAKE_DB_PORT_INTERN}

datawarehouse_container = ${DATA_WAREHOUSE_DB_NAME}-mysql
datawarehouse_volume = ${DATA_WAREHOUSE_DB_NAME}-vol
datawarehouse_ports = ${DATA_WAREHOUSE_DB_PORT_EXTERN}:${DATA_WAREHOUSE_DB_PORT_INTERN}

mysql_loc = /var/lib/mysql

# Deploy the docker containers
# -----------------------------------------------------------------------------
deploy_datalake :
	@echo "\nCreating Datalake Docker Volume ... "
	@docker volume create ${datalake_volume}
	@echo "\nCreating Datalake Docker Container ... "
	@docker run --name ${datalake_container} \
	-v ${datalake_volume}:${mysql_loc} \
	-p ${datalake_ports} \
	-e MYSQL_ROOT_PASSWORD=${DATA_LAKE_ROOT_PW} \
	-e MYSQL_DATABASE=${DATA_LAKE_DB_NAME} \
	-e MYSQL_USER=${DATA_LAKE_USER} \
	-e MYSQL_PASSWORD=${DATA_LAKE_USER_PW} \
	-d mysql:8.0

deploy_datawarehouse :
	@echo "\nCreating Warehouse Docker Volume ... "
	@docker volume create ${datawarehouse_container}
	@echo "\nCreating Warehouse Docker Container ... "
	@docker run --name ${datawarehouse_container} \
	-v ${datawarehouse_volume}:${mysql_loc} \
	-p ${datawarehouse_ports} \
	-e MYSQL_ROOT_PASSWORD=${DATA_WAREHOUSE_ROOT_PW} \
	-e MYSQL_DATABASE=${DATA_WAREHOUSE_DB_NAME} \
	-e MYSQL_USER=${DATA_WAREHOUSE_USER} \
	-e MYSQL_PASSWORD=${DATA_WAREHOUSE_USER_PW} \
	-d mysql:8.0

deploy_databases : deploy_datalake deploy_datawarehouse


# Start the docker containers in case they aren't running
# -----------------------------------------------------------------------------
start_datalake :
	@echo "\nStarting Datalake Container ... "
	@docker container start ${datalake_container}

start_datawarehouse :
	@echo "\nStarting Datawarehouse Container ... "
	@docker container start ${datawarehouse_container}

start_databases : start_datalake start_datawarehouse


# Stop the running containers
# -----------------------------------------------------------------------------
stop_datalake :
	@echo "\nStopping Datalake Container ... "
	@docker container stop ${datalake_container}

stop_datawarehouse :
	@echo "\nStopping Datawarehouse Container ... "
	@docker container stop ${datawarehouse_container}

stop_databases : stop_datalake stop_datawarehouse


# Log-in to the mysql databases of the containers
# -----------------------------------------------------------------------------
login_mysql_datalake:
	@docker exec -it ${datalake_container} \
	mysql -u ${DATA_LAKE_USER} --password=${DATA_LAKE_USER_PW}

login_mysql_datawarehouse:
	@docker exec -it ${datawarehouse_container} \
	mysql -u ${DATA_WAREHOUSE_USER} --password=${DATA_WAREHOUSE_USER_PW}


# Destroy the docker containers and all their data forever
# -----------------------------------------------------------------------------
destroy_datalake : \
	stop_datalake
	@echo "\nDeleting Datalake Container ... "
	@docker container rm ${datalake_container}
	@echo "\nRemoving Datalake Container Volume ... "
	@docker volume rm ${datalake_volume}

destroy_datawarehouse : \
	stop_datawarehouse
	@echo "\nDeleting Datawarehouse Container ... "
	@docker container rm ${datawarehouse_container}
	@echo "\nRemoving Datawarehouse Container Volume ... "
	@docker volume rm ${datawarehouse_volume}

destroy_databases : destroy_datalake destroy_datawarehouse
