build-container:
	docker build -t streaming-community-api .

run-container:
	docker run --rm -it -p 8000:8000 -v ${LOCAL_DIR}:/app/Video -v ./config.json:/app/config.json streaming-community-api