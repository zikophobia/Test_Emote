#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================
# بوت منفصل لأمر /ms
# الإصدار: 1.0
# ============================

import requests, os, sys, jwt, pickle, json, binascii, time, urllib3, base64, datetime, re, socket, threading, ssl, pytz, aiohttp
from protobuf_decoder.protobuf_decoder import Parser
from xC4 import *
from xHeaders import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from Pb2 import DEcwHisPErMsG_pb2, MajoRLoGinrEs_pb2, PorTs_pb2, MajoRLoGinrEq_pb2, sQ_pb2, Team_msg_pb2
from cfonts import render, say
import asyncio
import signal
import sys
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Telegram Bot Imports
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ------------------- إعدادات ثابتة (غيّرها حسب حسابك) -------------------
# حساب Garena الذي سيستخدمه هذا البوت (يجب أن يكون مختلفاً عن البوت الأساسي)
ACCOUNT_UID = "4357299491"          # استبدل بمعرف حسابك الجديد
ACCOUNT_PW  = "6A6822FB908387D500640BD4B06C1B9C2E36D339348A2A7D2296C3133801C051"  # كلمة المرور

# توكن بوت التلغرام الخاص بهذا البوت (يمكنك استخدام نفس التوكن أو توكن جديد)
BOT_TOKEN = "8248104861:AAEmzo4Bx2Ss6uiT3zma4CbCUnU717tRIEw"
ADMIN_TELEGRAM_ID = 6848455321
BASE_WEBHOOK_URL = "https://botemot-2.onrender.com"   # غيّره حسب رابطك

# قنوات الاشتراك (اختياري، يمكن تعطيلها)
REQUIRED_CHANNEL = "@Ziko_Tim"
REQUIRED_GROUP = "@MTX_SX_CHAT_TEAM"

# ------------------- المتغيرات العامة -------------------
online_writer = None
whisper_writer = None
insquad = None
joining_team = False
telegram_bot_running = False
telegram_bot = None
telegram_dp = None

# --- المفاتيح والإعدادات التي ستملأها دوال اللعبة ---
key = None
iv = None
region = None

# --- المتغير الخاص بتخزين آخر chat_id تم استقباله ---
current_chat_id = None

# ------------------- دوال مساعدة -------------------
def get_random_color():
    colors = [
        "FF0000", "00FF00", "0000FF", "FFFF00", "FF00FF", "00FFFF", "FFFFFF", "FFA500",
        "A52A2A", "800080", "000000", "808080", "C0C0C0", "FFC0CB", "FFD700", "ADD8E6",
        "90EE90", "D2691E", "DC143C", "00CED1", "9400D3", "F08080", "20B2AA", "FF1493",
        "7CFC00", "B22222", "FF4500", "DAA520", "00BFFF", "00FF7F", "4682B4", "6495ED",
        "5F9EA0", "DDA0DD", "E6E6FA", "B0C4DE", "556B2F", "8FBC8F", "2E8B57", "3CB371",
        "6B8E23", "808000", "B8860B", "CD5C5C", "8B0000", "FF6347", "FF8C00", "BDB76B",
        "9932CC", "8A2BE2", "4B0082", "6A5ACD", "7B68EE", "4169E1", "1E90FF", "191970",
        "00008B", "000080", "008080", "008B8B", "B0E0E6", "AFEEEE", "E0FFFF", "F5F5DC",
        "FAEBD7"
    ]
    return random.choice(colors)

async def safe_send_message(chat_type, message, target_uid, chat_id, key, iv, max_retries=3):
    """إرسال رسالة بأمان مع إعادة المحاولة"""
    for attempt in range(max_retries):
        try:
            msg_packet = await xSEndMsgsQ(message, chat_id, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)
    return False

def get_subscription_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 القناة", url="https://t.me/Ziko_Tim")],
        [InlineKeyboardButton(text="💬 المجموعة", url="https://t.me/MTX_SX_CHAT_TEAM")],
        [InlineKeyboardButton(text="✅ تحقق", callback_data="check_sub")]
    ])
    return keyboard

# ------------------- دوال التحقق من الاشتراك (اختياري) -------------------
async def check_subscription(user_id: int) -> bool:
    try:
        channel_member = await telegram_bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        group_member = await telegram_bot.get_chat_member(REQUIRED_GROUP, user_id)
        return (channel_member.status not in ["left", "kicked"] and
                group_member.status not in ["left", "kicked"])
    except:
        return False

async def require_subscription(message: Message):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        return True
    if await check_subscription(message.from_user.id):
        return True
    else:
        await message.reply(
            f"⚠️ **عذراً، يجب عليك الاشتراك في القناة والمجموعة التاليتين لاستخدام البوت:**\n\n"
            f"📢 **القناة:** {REQUIRED_CHANNEL}\n"
            f"💬 **المجموعة:** {REQUIRED_GROUP}",
            reply_markup=get_subscription_keyboard()
        )
        return False

# ------------------- دوال التلغرام -------------------
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}/webhook")
    print(f"✅ Webhook set to {BASE_WEBHOOK_URL}/webhook")

async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.delete_webhook()
    print("❌ Webhook deleted")

async def telegram_startup():
    global telegram_bot, telegram_dp, telegram_bot_running
    logging.basicConfig(level=logging.INFO)
    telegram_bot = Bot(token=BOT_TOKEN)
    telegram_dp = Dispatcher()
    await register_handlers(telegram_dp)
    telegram_dp.startup.register(on_startup)
    telegram_dp.shutdown.register(on_shutdown)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=telegram_dp, bot=telegram_bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, telegram_dp, bot=telegram_bot)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🤖 بوت التلغرام يعمل على المنفذ {port} مع webhook")
    telegram_bot_running = True
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        await runner.cleanup()

# ------------------- معالجات الأوامر (فقط /start, /help, /ms, /join, /exit) -------------------
async def register_handlers(dp: Dispatcher):

    @dp.callback_query(lambda c: c.data == 'check_sub')
    async def process_callback_check_sub(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        if await check_subscription(user_id):
            await callback_query.answer("✅ تم التحقق بنجاح! يمكنك استخدام البوت الآن.")
            await callback_query.message.edit_text("✅ تم التحقق بنجاح!\nأرسل /help لبدء استخدام البوت.")
        else:
            await callback_query.answer("❌ لم تشترك بعد! اشترك ثم حاول مرة أخرى.", show_alert=True)

    @dp.message(Command("start"))
    async def start_cmd(message: Message):
        user_id = message.from_user.id
        chat_type = message.chat.type
        if user_id == ADMIN_TELEGRAM_ID:
            welcome_text = """
🔥 <b>MS BOT - للرسائل فقط</b> 🔥

━━━━━━━━━━━━━━━━━━━━━━

<b>🛠️ الأوامر المتاحة:</b>
/ms [team_code] [الرسالة] — إرسال رسالة ملونة في الفريق (4 مرات، 6 كلمات حد أقصى)
/join [team_code] — دخول الفريق يدوياً (للتجربة)
/exit — مغادرة الفريق الحالي

━━━━━━━━━━━━━━━━━━━━━━
👑 <b>Developer:</b> @ZikoB0SS
"""
            await message.reply(welcome_text, parse_mode="HTML")
            return
        if chat_type == "private":
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 Join Group", url="https://t.me/MTX_SX_CHAT_TEAM")]
            ])
            await message.reply(
                "🤖 <b>This bot works only in groups!</b>\n\n"
                "Please join our group to use the bot:",
                reply_markup=markup,
                parse_mode="HTML"
            )
            return
        if not await check_subscription(user_id):
            await message.reply(
                "🔒 **Subscription Required**\n\n"
                "Please join our channel and group to use the bot:",
                reply_markup=get_subscription_keyboard()
            )
            return
        commands_text = """
🔥 <b>MS BOT - للرسائل فقط</b> 🔥

━━━━━━━━━━━━━━━━━━━━━━

<b>📝 الأوامر:</b>
/ms [team_code] [الرسالة] — إرسال رسالة في الفريق
/join [team_code] — دخول الفريق يدوياً (للتجربة)
/exit — مغادرة الفريق الحالي

━━━━━━━━━━━━━━━━━━━━━━
👑 <b>Developer:</b> @ZikoB0SS
"""
        await message.reply(commands_text, parse_mode="HTML")

    @dp.message(Command("help"))
    async def help_cmd(message: Message):
        await start_cmd(message)

    # أمر /ms
    @dp.message(Command("ms"))
    async def ms_command(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.strip().split(maxsplit=2)
        if len(parts) < 3:
            await message.reply("❌ الاستخدام: /ms [team_code] [الرسالة] (حد 6 كلمات)")
            return
        team_code = parts[1]
        user_message = parts[2].strip()
        word_count = len(user_message.split())
        if word_count > 6:
            await message.reply(f"❌ الرسالة طويلة جداً! الحد 6 كلمات (لديك {word_count}).")
            return
        status_msg = await message.reply(f"🔄 إرسال إلى {team_code}...")
        asyncio.create_task(process_ms_command(
            team_code, user_message, key, iv, region,
            message.chat.id, status_msg.message_id, message.from_user.id
        ))

    # أمر /join للتجربة
    @dp.message(Command("join"))
    async def join_command(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ الاستخدام: /join [team_code]")
            return
        team_code = parts[1]
        status_msg = await message.reply(f"🔄 جاري الانضمام إلى {team_code}...")
        try:
            join_packet = await GenJoinSquadsPacket(team_code, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
            await telegram_bot.edit_message_text(f"✅ تم إرسال طلب الانضمام إلى {team_code}.", message.chat.id, status_msg.message_id)
        except Exception as e:
            await telegram_bot.edit_message_text(f"❌ خطأ: {str(e)}", message.chat.id, status_msg.message_id)

    # أمر /exit
    @dp.message(Command("exit"))
    async def exit_command(message: Message):
        if not await require_subscription(message):
            return
        try:
            exit_packet = await ExiT(None, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', exit_packet)
            await message.reply("✅ تم مغادرة الفريق.")
        except Exception as e:
            await message.reply(f"❌ خطأ: {str(e)}")

# ------------------- دالة معالجة /ms -------------------
async def process_ms_command(team_code: str, user_message: str, key, iv, region, chat_id: int, status_msg_id: int, user_id: int):
    global current_chat_id
    try:
        # إعادة تعيين current_chat_id قبل الانضمام
        current_chat_id = None

        # انضمام
        join_packet = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)

        # انتظار chat_id لمدة 10 ثوانٍ
        waited = 0
        while waited < 10 and current_chat_id is None:
            await asyncio.sleep(0.5)
            waited += 0.5

        if current_chat_id is None:
            raise Exception("لم يتم الحصول على معرف الدردشة بعد الانضمام")

        # إرسال الرسالة 4 مرات
        for i in range(4):
            color = get_random_color()
            colored_message = f"[B][C]{color} {user_message}"
            await safe_send_message(0, colored_message, user_id, current_chat_id, key, iv)
            await asyncio.sleep(0.5)

        # مغادرة
        exit_packet = await ExiT(None, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', exit_packet)

        # إعادة تعيين المتغير (اختياري)
        current_chat_id = None

        await telegram_bot.edit_message_text(f"✅ تم إرسال الرسالة إلى {team_code} (4 مرات).", chat_id, status_msg_id)
    except Exception as e:
        await telegram_bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, status_msg_id)

# ------------------- دوال الاتصال TCP (معدلة لالتقاط chat_id) -------------------
async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer, whisper_writer, insquad, joining_team, region, current_chat_id
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            writer.write(bytes.fromhex(AutHToKen))
            await writer.drain()
            print("تم إرسال رمز المصادقة. دخول في حلقة القراءة...")
            while True:
                data = await reader.read(9999)
                if not data:
                    print("تم إغلاق الاتصال.")
                    break
                # هنا يمكن إضافة معالجة إذا لزم الأمر
        except Exception as e:
            print(f"خطأ في TcPOnLine: {e}")
        finally:
            if online_writer:
                online_writer.close()
                await online_writer.wait_closed()
                online_writer = None
            await asyncio.sleep(reconnect_delay)

async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region, reconnect_delay=0.5):
    global whisper_writer, online_writer, current_chat_id
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            writer.write(bytes.fromhex(AutHToKen))
            await writer.drain()
            ready_event.set()
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                print(f"البوت في نقابة {clan_id}")
                pK = await AuthClan(clan_id, clan_compiled_data, key, iv)
                if whisper_writer:
                    whisper_writer.write(pK)
                    await whisper_writer.drain()
            while True:
                data = await reader.read(9999)
                if not data:
                    break
                # محاولة فك تشفير الرسالة واستخراج chat_id
                if data.hex().startswith("120000"):
                    try:
                        response = await DecodeWhisperMessage(data.hex()[10:])
                        if response:
                            # تحديث current_chat_id بأي chat_id نستقبله
                            current_chat_id = response.Data.Chat_ID
                            print(f"🆔 تم تحديث current_chat_id إلى: {current_chat_id}")
                    except:
                        pass
        except Exception as e:
            print(f"خطأ في TcPChaT: {e}")
        finally:
            if whisper_writer:
                whisper_writer.close()
                await whisper_writer.wait_closed()
                whisper_writer = None
            await asyncio.sleep(reconnect_delay)

# ------------------- الدالة الرئيسية -------------------
async def MaiiiinE():
    global key, iv, region
    open_id, access_token = await GeNeRaTeAccEss(ACCOUNT_UID, ACCOUNT_PW)
    if not open_id or not access_token:
        print("❌ فشل تسجيل الدخول بالحساب")
        return None

    PyL = await EncRypTMajoRLoGin(open_id, access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE:
        print("❌ الحساب محظور أو غير مسجل!")
        return None

    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    region = MajoRLoGinauTh.region
    ToKen = MajoRLoGinauTh.token
    TarGeT = MajoRLoGinauTh.account_uid
    key = MajoRLoGinauTh.key
    iv = MajoRLoGinauTh.iv
    timestamp = MajoRLoGinauTh.timestamp

    LoGinDaTa = await GetLoginData(UrL, PyL, ToKen)
    if not LoGinDaTa:
        print("❌ خطأ في الحصول على المنافذ")
        return None
    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)

    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port

    OnLineiP, OnLineporT = OnLinePorTs.split(":")
    ChaTiP, ChaTporT = ChaTPorTs.split(":")

    equie_emote(ToKen, UrL)
    AutHToKen = await xAuThSTarTuP(int(TarGeT), ToKen, int(timestamp), key, iv)
    ready_event = asyncio.Event()

    # تشغيل بوت التلغرام
    telegram_task = asyncio.create_task(telegram_startup())

    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region))
    task2 = asyncio.create_task(TcPOnLine(OnLineiP, OnLineporT, key, iv, AutHToKen))

    print("🤖 بوت MS - متصل")
    print(f"🔹 المعرف: {TarGeT}")
    print("🔹 الحالة: 🟢 جاهز")

    await asyncio.gather(task1, task2, telegram_task)

# ------------------- معالجة إشارة الإيقاف -------------------
def handle_keyboard_interrupt(signum, frame):
    print("\n🛑 إيقاف البوت...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_keyboard_interrupt)

async def StarTinG():
    while True:
        try:
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)
        except KeyboardInterrupt:
            print("\n🛑 تم الإيقاف بواسطة المستخدم")
            break
        except asyncio.TimeoutError:
            print("انتهت صلاحية الرمز! إعادة التشغيل")
        except Exception as e:
            print(f"خطأ عام - إعادة التشغيل: {e}")

if __name__ == '__main__':
    asyncio.run(StarTinG())