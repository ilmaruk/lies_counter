import os
from datetime import datetime

import aiohttp_jinja2
import aioredis
import jinja2
from aiohttp import web


async def _get_context(db):
    ebj = await _get_score(db, "ebj")
    rgf = await _get_score(db, "rgf")
    max_val = max(ebj, rgf)
    ebj_ratio = int(ebj / max_val * 100) if max_val > 0 else 100
    rgf_ratio = int(rgf / max_val * 100) if max_val > 0 else 100

    lu = await db.get("last_updated")
    lu = lu.decode("utf-8") if lu is not None else "never"

    ip = await db.get("last_ip")
    ip = ip.decode("utf-8") if ip is not None else "nowhere"

    return {
        "ebj": ebj,
        "ebj_ratio": ebj_ratio,
        "rgf": rgf,
        "rgf_ratio": rgf_ratio,
        "last_updated": lu,
        "last_ip": ip,
    }


async def home(request):
    context = await _get_context(request.app["db"])
    return aiohttp_jinja2.render_template("index.html", request, context=context)


async def increment(request: web.Request):
    if _validate_user_agent(request):
        user_id = request.match_info.get("userid")
        await request.app["db"].execute("INCR", user_id)
    await _set_last(request.app["db"], request)
    raise web.HTTPFound(location="/")


async def decrement(request: web.Request):
    if _validate_user_agent(request):
        user_id = request.match_info.get("userid")
        await request.app["db"].execute("DECR", user_id)
    await _set_last(request.app["db"], request)
    raise web.HTTPFound(location="/")


def _validate_user_agent(request: web.Request) -> bool:
    ua = request.headers.get("user-agent")  # str
    return ua.find("Linux") != -1


async def _get_score(db, key):
    score = await db.get(key)
    return int(score) if score is not None else 0


async def _set_last(db, request: web.Request):
    await db.set("last_updated", str(datetime.now()))
    await db.set("last_ip", request.remote)


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
