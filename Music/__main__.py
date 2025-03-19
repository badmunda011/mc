from pyrogram import idle

from config import Config
from Music.core.calls import Pbxmusic
from Music.core.clients import Pbxbot
from Music.core.database import db
from Music.core.logger import LOGS
from Music.core.users import user_data
from Music.helpers.strings import TEXTS
from Music.version import __version__


async def start_bot():
    pmusic_version = __version__["Pbx Music"]
    py_version = __version__["Python"]
    pyro_version = __version__["Pyrogram"]
    pycalls_version = __version__["PyTgCalls"]

    LOGS.info("\x41\x6c\x6c\x20\x43\x68\x65\x63\x6b\x73\x20\x43\x6f\x6d\x70\x6c\x65\x74\x65\x64\x21\x20\x4c\x65\x74\x27\x73\x20\x53\x74\x61\x72\x74\x20\x50\x62\x78\x2d\x4d\x75\x73\x69\x63\x2e\x2e\x2e")

    await user_data.setup()
    await Pbxbot.start()
    await Pbxmusic.start()
    await db.connect()

    try:
        if Config.BOT_PIC:
            await Pbxbot.app.send_photo(
                int(Config.LOGGER_ID),
                Config.BOT_PIC,
                TEXTS.BOOTED.format(
                    Config.BOT_NAME,
                    pmusic_version,
                    py_version,
                    pyro_version,
                    pycalls_version,
                    Pbxbot.app.mention(style="md"),
                ),
            )
        else:
            await Pbxbot.app.send_message(
                int(Config.LOGGER_ID),
                TEXTS.BOOTED.format(
                    Config.BOT_NAME,
                    pmusic_version,
                    py_version,
                    pyro_version,
                    pycalls_version,
                    Pbxbot.app.mention(style="md"),
                ),
            )
    except Exception as e:
        LOGS.warning(f"\x45\x72\x72\x6f\x72\x20\x69\x6e\x20\x4c\x6f\x67\x67\x65\x72\x3a\x20{e}")

    LOGS.info(f"\x3e\x3e\x20\x50\x62\x78\x2d\x4d\x75\x73\x69\x63\x20\x5b{pmusic_version}\x5d\x20\x69\x73\x20\x6e\x6f\x77\x20\x6f\x6e\x6c\x69\x6e\x65\x21")

    await idle()

    await Pbxbot.app.send_message(
        Config.LOGGER_ID,
        f"\x23\x53\x54\x4f\x50\x5c\x6e\x5c\x6e\x2a\x2a\x50\x62\x78\x2d\x4d\x75\x73\x69\x63\x20\x5b{pmusic_version}\x5d\x20\x69\x73\x20\x6e\x6f\x77\x20\x6f\x66\x66\x6c\x69\x6e\x65\x21\x2a\x2a",
    )
    LOGS.info(f"\x50\x62\x78\x2d\x4d\x75\x73\x69\x63\x20\x5b{pmusic_version}\x5d\x20\x69\x73\x20\x6e\x6f\x77\x20\x6f\x66\x66\x6c\x69\x6e\x65\x21")


if __name__ == "__main__":
    Pbxbot.run(start_bot())
