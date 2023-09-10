import asyncio
import ssl
import socket

import arcane.settings


class AsyncIRCBot:
    def __init__(self, host, port, username, token, channels):
        self.host = host
        self.port = port
        self.username = username
        self.token = token
        self.channels = channels
        self.irc = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port, ssl=True)
        await self.send(f"PASS oauth:{self.token}")
        await self.send(f"NICK {self.username}")
        for channel in self.channels:
            await self.join_channel(channel)

    async def send(self, message):
        self.writer.write((message + '\r\n').encode())
        return await self.writer.drain()

    async def join_channel(self, channel):
        await self.send(f"JOIN #{channel}")

    async def receive_messages(self):
        while True:
            data = await self.reader.readline()
            if not data:
                raise Exception("socket closed")
            print(f'Receiver: {data.decode()}')  # Здесь вы можете обработать входящее сообщение

    async def setop(self):
        await self.connect()
        await self.receive_messages()

    async def run(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(await self.setop())


if __name__ == "__main__":
    HOST = "irc.chat.twitch.tv"
    PORT = 6697
    USERNAME = arcane.settings.USERNAME
    TOKEN = arcane.settings.ACCESS_TOKEN
    CHANNELS = ["magicxcmd"]  # Список каналов для подключения

    bot = AsyncIRCBot(HOST, PORT, USERNAME, TOKEN, CHANNELS)
    asyncio.run(bot.run())
