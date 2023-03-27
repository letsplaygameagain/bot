
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from sqlalchemy.exc import IntegrityError
from Ubot.core.db import *
from . import *
from Ubot import TEMP_SETTINGS
from Ubot.core.SQL.globals import addgvar, gvarstatus
from ubotlibs.ubot.utils.tools import get_arg


DEF_UNAPPROVED_MSG = (
"╔═════════════════════╗\n"
"ㅤ   ⚡️ ᴡᴇʟᴄᴏᴍᴇ ⚡️\n"
"╚═════════════════════╝\n"
"➣ ᴊᴀɴɢᴀɴ  sᴘᴀᴍ  ᴄʜᴀᴛ  ᴛᴜᴀɴ  sᴀʏᴀ\n"
"➣ ᴀᴛᴀᴜ ᴀɴᴅᴀ ᴏᴛᴏᴍᴀᴛɪs  sᴀʏᴀ ʙʟᴏᴋɪʀ\n"
"╔═════════════════════╗\n"
"  ㅤ     ⚡𝕡𝕖𝕤𝕒𝕟  𝕠𝕥𝕠𝕞𝕒𝕥𝕚𝕤⚡\n"
"     ㅤ  𝙽𝙰𝚈𝙰-𝙿𝚁𝙾𝙹𝙴𝙲𝚃ㅤㅤ  \n"
"╚═════════════════════╝"
)


@Client.on_message(
    ~filters.me & filters.private & ~filters.bot & filters.incoming, group=69
)
async def incomingpm(client, message):
    try:
        from Ubot.core.SQL.globals import gvarstatus
        from Ubot.core.SQL.pm_permit_sql import is_approved
    except BaseException:
        pass
    user_id = message.from_user.id
    if gvarstatus(str(user_id), "PMPERMIT") and gvarstatus(str(user_id), "PMPERMIT") == "false":
        return
    if await auto_accept(client, message) or message.from_user.is_self:
        message.continue_propagation()
    if message.chat.id != 777000:
        PM_LIMIT = gvarstatus(str(user_id), "PM_LIMIT") or 5
        getmsg = gvarstatus(str(user_id), "unapproved_msg")
        if getmsg is not None:
            UNAPPROVED_MSG = getmsg
        else:
            UNAPPROVED_MSG = DEF_UNAPPROVED_MSG

        apprv = is_approved(message.chat.id)
        if not apprv and message.text != UNAPPROVED_MSG:
            if message.chat.id in TEMP_SETTINGS["PM_LAST_MSG"]:
                prevmsg = TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id]
                if message.text != prevmsg:
                    async for message in client.search_messages(
                        message.chat.id,
                        from_user="me",
                        limit=5,
                        query=UNAPPROVED_MSG,
                    ):
                        await message.delete()
                    if TEMP_SETTINGS["PM_COUNT"][message.chat.id] < (int(PM_LIMIT) - 1):
                        ret = await message.reply_text(UNAPPROVED_MSG)
                        TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] = ret.text
            else:
                ret = await message.reply_text(UNAPPROVED_MSG)
                if ret.text:
                    TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] = ret.text
            if message.chat.id not in TEMP_SETTINGS["PM_COUNT"]:
                TEMP_SETTINGS["PM_COUNT"][message.chat.id] = 1
            else:
                TEMP_SETTINGS["PM_COUNT"][message.chat.id] = (
                    TEMP_SETTINGS["PM_COUNT"][message.chat.id] + 1
                )
            if TEMP_SETTINGS["PM_COUNT"][message.chat.id] > (int(PM_LIMIT) - 1):
                await message.reply("**Maaf anda Telah Di Blokir Karna Spam Chat**")
                try:
                    del TEMP_SETTINGS["PM_COUNT"][message.chat.id]
                    del TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id]
                except BaseException:
                    pass

                await client.block_user(message.chat.id)

    message.continue_propagation()


async def auto_accept(client, message):
    try:
        from Ubot.core.SQL.pm_permit_sql import approve, is_approved
    except BaseException:
        pass

    if message.chat.id in DEVS:
        try:
            approve(message.chat.id)
            await client.send_message(
                message.chat.id,
                f"<b>Menerima Pesan!!!</b>\n{message.from_user.mention} <b>Terdeteksi Developer Naya-Project</b>",
                parse_mode=enums.ParseMode.HTML,
            )
        except IntegrityError:
            pass
    if message.chat.id not in [client.me.id, 777000]:
        if is_approved(message.chat.id):
            return True

        async for msg in client.get_chat_history(message.chat.id, limit=1):
            if msg.from_user.id == client.me.id:
                try:
                    del TEMP_SETTINGS["PM_COUNT"][message.chat.id]
                    del TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id]
                except BaseException:
                    pass

                try:
                    approve(chat.id)
                    async for message in client.search_messages(
                        message.chat.id,
                        from_user="me",
                        limit=5,
                        query=UNAPPROVED_MSG,
                    ):
                        await message.delete()
                    return True
                except BaseException:
                    pass

    return False


@Ubot(["ok", "y"], "")
async def approvepm(client, message):
    try:
        from Ubot.core.SQL.pm_permit_sql import approve
    except BaseException:
        await message.edit("Running on Non-SQL mode!")
        return

    if message.reply_to_message:
        reply = message.reply_to_message
        replied_user = reply.from_user
        if replied_user.is_self:
            await message.reply("Anda tidak dapat menyetujui diri sendiri.")
            return
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        uid = replied_user.id
    else:
        aname = message.chat
        if not aname.type == enums.ChatType.PRIVATE:
            await message.reply(
                "Saat ini Anda tidak sedang dalam PM dan Anda belum membalas pesan seseorang."
            )
            return
        name0 = aname.first_name
        uid = aname.id

    try:
        approve(uid)
        await message.reply(f"**Menerima Pesan Dari** [{name0}](tg://user?id={uid})!")
    except IntegrityError:
        await message.reply(
            f"[{name0}](tg://user?id={uid}) mungkin sudah disetujui untuk PM."
        )
        return


@Ubot(["no", "g"], "")
async def disapprovepm(client, message):
    try:
        from Ubot.core.SQL.pm_permit_sql import dissprove
    except BaseException:
        await message.edit("Running on Non-SQL mode!")
        return

    if message.reply_to_message:
        reply = message.reply_to_message
        replied_user = reply.from_user
        if replied_user.is_self:
            await message.reply("Anda tidak bisa menolak diri sendiri.")
            return
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        uid = replied_user.id
    else:
        aname = message.chat
        if not aname.type == enums.ChatType.PRIVATE:
            await message.reply(
                "Saat ini Anda tidak sedang dalam PM dan Anda belum membalas pesan seseorang."
            )
            return
        name0 = aname.first_name
        uid = aname.id

    dissprove(uid)

    await message.reply(
        f"**Pesan** [{name0}](tg://user?id={uid}) **Telah Ditolak, Mohon Jangan Melakukan Spam Chat!**"
    )


@Ubot(["setlimit"], "")
async def setpm_limit(client, message):
    user_id = client.me.id
    try:
        from Ubot.core.SQL.globals import addgvar
    except AttributeError:
        await message.edit("**Running on Non-SQL mode!**")
        return
    input_str = (
        message.text.split(None, 1)[1]
        if len(
            message.command,
        )
        != 1
        else None
    )
    if not input_str:
        return await message.reply("**Harap masukan angka untuk PM_LIMIT.**")
    kuy = await message.reply("`Processing...`")
    if input_str and not input_str.isnumeric():
        return await kuy.edit("**Harap masukan angka untuk PM_LIMIT.**")
    
    addgvar(str(user_id), "PM_LIMIT", input_str)
    await kuy.edit(f"**Set PM limit to** `{input_str}`")


@Ubot(["pmpermit"], "")
async def onoff_pmpermit(client, message):
    blok = get_arg(message)
    if not blok:
        await message.reply("**Gunakan format**:\n `antipm` on atau off")
        return
    elif blok == "off":
        tai = False
    elif blok == "on":
        tai = True
    user_id = client.me.id
    if gvarstatus(str(user_id), "PMPERMIT") and gvarstatus(str(user_id), "PMPERMIT") == "false":
        PMPERMIT = False
    else:
        PMPERMIT = True
    if PMPERMIT:
        if tai:
            await message.reply("**PMPERMIT Sudah Diaktifkan**")
        else:
            addgvar(str(user_id), "PMPERMIT", tai)
            await message.edit("**PMPERMIT Berhasil Dimatikan**")
    elif tai:
        addgvar(str(user_id), "PMPERMIT", tai)
        await message.edit("**PMPERMIT Berhasil Diaktifkan**")
    else:
        await message.edit("**PMPERMIT Sudah Dimatikan**")


@Ubot(["setpm"], "")
async def setpmpermit(client, message):
    user_id = client.me.id
    try:
        import Ubot.core.SQL.globals as sql
    except AttributeError:
        await message.edit("**Running on Non-SQL mode!**")
        return
    sempak = await message.reply("`Processing...`")
    nob = gvarstatus(str(user_id), "UNAPPROVED_MSG")
    message = message.reply_to_message
    if nob is not None:
        delgvar(str(user_id), "UNAPPROVED_MSG")
    if not message:
        return await sempak.edit("**Mohon Balas Ke Pesan**")
    msg = message.text
    addgvar(str(user_id), "UNAPPROVED_MSG", msg)
    
    await asyncio.sleep(0.1)
    await sempak.edit("**Pesan Berhasil Disimpan**")


@Ubot(["getpm"], "")
async def get_pmermit(client, message):
    user_id = client.me.id
    try:
        import Ubot.core.SQL.globals as sql
    except AttributeError:
        await message.edit("**Running on Non-SQL mode!**")
        return
    wow = await message.reply("`Processing...`")
    nob = sql.gvarstatus(str(user_id), "UNAPPROVED_MSG")
    if nob is not None:
        await wow.edit("**Pesan PMPERMIT Yang Sekarang:**" f"\n\n{nob}")
    else:
        
        await wow.edit(
            "**Anda Belum Menyetel Pesan Costum PMPERMIT,**\n"
            f"**Masih Menggunakan Pesan PM Default:**\n\n{DEF_UNAPPROVED_MSG}"
        )


@Ubot(["resetpm"], "")
async def reset_pmpermit(client, message):
    user_id = client.me.id
    try:
        import Ubot.core.SQL.globals as sql
    except AttributeError:
        await message.edit("**Running on Non-SQL mode!**")
        return
    wah = await message.reply("`Processing...`")
    nob = sql.gvarstatus(str(_user_id), "UNAPPROVED_MSG")

    if nob is None:
        await wah.edit("**Pesan Antipm Anda Sudah Default**")
    else:
        sql.delgvar(str(user_id), "UNAPPROVED_MSG")
        await wah.edit("**Berhasil Mengubah Pesan Custom Antipm menjadi Default**")


add_command_help(
    "antipm",
    [
        [
            f"ok atau y",
            "Menerima pesan seseorang dengan cara balas pesannya atau tag dan juga untuk dilakukan di pm",
        ],
        [
            f"no atau g",
            "Menolak pesan seseorang dengan cara balas pesannya atau tag dan juga untuk dilakukan di pm",
        ],
        [
            "setlimit <angka>",
            "Untuk mengcustom pesan limit auto block pesan",
        ],
        [
            "setpm <balas ke pesan>",
            "Untuk mengcustom pesan PMPERMIT untuk orang yang pesannya belum diterima.",
        ],
        [
            "getpm",
            "Untuk melihat pesan PMPERMIT.",
        ],
        [
            "resetpm",
            "Untuk Mereset Pesan PMPERMIT menjadi DEFAULT",
        ],
        [
            "pmpermit [on/off]",
            "Untuk mengaktifkan atau menonaktifkan PMPERMIT",
        ],
    ],
)
