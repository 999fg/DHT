import asyncio

import network
import logging
logging.getLogger().setLevel("INFO")

class CLI(network.Network):
    async def start(self):
        logging.info(input("HELLO: "))
        asyncio.ensure_future(self.start(), loop = self._loop)
    def __init__(self, loop):
        network.Network.__init__(self, loop)
        self._loop = loop
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
