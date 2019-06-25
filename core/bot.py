import json
import logging
from collections import namedtuple

import discord
from discord.ext import commands
from pymongo import MongoClient, errors


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Mongo:
    """Simple wrapper around PyMongo."""

    def __init__(self, db_client, collection):
        self.db_client = db_client
        self.collection = getattr(self.db_client, collection)

    def find(self, name):
        if not self.db_client:
            return None
        return(self.collection.find_one({"name": name}))

    def insert(self, name, value):
        if not self.db_client:
            return None
        document = {"name": name}
        document.update(value)
        return (self.collection.insert_one(document))

    def update(self, name, data):
        if not self.db_client:
            return None
        document = self.find(name)
        document.update(data)
        return self.save(document)

    def delete(self, name):
        if not self.db_client:
            return None
        return (self.collection.delete_one({"name": name}))

    def save(self, doc):
        if not self.db_client:
            return None
        return (self.collection.save(doc))


class Bot(commands.AutoShardedBot):
    """An extension of AutoShardedBot, provided by the discord.py library"""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        with open("./config.json", "r", encoding="utf8") as file:
            data = json.dumps(json.load(file))
            self.config = json.loads(data, object_hook=lambda d: namedtuple(
                "config", d.keys())(*d.values()))

    def db(self, collection):
        return Mongo(self.db_client, collection)

    def connect_to_mongo(self):
        db_client = MongoClient(self.config.uri)[self.config.db]
        try:
           db_client.collection_names()
        except Exception:
            db_client = None
            logger.warning("MongoDB connection failed. There will be no MongoDB support.")
        return db_client


    async def on_ready(self):
        self.load_extension('ui.developer')
        game = discord.Game("Unfinished.")
        await self.change_presence(status=discord.Status.dnd, activity=game)
        self.db_client = await self.loop.run_in_executor(None, self.connect_to_mongo)
        print("Running.")
    

flux = Bot(command_prefix=commands.when_mentioned_or("."))
