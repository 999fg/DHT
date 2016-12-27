import asyncio
import uuid
import network
import logging
logging.getLogger().setLevel("INFO")

class CLI(network.Network):
    async def start(self):
        args = input("INPUT (put key value/get key/remove key/stat): ")
        args = args.split(' ')
        if args[0] == 'put' and len(args) == 3:
            message = {
                "type": "put",
                "uuid": self.uuid,
                "key": args[1],
                "value": args[2],
            }
            self.send_message(message, ("10.0.0.4", 19999))
        elif args[0] == 'get' and len(args) == 2:
            pass
        elif args[0] == 'delete' and len(args) == 2:
            pass
        elif args[0] == 'stat' and len(args) == 1:
            pass
        else:
            logging.info("Invalid input arguments.")
            asyncio.ensure_future(self.start(), loop = self._loop)

    def message_arrived(self, message, addr):
        if message["type"] == "put_success":
            logging.info("put success!")
            asyncio.ensure_future(self.start(), loop = self._loop)
        

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
