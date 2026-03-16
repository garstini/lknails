bind = "0.0.0.0:8000"
workers = 3
threads = 2
timeout = 60
wsgi_app = "config.wsgi:application"
accesslog = "-"
errorlog = "-"
