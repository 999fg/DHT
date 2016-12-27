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
import random
logging.getLogger().setLevel("INFO")

NETWORK_MAGIC_VALUE= "Sound body, sound code."
NETWORK_PORT = 19999
NETWORK_LISTEN_ADDR = "0.0.0.0" #or 127.0.0.1
NETWORK_UDP_MTU = 1024
NETWORK_BROADCAST_ADDR = "255.255.255.255"
EMULATE_BROADCAST = True
EMULATE_ADDR = "10.0.0.{num}"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
cli_uuid = str(uuid.uuid1())
args = sys.argv[1:]

def send_message(message):
    s = json.dumps(message)
    try:
        b = s.encode(encoding='utf-8', errors='strict')
        if len(b) > NETWORK_UDP_MTU:
            logging.error("Too large send message: {orig} over {limit}".format(orig=len(b), limit=NETWORK_UDP_MTU))
        else:
            logging.debug("Sending {bytes} bytes of message".format(bytes=len(b)))
            addrs = ["10.0.0.4", "10.0.0.7", "10.0.0.8", "10.0.0.9"]
            addr_to = addrs[random.randint(0,3)]
            sock.sendto(b, ("10.0.0.4", NETWORK_PORT))
    except Exception as e:
        logging.error("Cannot encode a send message: " + str(e))


def cli():
    if args[0] == 'put' and len(args) == 3:
        message = {
            "type": "put",
            "uuid": cli_uuid,
            "key": args[1],
            "value": args[2],
            "_magic": NETWORK_MAGIC_VALUE,
        }
        send_message(message)
        sock.bind(("0.0.0.0", 19999))
        data = None
        while True:
            data = sock.recvfrom(1024)
            if data:
                s = data.decode(encoding="utf-8", errors="strict")
                message = json.loads(s)
                if not "_magic" in message:
                    raise Exception("No magic value")
                if not message["_magic"] == NETWORK_MAGIC_VALUE:
                    raise Exception("Invalid magic value")
                if message["type"] == "put_success":
                    logging.info("PUT SUCCESSFUL!")

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
