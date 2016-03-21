# rabbitmq-ocr

#configure your env vars
vim Dockerfile

# Build you image
docker build --tag="localhost:5000/centos7/tesseract_pr:latest" --file="/var/docker_projects/centos7/tesseract/Dockerfile" .

# Lauch docker instance
/usr/bin/docker run --restart=always --name tesseract_container_name docker_regestry_hostname:5000/centos7/tesseract /bin/sh -c "python daemon.py"

# If you are using fleet please find the unui file

