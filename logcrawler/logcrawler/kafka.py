#!/usr/bin/env python
# coding: utf-8

import struct
import binascii
import socket

def encode_message(message):
    # <MAGIC_BYTE: char> <CRC32: int> <PAYLOAD: bytes>
    return struct.pack('>B', 0) + \
           struct.pack('>i', binascii.crc32(message)) + \
           message

def encode_produce_request(topic, partition, messages):
    # encode messages as <LEN: int> <MESSAGE_BYTES>
    encoded = [encode_message(message) for message in messages]
    message_set = ''.join([struct.pack('>i', len(m)) + m for m in encoded])
    
    # create the request as 
    # <REQUEST_SIZE: int> <REQUEST_ID: short> <TOPIC: bytes> <PARTITION: int> <BUFFER_SIZE: int> <BUFFER: bytes>
    data = struct.pack('>H', KAFKA_PRODUCE_REQUEST_ID) + \
           struct.pack('>H', len(topic)) + topic + \
           struct.pack('>i', partition) + \
           struct.pack('>i', len(message_set)) + message_set
    return struct.pack('>i', len(data)) + data

class KafkaProducer:
    def __init__(self, host, port):
        try:
            self.connection = socket.socket()
            self.connection.connect((host, port))
        except:
            self.connection = None

    def close(self):
        self.connection.close()

    def send(self, messages, topic, partition = 0):
        self.connection.sendall(encode_produce_request(topic, partition, messages))
