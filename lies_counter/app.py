import os

import aiohttp_jinja2
import aioredis
import jinja2
from aiohttp import web


async def home(request):
    context = {
        "ebj": 2,
        "rgf": 2,
    }
    response = aiohttp_jinja2.render_template("index.html", request,
                                              context=context)

    return response


async def increment(request):
    user_id = request.match_info.get('name', "Anonymous")
    await request.app["db"].execute("INCR", user_id)
    return web.Response()


async def decrement(request: web.Request):
    user_id = request.match_info.get('name', "Anonymous")
    await request.app["db"].execute("DECR", user_id)
    return web.Response()


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

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
    )

    return app


if __name__ == '__main__':
    web.run_app(init())
