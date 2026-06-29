release: python manage.py migrate && python manage.py seed_menu && python manage.py init_admin && python manage.py init_info
web: gunicorn config.wsgi --log-file -
