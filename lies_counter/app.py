import os

import aiohttp_jinja2
import aioredis
import jinja2
from aiohttp import web


async def home(request):
    db = request.app["db"]
    ebj = await _get_score(db, "ebj")
    rgf = await _get_score(db, "rgf")
    max_val = max(ebj, rgf)

    context = {
        "ebj": ebj,
        "ebj_ratio": int(ebj / max_val * 100),
        "rgf": rgf,
        "rgf_ratio": int(rgf / max_val * 100),
    }
    response = aiohttp_jinja2.render_template("index.html", request,
                                              context=context)

    return response


async def increment(request):
    user_id = request.match_info.get("userid")
    await request.app["db"].execute("INCR", user_id)
    raise web.HTTPFound(location="/")
    # return web.Response(text=str(await _get_score(request.app["db"], user_id)))


async def decrement(request: web.Request):
    user_id = request.match_info.get("userid")
    await request.app["db"].execute("DECR", user_id)
    raise web.HTTPFound(location="/")
    # return web.Response(text=str(await _get_score(request.app["db"], user_id)))


async def _get_score(db, key):
    score = await db.get(key)
    return int(score)


async def connect_to_db(app):
    app["db"] = await aioredis.create_redis(('redis', 6379), loop=app.loop)


def init():
    app = web.Application()
    app.add_routes([
        web.get('/', home),
        web.post('/inc/{userid}', increment),
        web.post('/dec/{userid}', decrement),
    ])

    app.on_startup.append(connect_to_db)

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
    )

    return app


if __name__ == '__main__':
    web.run_app(init())
