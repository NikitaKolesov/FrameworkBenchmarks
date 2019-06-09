from aiohttp import web

routes = web.RouteTableDef()

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


@routes.get('/json')
async def index(request):
    return web.json_response(json_response)


app = web.Application()
app.add_routes(routes)
