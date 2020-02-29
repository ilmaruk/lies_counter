import os
from datetime import datetime

import aiohttp_jinja2
import aioredis
import jinja2
from aiohttp import web


async def home(request):
    db = request.app["db"]
    ebj = await _get_score(db, "ebj")
    rgf = await _get_score(db, "rgf")
    max_val = max(ebj, rgf)
    ebj_ratio = int(ebj / max_val * 100) if max_val > 0 else 100
    rgf_ratio = int(rgf / max_val * 100) if max_val > 0 else 100

    lu = await db.get("last_updated")
    lu = lu.decode("utf-8") if lu is not None else "never"

    context = {
        "ebj": ebj,
        "ebj_ratio": ebj_ratio,
        "rgf": rgf,
        "rgf_ratio": rgf_ratio,
        "last_updated": lu,
    }
    response = aiohttp_jinja2.render_template("index.html", request,
                                              context=context)

    return response


async def increment(request):
    user_id = request.match_info.get("userid")
    if user_id == "ebj":
        await request.app["db"].execute("INCR", user_id)
        await _set_last_updated(request.app["db"])
    raise web.HTTPFound(location="/")


async def decrement(request: web.Request):
    user_id = request.match_info.get("userid")
    if user_id == "rgf":
        await request.app["db"].execute("DECR", user_id)
        await _set_last_updated(request.app["db"])
    raise web.HTTPFound(location="/")


async def _get_score(db, key):
    score = await db.get(key)
    return int(score) if score is not None else 0


async def _set_last_updated(db):
    await db.set("last_updated", str(datetime.now()))


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
