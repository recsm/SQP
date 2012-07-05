all: dump update migrate restart

update:
	@echo "Pulling the latest changes from the git repository"
	git pull origin master
	chown -R www-data.www-data .

dump:
	@echo "Dumping sqp to /tmp/latest_sqp_devel_dump.sql"
	mysqldump -u sqpsu --password=f64b79b4 sqp_prod > /tmp/latest_sqp_prod_dump.sql

migrate: dump
	@echo "Running south migrations"
	python manage.py migrate sqp 

quick-migrate:
	@echo "Running migration and skipping temp dump"
	python manage.py migrate sqp

restart: stop start
	
status:
	supervisorctl status

stop:
	service supervisord stop
start:	
	service supervisord start
	supervisorctl status

django-runserver:
	supervisorctl stop tornado-8000
	env PYRO_HMAC_KEY="2d736347ff7487d559d7fb3cfc1e92dd" PYRO_HOST=10.60.6.61 PYRO_NS_HOST=10.60.6.61 python /srv/sqp_project/manage.py runserver
 8000
	supervisorctl start tornado-8000

profile:
	supervisorctl stop tornado-8000
	env PYRO_HMAC_KEY="2d736347ff7487d559d7fb3cfc1e92dd" PYRO_HOST=10.60.6.61 PYRO_NS_HOST=10.60.6.61 python -m cProfile -s time /srv/sqp_project
/manage.py runserver 8000
	supervisorctl start tornado-8000


