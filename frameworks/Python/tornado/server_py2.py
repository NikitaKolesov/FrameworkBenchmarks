#!/usr/bin/env python

import json
import motor
from pymongo.operations import UpdateOne
import tornado.ioloop
import tornado.web
import tornado.httpserver

from random import randint
from tornado import gen
from tornado.options import options
from commons import (
    JsonHandler,
    JsonHelloWorldHandler,
    PlaintextHelloWorldHandler,
    HtmlHandler,
)


options.define("port", default=8888, type=int, help="Server port")
options.define("mongo", default="localhost", type=str, help="MongoDB host")
options.define("backlog", default=8192, type=int, help="Server backlog")


class SingleQueryHandler(JsonHandler):
    @gen.coroutine
    def get(self):
        world = yield db.world.find_one(randint(1, 10000))
        world = {
            self.ID: int(world["_id"]),
            self.RANDOM_NUMBER: int(world[self.RANDOM_NUMBER]),
        }

        response = json.dumps(world)
        self.finish(response)


class MultipleQueriesHandler(JsonHandler):
    @gen.coroutine
    def get(self):
        try:
            queries = int(self.get_argument(self.QUERIES))
        except Exception:
            queries = 1
        else:
            if queries < 1:
                queries = 1
            elif queries > 500:
                queries = 500

        worlds = yield [db.world.find_one(randint(1, 10000)) for _ in xrange(queries)]

        worlds = [
            {
                self.ID: int(world["_id"]),
                self.RANDOM_NUMBER: int(world[self.RANDOM_NUMBER]),
            }
            for world in worlds
        ]

        self.finish(json.dumps(worlds))


class UpdateHandler(JsonHandler):
    @gen.coroutine
    def get(self):
        try:
            queries = int(self.get_argument(self.QUERIES))
        except Exception:
            queries = 1
        else:
            if queries < 1:
                queries = 1
            elif queries > 500:
                queries = 500

        worlds = yield [db.world.find_one(randint(1, 10000)) for _ in xrange(queries)]
        updates = []
        out = []

        for world in worlds:
            new_value = randint(1, 10000)
            updates.append(
                UpdateOne(
                    {"_id": world["_id"]}, {"$set": {self.RANDOM_NUMBER: new_value}}
                )
            )
            out.append({self.ID: world["_id"], self.RANDOM_NUMBER: new_value})

        yield db.world.bulk_write(updates, ordered=False)
        self.finish(json.dumps(out))


class FortuneHandler(HtmlHandler):
    @gen.coroutine
    def get(self):
        fortunes = []
        cursor = db.fortune.find()

        while (yield cursor.fetch_next):
            fortunes.append(cursor.next_object())
        fortunes.append(
            {self.ID: 0, "message": "Additional fortune added at request time."}
        )
        fortunes.sort(key=lambda f: f["message"])
        self.render("fortunes.html", fortunes=fortunes)


application = tornado.web.Application(
    [
        (r"/json", JsonHelloWorldHandler),
        (r"/plaintext", PlaintextHelloWorldHandler),
        (r"/db", SingleQueryHandler),
        (r"/queries", MultipleQueriesHandler),
        (r"/updates", UpdateHandler),
        (r"/fortunes", FortuneHandler),
    ],
    template_path="templates",
)
application.ui_modules = {}

if __name__ == "__main__":
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(application)
    server.bind(options.port, backlog=options.backlog)
    server.start(0)

    ioloop = tornado.ioloop.IOLoop.instance()
    db = motor.MotorClient(options.mongo, maxPoolSize=500).hello_world
    ioloop.start()
