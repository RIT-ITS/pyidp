workers = 2
threads = 5
timeout = 60
bind = "unix:/run/pyidp/gunicorn.sock"
accesslog = "-"
errorlog = "-"
preload_app = True
