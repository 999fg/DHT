import sys
import asyncio
import json

import network
import timer
from enum import Enum
import logging
import datetime
import time
import uuid
import socket
logging.getLogger().setLevel("INFO")

NETWORK_MAGIC_VALUE= "Sound body, sound code."
NETWORK_PORT = 19999
NETWORK_LISTEN_ADDR = "0.0.0.0" #or 127.0.0.1
NETWORK_UDP_MTU = 1024
NETWORK_BROADCAST_ADDR = "255.255.255.255"
EMULATE_BROADCAST = True
EMULATE_ADDR = "10.0.0.{num}"

def cli():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    cli_uuid = str(uuid.uuid1())
    args = sys.argv[1:]
    if args[0] == 'put' and len(args) == 3:
        message = {
            "type": "get",
            "uuid": cli_uuid,
            "_magic": NETWORK_MAGIC_VALUE,
        }
        s = json.dumps(message)
        try:
            b = s.encode(encoding='utf-8', errors='strict')
            if len(b) > NETWORK_UDP_MTU:
                logging.error("Too large send message: {orig} over {limit}".format(orig=len(b), limit=NETWORK_UDP_MTU))
            else:
                logging.debug("Sending {bytes} bytes of message".format(bytes=len(b)))
                sock.sendto(b, ("10.0.0.4", 19999))
        except Exception as e:
            logging.error("Cannot encode a send message: " + str(e))
    elif args[0] == 'get' and len(args) == 2:
        pass
    elif args[0] == 'delete' and len(args) == 2:
        pass
    elif args[0] == 'stat' and len(args) == 1:
        pass
    else:
        logging.info("Invalid input arguments.")


if __name__=='__main__':
    cli()
