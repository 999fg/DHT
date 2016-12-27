import asyncio

import network
import logging
logging.getLogger().setLevel("INFO")

class CLI:

    async def start(self):
        logging.info(input("HELLO: "))
    def __init__(self, loop):
        network.Network.__init__(self, loop)
        self._loop = loop
        asyncio.ensure_future(self.start(), loop = self._loop)


def main():
    loop = asyncio.new_event_loop()

    CLI(loop)

    try:
        loop.run_forever()
    finally:
        loop.close()
    pass

if __name__ == "__main__":
    main()
