all: dump update migrate restart

update:
	@echo "Pulling the latest changes from the git repository"
	git pull origin master
	chown -R www-pub.www-pub .

dump:
	@echo "Dumping sqp to /tmp/latest_sqp_devel_dump.sql"
	mysqldump -u sqp -p sqp_prod > /tmp/latest_sqp_dump.sql

migrate: dump
	@echo "Running south migrations"
	./python manage.py migrate sqp 

quick-migrate:
	@echo "Running migration and skipping temp dump"
	./python manage.py migrate sqp

restart: stop start
	
status:
	supervisorctl status

stop:
	@echo "Restarting supervisord services"
	supervisorctl stop all
	
start:	
	service supervisord start
	supervisorctl status
	sleep 10
	supervisorctl status

