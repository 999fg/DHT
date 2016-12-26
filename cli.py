import sys
import asyncio

import network
import timer
from enum import Enum
import logging
import datetime
import time
import uuid
import socket
logging.getLogger().setLevel("INFO")

def cli():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    cli_uuid = str(uuid.uuid1())
    args = sys.argv[1:]
    if args[0] == 'put' and len(args) == 3:
        message = {
            "type": "get",
            "uuid": cli_uuid,
        }
        sock.sendto(message, ("10.0.0.4", 19999))
        pass
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
