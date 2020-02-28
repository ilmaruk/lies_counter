import aioredis
from aiohttp import web


async def home(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def increment(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def decrement(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def connect_to_db(app):
    app["db"] = await aioredis.create_redis(('redis', 6379), loop=app.loop)


def init():
    app = web.Application()
    app.add_routes([
        web.get('/', home),
        web.post('/inc/{name}', increment),
        web.post('/dec/{name}', decrement),
    ])

    app.on_startup.append(connect_to_db)

    return app


if __name__ == '__main__':
    web.run_app(init())
