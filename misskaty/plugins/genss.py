"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import os
import time
import traceback
from asyncio import gather, sleep
from logging import getLogger
from shutil import rmtree

from pyrogram import enums, filters
from pyrogram.errors import FloodWait

from misskaty import BOT_USERNAME, app
from misskaty.core.message_utils import *
from misskaty.core.decorator.pyro_cooldown import wait
from misskaty.core.decorator.errors import capture_err
from misskaty.helper import genss_link, progress_for_pyrogram, take_ss
from misskaty.vars import COMMAND_HANDLER

LOGGER = getLogger(__name__)

__MODULE__ = "MediaTool"
__HELP__ = """"
/genss [reply to video] - Generate Screenshot From Video.
/genss_link [link] - Generate Screenshot Video From URL. (Unstable)
/mediainfo [link/reply to TG Video] - Get Mediainfo From File.
"""


@app.on_message(filters.command(["genss"], COMMAND_HANDLER) & wait(30))
@capture_err
async def genss(client, m):
    replied = m.reply_to_message
    if replied is not None:
        vid = [replied.video, replied.document]
        media = next((v for v in vid if v is not None), None)
        if media is None:
            return await kirimPesan(m, "Reply to a Telegram Video or document as video to generate screenshoot!")
        process = await kirimPesan(m, "`Processing, please wait..`")

        c_time = time.time()
        the_real_download_location = await replied.download(
            progress=progress_for_pyrogram,
            progress_args=("Trying to download, please wait..", process, c_time),
        )
        if the_real_download_location is not None:
            try:
                await editPesan(process, f"File video berhasil didownload dengan path <code>{the_real_download_location}</code>.")
                await sleep(2)
                images = await take_ss(the_real_download_location)
                await editPesan(process, "Mencoba mengupload, hasil generate screenshot..")
                await client.send_chat_action(chat_id=m.chat.id, action=enums.ChatAction.UPLOAD_PHOTO)

                try:
                    await gather(
                        *[
                            m.reply_document(images, reply_to_message_id=m.id),
                            m.reply_photo(images, reply_to_message_id=m.id),
                        ]
                    )
                except FloodWait as e:
                    await sleep(e.value)
                    await gather(
                        *[
                            m.reply_document(images, reply_to_message_id=m.id),
                            m.reply_photo(images, reply_to_message_id=m.id),
                        ]
                    )
                await kirimPesan(
                    m, f"☑️ Uploaded [1] screenshoot.\n\n{m.from_user.first_name} (<code>{m.from_user.id}</code>)\n#️⃣ #ssgen #id{message.from_user.id}\n\nSS Generate by @{BOT_USERNAME}",
                    reply_to_message_id=m.id,
                )
                await process.delete()
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
            except Exception:
                exc = traceback.format_exc()
                await kirimPesan(m, f"Gagal generate screenshot.\n\n{exc}")
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
    else:
        await kirimPesan(m, "Reply to a Telegram media to get screenshots from media..")


@app.on_message(filters.command(["genss_link"], COMMAND_HANDLER))
@capture_err
async def genss_link(client, m):
    if len(m.command) == 1:
        return await kirimPesan(m, f"Use <code>/{m.command[0]} link</code> to generate screenshot from URL.")
    try:
        link = m.text.split(" ")[1]
        process = await kirimPesan(m, "`Processing, please wait..`")
        tmp_directory_for_each_user = f"./MissKaty_Genss/{str(m.from_user.id)}"
        if not os.path.isdir(tmp_directory_for_each_user):
            os.makedirs(tmp_directory_for_each_user)
        images = await genss_link(process, link, tmp_directory_for_each_user, 5, 8)
        await sleep(2)
        await editPesan(process, "Mencoba mengupload, hasil generate screenshot..")
        await client.send_chat_action(chat_id=m.chat.id, action=enums.ChatAction.UPLOAD_PHOTO)
        try:
            await m.reply_media_group(images, reply_to_message_id=m.id)
        except FloodWait as e:
            await sleep(e.value)
            await m.reply_media_group(images, reply_to_message_id=m.id)
        await kirimPesan(
            m,
            f"☑️ Uploaded [8] screenshoot.\n\nGenerated by @{BOT_USERNAME}.",
            reply_to_message_id=m.id,
        )
        await process.delete()
        try:
            rmtree(tmp_directory_for_each_user)
        except:
            pass
    except Exception:
        exc = traceback.format_exc()
        await kirimPesan(m, f"Gagal generate screenshot.\n\n{exc}")
        try:
            rmtree(tmp_directory_for_each_user)
        except:
            pass
