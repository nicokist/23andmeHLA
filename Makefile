all:
	docker build -t 23andmehla:latest .
	docker run -p 5000:5000 23andmehla
