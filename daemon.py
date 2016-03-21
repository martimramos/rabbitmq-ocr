#!/usr/bin/python
import pika
import time
import datetime
import sys
import os
import subprocess
import socket
import datetime
import logging

class RabbitmqQueueManager:

        def __init__(self):
                self.system_hostname = socket.gethostname()
                self.system_time_start = 0
                self.system_time_end = 0
                self.channel_in_queue = os.getenv('channel_in_queue')
                self.channel_out_queue = os.getenv('channel_out_queue')
                self.rabbitmq_hostname = os.getenv('rabbitmq_hostname')
                self.rabbitmq_port = os.getenv('rabbitmq_port')
                self.rabbitmq_username = os.getenv('rabbitmq_username')
                self.rabbitmq_password = os.getenv('rabbitmq_password')
                self.message_type = ''
                self.message_delivery_mode = 2
                self.message_app_id = ''
                self.message_content_type = 'application/octet-stream'
                self.message_timestamp = 0

        def publishMessage(self,message, message_delivery_mode, message_app_id, message_content_type, message_correlation_id, message_timestamp,message_type,message_headers, channel_out_queue, rabbitmq_hostname, channel):

                channel.basic_publish(exchange='',
                      routing_key=self.channel_out_queue,
                      body=message,
                      properties=pika.BasicProperties(
                      delivery_mode = self.message_delivery_mode, # make message persistent
                      app_id = self.message_app_id,
                      content_type = self.message_content_type,
                      correlation_id = message_correlation_id,
                      timestamp = self.message_timestamp,
                      type = message_type,
                      headers = message_headers,
                      ))
               
        def startConsuming(self, channel_in_queue, channel):
                channel.basic_qos(prefetch_count=1) # one message at a time
                channel.basic_consume(self.callback,queue=self.channel_in_queue)
                channel.start_consuming()

        def callback(self, ch, method, properties, body):
                message_correlation_id = properties.correlation_id
                self.system_time_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[0:-3]
                ocr_result = self.bytesTotxt(body)
                self.system_time_end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[0:-3]
                message_headers = {'origin ':lig.system_hostname, 'starttimestamp':lig.system_time_start, 'endtimestamp':lig.system_time_end }
                self.publishMessage(ocr_result, self.message_delivery_mode, self.message_app_id, self.message_content_type, message_correlation_id, self.message_timestamp,self.message_type,message_headers, lig.channel_out_queue, lig.rabbitmq_hostname, channel)
                self.messageAck(ch, method)

        def ConnectChannel(self,rabbitmq_hostname,channel_out_queue):
                connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_hostname))
                channel = connection.channel()
                channel.queue_declare(queue=self.channel_out_queue, durable=True)
                return channel

        def messageAck(self, ch, method):
                ch.basic_ack(delivery_tag = method.delivery_tag)

        def connectionClose(self):
                connection.close()

        def bytesTotxt(self, imgBytes):
                        try:
                                p = subprocess.Popen(['tesseract','-l','por+eng','stdin','stdout'],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
                                p.stdin.write(imgBytes)
                                out, err = p.communicate()
                                txt = out
                                tesseractErrorMessage = err
                                returncode = p.returncode

                                if returncode == 0:
                                        self.message_type = 'OCROK'
                                        p.stdin.close()
                                else:
                                        self.message_type = 'OCRERROR'
                                        txt = tesseractErrorMessage
                                        p.stdin.close()

                        except subprocess.CalledProcessError:
                                self.message_type = 'OCRERROR'
                                txt='IO Error.'
                                print("subprocess.CalledProcessError")
                        except IOError:
                                self.message_type = 'OCRERROR'
                                txt='An error occured trying to read the file.'
                                print("IOError ")
                        except ValueError:
                                self.message_type = 'OCRERROR'
                                txt='Non-numeric data found in the file.'
                                print("ValueError ")
                        except ImportError:
                                self.message_type = 'OCRERROR'
                                txt="NO module found"
                                print("ImportError ")
                        except EOFError:
                                self.message_type = 'OCRERROR'
                                txt='EOF on Python script?'
                                print("EOFError ")
                        except KeyboardInterrupt:
                                self.message_type = 'OCRERROR'
                                txt='Operation Cancelled.'
                                print("KeyboardInterrupt ")
                        except Exception as e:
                                self.message_type = 'OCRERROR'
                                txt = tesseractErrorMessage
                        except:
                                self.message_type = 'OCRERROR'
                                txt = tesseractErrorMessage
                                print("Generic exception ")
                        return txt

time.sleep(5)
lig = RabbitmqQueueManager()
channel = lig.ConnectChannel(lig.rabbitmq_hostname, lig.channel_out_queue)
lig.startConsuming(lig.channel_in_queue, channel)
