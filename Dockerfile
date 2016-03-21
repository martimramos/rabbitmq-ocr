FROM library/centos:7

MAINTAINER A N GSC <your_team@yourDomain.you>

RUN yum -y update && yum -y install epel-release && yum -y install tesseract tesseract-langpack-por python-pip
RUN pip install pika

ENV channel_in_queue='rabbitmq_in_queue'
ENV channel_out_queue="rabbitmq_out_queue"
ENV rabbitmq_hostname='yourRabbitMQ_hostname
ENV rabbitmq_port=5672
ENV rabbitmq_username='username'
ENV rabbitmq_password='password'

WORKDIR /runtime
COPY daemon.py /runtime/daemon.py
