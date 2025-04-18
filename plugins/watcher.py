import asyncio
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.types import JoinedGroupCallParticipant, LeftGroupCallParticipant, Update
from pytgcalls.types.stream import StreamAudioEnded

from config import Config
from Music.core.calls import Pbxmusic
from Music.core.clients import Pbxbot
from Music.core.database import db
from Music.core.logger import LOGS
from Music.helpers.buttons import Buttons
from Music.utils.leaderboard import leaders
from Music.utils.queue import Queue


@Pbxbot.app.on_message(filters.private, group=2)
async def new_users(_, msg: Message):
    chat_id = msg.from_user.id
    user_name = msg.from_user.first_name
    if not await db.is_user_exist(chat_id):
        BOT_USERNAME = Pbxbot.app.username
        await db.add_user(chat_id, user_name)
        if Config.LOGGER_ID:
            await Pbxbot.logit(
                "newuser",
                f"**⤷ User:** {msg.from_user.mention(style='md')}\n**⤷ ID:** `{chat_id}`\n__⤷ Started @{BOT_USERNAME} !!__",
            )
        else:
            LOGS.info(f"#NewUser: \n\nName: {user_name} \nID: {chat_id}")
    else:
        try:
            await db.update_user(chat_id, "user_name", user_name)
        except:
            pass
    await msg.continue_propagation()


@Pbxbot.app.on_message(filters.group, group=3)
async def new_users(_, msg: Message):
    chat_id = msg.chat.id
    if not await db.is_chat_exist(chat_id):
        BOT_USERNAME = Pbxbot.app.username
        await db.add_chat(chat_id)
        if Config.LOGGER_ID:
            await Pbxbot.logit(
                "newchat",
                f"**⤷ Chat Title:** {msg.chat.title} \n**⤷ Chat UN:** @{msg.chat.username or None}) \n**⤷ Chat ID:** `{chat_id}` \n__⤷ ADDED @{BOT_USERNAME} !!__",
            )
        else:
            LOGS.info(
                f"#NEWCHAT: \n\nChat Title: {msg.chat.title} \nChat UN: @{msg.chat.username}) \nChat ID: {chat_id} \n\nADDED @{BOT_USERNAME} !!",
            )
    await msg.continue_propagation()


@Pbxbot.app.on_message(filters.video_chat_ended, group=4)
async def vc_end(_, msg: Message):
    chat_id = msg.chat.id
    try:
        await Pbxmusic.leave_vc(chat_id)
        await db.set_loop(chat_id, 0)
    except:
        pass
    await msg.continue_propagation()


@Pbxmusic.music.on_kicked()
@Pbxmusic.music.on_left()
async def end_streaming(_, chat_id: int):
    await Pbxmusic.leave_vc(chat_id)
    await db.set_loop(chat_id, 0)


@Pbxmusic.music.on_stream_end()
async def changed(_, update: Update):
    if isinstance(update, StreamAudioEnded):
        await Pbxmusic.change_vc(update.chat_id)


@Pbxmusic.music.on_participants_change()
async def members_change(_, update: Update):
    if not isinstance(update, JoinedGroupCallParticipant) and not isinstance(
        update, LeftGroupCallParticipant
    ):
        return
    try:
        chat_id = update.chat_id
        audience = Pbxmusic.audience.get(chat_id)
        users = await Pbxmusic.vc_participants(chat_id)
        user_ids = [user.user_id for user in users]
        if not audience:
            await Pbxmusic.autoend(chat_id, user_ids)
        else:
            new = (
                audience + 1
                if isinstance(update, JoinedGroupCallParticipant)
                else audience - 1
            )
            Pbxmusic.audience[chat_id] = new
            await Pbxmusic.autoend(chat_id, user_ids)
    except:
        return

async def change_vc(self, chat_id: int):
    try:
        get = Queue.get_queue(chat_id)
        if not get:
            return await self.leave_vc(chat_id)

        loop = await db.get_loop(chat_id)
        if loop == 0:
            file = Queue.rm_queue(chat_id, 0)
            await self.autoclean(file)
        else:
            await db.set_loop(chat_id, loop - 1)

        get = Queue.get_queue(chat_id)
        if not get:
            return await self.leave_vc(chat_id)

        chat_id = get[0]["chat_id"]
        queue = get[0]["file"]
        title = get[0]["title"]
        vc_type = get[0]["vc_type"]
        video_id = get[0]["video_id"]

        if not os.path.exists(queue):
            raise ChangeVCException(f"File not found: {queue}")

        if vc_type == "video":
            input_stream = AudioVideoPiped(queue, MediumQualityAudio(), MediumQualityVideo())
        else:
            input_stream = AudioPiped(queue, MediumQualityAudio())

        await self.music.change_stream(chat_id, input_stream)

    except FileNotFoundError as e:
        LOGS.error(f"File not found: {e}")
        return await self.leave_vc(chat_id)

    except Exception as e:
        LOGS.error(e)
        return await self.leave_vc(chat_id)


async def update_played():
    while not await asyncio.sleep(1):
        active_chats = await db.get_active_vc()
        for x in active_chats:
            chat_id = int(x["chat_id"])
            if chat_id == 0:
                continue
            is_paused = await db.get_watcher(chat_id, "pause")
            if is_paused:
                continue
            que = Queue.get_queue(chat_id)
            if que == []:
                continue
            Queue.update_duration(chat_id, 1, 1)


asyncio.create_task(update_played())


async def end_inactive_vc():
    while not await asyncio.sleep(10):
        for chat_id in db.inactive:
            dur = db.inactive.get(chat_id)
            if dur == {}:
                continue
            if datetime.datetime.now() > dur:
                if not await db.is_active_vc(chat_id):
                    db.inactive[chat_id] = {}
                    continue
                db.inactive[chat_id] = {}
                try:
                    await Pbxmusic.leave_vc(chat_id)
                except:
                    continue
                try:
                    await Pbxbot.app.send_message(
                        chat_id,
                        "⏹️ **Inactive VC:** Streaming has been stopped!",
                    )
                except:
                    continue


asyncio.create_task(end_inactive_vc())


async def leaderboard():
    context = {
        "mention": Pbxbot.app.mention,
        "username": Pbxbot.app.username,
        "client": Pbxbot.app,
    }
    text = await leaders.generate(context)
    btns = Buttons.close_markup()
    await leaders.broadcast(Pbxbot, text, btns)


hrs = leaders.get_hrs()
min = leaders.get_min()

scheduler = AsyncIOScheduler()
scheduler.add_job(leaderboard, "cron", hour=hrs, minute=min, timezone=Config.TZ)
scheduler.start()
