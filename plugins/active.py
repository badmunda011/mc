import datetime

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from config import Config
from Music.core.calls import Pbxmusic
from Music.core.clients import Pbxbot
from Music.core.database import db
from Music.core.decorators import check_mode
from Music.core.logger import LOGS
from Music.helpers.formatters import formatter
from Music.utils.pages import MakePages
from Music.utils.queue import Queue


@Pbxbot.app.on_message(filters.command("active") & Config.SUDO_USERS)
@check_mode
async def activevc(_, message: Message):
    Pbx = await message.reply_text(f"Getting active voice chats ...")
    active_chats = await db.get_active_vc()
    collection = []
    for x in active_chats:
        cid = int(x["chat_id"])
        if cid == 0:
            continue
        joined = x["join_time"]
        vc_type = x["vc_type"]
        participants = len(await Pbxmusic.vc_participants(cid))
        try:
            check = Queue.get_queue(cid)
            song = check[0]["title"]
        except Exception as e:
            LOGS.error(e)
            song = "Unknown"
        try:
            title = (await Pbxbot.app.get_chat(cid)).title
        except Exception:
            title = "Private Group"
        active_since = datetime.datetime.now() - joined
        total_secs = active_since.total_seconds()
        _hours = int(total_secs // 3600)
        _minutes = int(total_secs % 3600 // 60)
        context = {
            "chat_id": cid,
            "title": title,
            "participants": participants - 1,
            "active_since": f"{_hours} hrs, {_minutes} mins.",
            "playing": song,
            "vc_type": vc_type,
        }
        collection.append(context)
    if len(collection) == 0:
        return await Pbx.edit(f"No active voice chats found!")
    await MakePages.activevc_page(Pbx, collection, 0, 0, True)


@Pbxbot.app.on_callback_query(filters.regex(r"activevc") & ~Config.BANNED_USERS)
async def activevc_cb(_, cb: CallbackQuery):
    data = cb.data.split("|")
    cmd = data[1]
    page = int(data[2])
    collection = []
    active_chats = await db.get_active_vc()
    for x in active_chats:
        cid = int(x["chat_id"])
        if cid == 0:
            continue
        joined = x["join_time"]
        vc_type = x["vc_type"]
        participants = len(await Pbxmusic.vc_participants(cid))
        try:
            check = Queue.get_queue(cid)
            song = check[0]["title"]
        except Exception as e:
            LOGS.error(e)
            song = "Unknown"
        try:
            title = (await Pbxbot.app.get_chat(cid)).title
        except Exception:
            title = "Private Group"
        active_since = datetime.datetime.now() - joined
        total_secs = active_since.total_seconds()
        _hours = int(total_secs // 3600)
        _minutes = int(total_secs % 3600 // 60)
        context = {
            "chat_id": cid,
            "title": title,
            "participants": participants - 1,
            "active_since": f"{_hours} hrs, {_minutes} mins.",
            "playing": song,
            "vc_type": vc_type,
        }
        collection.append(context)
    last_page, _ = formatter.group_the_list(collection, length=True)
    last_page -= 1
    if page == 0 and cmd == "prev":
        new_page = last_page
    elif page == last_page and cmd == "next":
        new_page = 0
    else:
        new_page = page + 1 if cmd == "next" else page - 1
    index = new_page * 5
    await MakePages.activevc_page(cb, collection, new_page, index, True)
