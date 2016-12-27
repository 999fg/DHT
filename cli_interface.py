import asyncio
import network
import logging
import random
logging.getLogger().setLevel("INFO")

addrs = ["10.0.0.4", "10.0.0.7", "10.0.0.8", "10.0.0.10"] # gemini1, gemini3, Gemini4, gemini6
PORT = 19999

class CLI(network.Network):
    async def start(self):
        args = input("INPUT (put key value/get key/remove key/stat): ")
        args = args.split(' ')
        addr = (addrs[random.randint(0,3)], PORT)
        if args[0] == 'put' and len(args) == 3:
            message = {
                "type": "put",
                "uuid": self.uuid,
                "key": args[1],
                "value": args[2],
            }
            self.send_message(message, addr)
            asyncio.ensure_future(self.start(), loop = self._loop)
        elif args[0] == 'get' and len(args) == 2:
            message = {
                "type": "get",
                "uuid": self.uuid,
                "key": args[1]
            }
            self.send_message(message, addr)
        elif args[0] == 'remove' and len(args) == 2:
            message = {
                "type": "remove",
                "uuid": self.uuid,
                "key": args[1]
            }
            self.send_message(message, addr)
            asyncio.ensure_future(self.start(), loop = self._loop)
        elif args[0] == 'stat' and len(args) == 1:
            message = {
                "type": "stat",
                "uuid": self.uuid,
            }
            self.send_message(message, addr)
        else:
            logging.info("Invalid input arguments.")
            asyncio.ensure_future(self.start(), loop = self._loop)
    def message_arrived(self, message, addr):
        if message["type"] == "get_success":
            if message["value"]:
                logging.info("get success! The value for key {key} is {value}.".format(key=message["key"], value=message["value"]))
            else:
                logging.info("get failed! The key does not exist!")
            asyncio.ensure_future(self.start(), loop = self._loop)
        elif message["type"] == "stat_success":
            stat = message["node_key"]
            redundancy = {}
            for uuid, keylist in stat.items():
                for key in keylist:
                    if key not in redundancy.keys():
                        redundancy[key] = 1
                    else:
                        redundancy[key] += 1
            index = 0
            for uuid, keylist in stat.items():
                logging.info("-----------------")
                logging.info("<Node {index}>".format(index=index))
                logging.info("UUID: {uuid}".format(uuid=uuid))
                logging.info("# of KEYs: {no}".format(no=len(keylist)))
                logging.info("-----------------")
                logging.info("# of REDUNDANCIES")
                for key in keylist:
                    logging.info("KEY {key}: {red} times".format(key=key, red=redundancy[key]))
                logging.info("-----------------")
    def __init__(self, loop):
        network.Network.__init__(self, loop)
        self._loop = loop

        import uuid
        self.uuid = str(uuid.uuid1())
        asyncio.ensure_future(self.start(), loop = self._loop)


def interface():
    loop = asyncio.new_event_loop()

    CLI(loop)

    try:
        loop.run_forever()
    finally:
        loop.close()
    pass

if __name__ == "__main__":
    interface()
