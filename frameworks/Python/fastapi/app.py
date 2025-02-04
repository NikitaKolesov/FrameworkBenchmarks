import asyncio
import asyncpg
import os
import jinja2
from fastapi import FastAPI
from starlette.responses import HTMLResponse, UJSONResponse, PlainTextResponse
from random import randint
from operator import itemgetter
from urllib.parse import parse_qs

lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

json_response = {
    "name": "Ekaterina",
    "lastname": "Kolesova",
    "age": 25,
    "married": True,
    "pets": 0,
    "salary": 50000,
    "currency": "rubles",
    "credo": "Sitting is better than eating",
    "dummy_text": lorem_ipsum,
}

app = FastAPI()


@app.get("/json")
async def json_serialization():
    return UJSONResponse(json_response)


@app.get("/ujson")
async def json_serialization():
    return json_response


@app.get("/plaintext")
async def plaintext():
    return PlainTextResponse(b"Hello, world!")
