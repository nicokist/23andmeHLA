all:
	docker build -t 23andmehla:latest .
	docker run -e flask_secret_key='Jerusalem' --link some-redis:redis -p 5000:5000 -p 8000:80 23andmehla
