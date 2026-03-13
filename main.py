#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from APIS import insta
from flask import Flask, jsonify, request
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

# ------------------- الإعدادات الثابتة -------------------
ADMIN_UID = "8804135237"
server2 = "BD"
key2 = "mg24"
BYPASS_TOKEN = "your_bypass_token_here"

# ضع توكن البوت هنا مباشرة
BOT_TOKEN = "8248104861:AAEmzo4Bx2Ss6uiT3zma4CbCUnU717tRIEw"
ADMIN_TELEGRAM_ID = 6848455321
BASE_WEBHOOK_URL = "https://test-emote-y9hd.onrender.com"   # <- تم التعديل حسب رابطك الجديد

# قنوات الاشتراك الإجباري
REQUIRED_CHANNEL = "@Ziko_Tim"
REQUIRED_GROUP = "@MTX_SX_CHAT_TEAM"

# ------------------- المتغيرات العامة -------------------
online_writer = None
whisper_writer = None
insquad = None
joining_team = False
lag_running = False
lag_task = None
telegram_bot_running = False
telegram_bot = None
telegram_dp = None

# --- المتغيرات العامة التي تحتاجها دوال الأوامر ---
key = None
iv = None
region = None

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
    """Safely send message with retry mechanism"""
    for attempt in range(max_retries):
        try:
            P = await SEndMsG(chat_type, message, target_uid, chat_id, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
            return True
        except Exception as e:
            print(f"فشل إرسال الرسالة (محاولة {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)
    return False

async def SEndMsG(chat_type, message, target_uid, chat_id, key, iv):
    """Send message based on chat type"""
    if chat_type == 0:  # Squad
        return await xSEndMsgsQ(message, chat_id, key, iv)
    elif chat_type == 1:  # Clan
        return await xSEndMsg(message, 1, chat_id, chat_id, key, iv)
    else:  # Private
        return await xSEndMsg(message, 2, target_uid, target_uid, key, iv)

# ------------------- تعيينات الإيموجيات -------------------
ALL_EMOTE = {1: 909000001, 2: 909000002, 3: 909000003, 4: 909000004, 5: 909000005, 6: 909000006, 7: 909000007, 8: 909000008, 9: 909000009, 10: 909000010, 11: 909000011, 12: 909000012, 13: 909000013, 14: 909000014, 15: 909000015, 16: 909000016, 17: 909000017, 18: 909000018, 19: 909000019, 20: 909000020, 21: 909000021, 22: 909000022, 23: 909000023, 24: 909000024, 25: 909000025, 26: 909000026, 27: 909000027, 28: 909000028, 29: 909000029, 30: 909000031, 31: 909000032, 32: 909000033, 33: 909000034, 34: 909000035, 35: 909000036, 36: 909000037, 37: 909000038, 38: 909000039, 39: 909000040, 40: 909000041, 41: 909000042, 42: 909000043, 43: 909000044, 44: 909000045, 45: 909000046, 46: 909000047, 47: 909000048, 48: 909000049, 49: 909000051, 50: 909000052, 51: 909000053, 52: 909000054, 53: 909000055, 54: 909000056, 55: 909000057, 56: 909000058, 57: 909000059, 58: 909000060, 59: 909000061, 60: 909000062, 61: 909000063, 62: 909000064, 63: 909000065, 64: 909000066, 65: 909000067, 66: 909000068, 67: 909000069, 68: 909000070, 69: 909000071, 70: 909000072, 71: 909000073, 72: 909000074, 73: 909000075, 74: 909000076, 75: 909000077, 76: 909000078, 77: 909000079, 78: 909000080, 79: 909000081, 80: 909000082, 81: 909000083, 82: 909000084, 83: 909000085, 84: 909000086, 85: 909000087, 86: 909000088, 87: 909000089, 88: 909000090, 89: 909000091, 90: 909000092, 91: 909000093, 92: 909000094, 93: 909000095, 94: 909000096, 95: 909000097, 96: 909000098, 97: 909000099, 98: 909000100, 99: 909000101, 100: 909000102, 101: 909000103, 102: 909000104, 103: 909000105, 104: 909000106, 105: 909000107, 106: 909000108, 107: 909000109, 108: 909000110, 109: 909000111, 110: 909000112, 111: 909000113, 112: 909000114, 113: 909000115, 114: 909000116, 115: 909000117, 116: 909000118, 117: 909000119, 118: 909000120, 119: 909000121, 120: 909000122, 121: 909000123, 122: 909000124, 123: 909000125, 124: 909000126, 125: 909000127, 126: 909000128, 127: 909000129, 128: 909000130, 129: 909000131, 130: 909000132, 131: 909000133, 132: 909000134, 133: 909000135, 134: 909000136, 135: 909000137, 136: 909000138, 137: 909000139, 138: 909000140, 139: 909000141, 140: 909000142, 141: 909000143, 142: 909000144, 143: 909000145, 144: 909000150, 145: 909033001, 146: 909033002, 147: 909033003, 148: 909033004, 149: 909033005, 150: 909033006, 151: 909033007, 152: 909033008, 153: 909033009, 154: 909033010, 155: 909034001, 156: 909034002, 157: 909034003, 158: 909034004, 159: 909034005, 160: 909034006, 161: 909034007, 162: 909034008, 163: 909034009, 164: 909034010, 165: 909034011, 166: 909034012, 167: 909034013, 168: 909034014, 169: 909035001, 170: 909035002, 171: 909035003, 172: 909035004, 173: 909035005, 174: 909035006, 175: 909035007, 176: 909035008, 177: 909035009, 178: 909035010, 179: 909035011, 180: 909035012, 181: 909035013, 182: 909035014, 183: 909035015, 184: 909036001, 185: 909036002, 186: 909036003, 187: 909036004, 188: 909036005, 189: 909036006, 190: 909036008, 191: 909036009, 192: 909036010, 193: 909036011, 194: 909036012, 195: 909036014, 196: 909037001, 197: 909037002, 198: 909037003, 199: 909037004, 200: 909037005, 201: 909037006, 202: 909037007, 203: 909037008, 204: 909037009, 205: 909037010, 206: 909037011, 207: 909037012, 208: 909038001, 209: 909038002, 210: 909038003, 211: 909038004, 212: 909038005, 213: 909038006, 214: 909038008, 215: 909038009, 216: 909038010, 217: 909038011, 218: 909038012, 219: 909038013, 220: 909039001, 221: 909039002, 222: 909039003, 223: 909039004, 224: 909039005, 225: 909039006, 226: 909039007, 227: 909039008, 228: 909039009, 229: 909039010, 230: 909039011, 231: 909039012, 232: 909039013, 233: 909039014, 234: 909040001, 235: 909040002, 236: 909040003, 237: 909040004, 238: 909040005, 239: 909040006, 240: 909040008, 241: 909040009, 242: 909040010, 243: 909040011, 244: 909040012, 245: 909040013, 246: 909040014, 247: 909041001, 248: 909041002, 249: 909041003, 250: 909041004, 251: 909041005, 252: 909041006, 253: 909041007, 254: 909041008, 255: 909041009, 256: 909041010, 257: 909041011, 258: 909041012, 259: 909041013, 260: 909041014, 261: 909041015, 262: 909042001, 263: 909042002, 264: 909042003, 265: 909042004, 266: 909042005, 267: 909042006, 268: 909042007, 269: 909042008, 270: 909042009, 271: 909042011, 272: 909042012, 273: 909042013, 274: 909042016, 275: 909042017, 276: 909042018, 277: 909043001, 278: 909043002, 279: 909043003, 280: 909043004, 281: 909043005, 282: 909043006, 283: 909043007, 284: 909043008, 285: 909043009, 286: 909043010, 287: 909043013, 288: 909044001, 289: 909044002, 290: 909044003, 291: 909044004, 292: 909044005, 293: 909044006, 294: 909044007, 295: 909044008, 296: 909044009, 297: 909044010, 298: 909044011, 299: 909044012, 300: 909044015, 301: 909044016, 302: 909045001, 303: 909045002, 304: 909045003, 305: 909045004, 306: 909045005, 307: 909045006, 308: 909045007, 309: 909045008, 310: 909045009, 311: 909045010, 312: 909045011, 313: 909045012, 314: 909045015, 315: 909045016, 316: 909045017, 317: 909046001, 318: 909046002, 319: 909046003, 320: 909046004, 321: 909046005, 322: 909046006, 323: 909046007, 324: 909046008, 325: 909046009, 326: 909046010, 327: 909046011, 328: 909046012, 329: 909046013, 330: 909046014, 331: 909046015, 332: 909046016, 333: 909046017, 334: 909047001, 335: 909047002, 336: 909047003, 337: 909047004, 338: 909047005, 339: 909047006, 340: 909047007, 341: 909047008, 342: 909047009, 343: 909047010, 344: 909047011, 345: 909047012, 346: 909047013, 347: 909047015, 348: 909047016, 349: 909047017, 350: 909047018, 351: 909047019, 352: 909048001, 353: 909048002, 354: 909048003, 355: 909048004, 356: 909048005, 357: 909048006, 358: 909048007, 359: 909048008, 360: 909048009, 361: 909048010, 362: 909048011, 363: 909048012, 364: 909048013, 365: 909048014, 366: 909048015, 367: 909048016, 368: 909048017, 369: 909048018, 370: 909049001, 371: 909049002, 372: 909049003, 373: 909049004, 374: 909049005, 375: 909049006, 376: 909049007, 377: 909049008, 378: 909049009, 379: 909049010, 380: 909049011, 381: 909049012, 382: 909049013, 383: 909049014, 384: 909049015, 385: 909049016, 386: 909049017, 387: 909049018, 388: 909049019, 389: 909049020, 390: 909049021, 391: 909050002, 392: 909050003, 393: 909050004, 394: 909050005, 395: 909050006, 396: 909050008, 397: 909050009, 398: 909050010, 399: 909050011, 400: 909050012, 401: 909050013, 402: 909050014, 403: 909050015, 404: 909050016, 405: 909050017, 406: 909050018, 407: 909050019, 408: 909050020, 409: 909050021, 410: 909050026, 411: 909050027, 412: 909050028, 413: 909547001, 414: 909550001}

EMOTE_MAP = {1: 909000063, 2: 909000081, 3: 909000075, 4: 909000085, 5: 909000134, 6: 909000098, 7: 909035007, 8: 909051012, 9: 909000141, 10: 909034008, 11: 909041002, 12: 909039004, 13: 909042008, 14: 909051014, 15: 909039012, 16: 909040010, 17: 909035010, 18: 909041005, 19: 909051003, 20: 909034001}

EVO_NAMES = {1: "AK4 ZIKO", 2: "SCAR4 ZIKO", 3: "MP40 ZIKO", 4: "MP40 ZIKO 2", 5: "M1014 ZIKO", 6: "M1014 ZIKO 2", 7: "XM8 ZIKO", 8: "Famas ZIKO", 9: "UMP ZIKO", 10: "M1887 ZIKO", 11: "Woodpecker ZIKO", 12: "Groza ZIKO", 13: "M4A1 ZIKO", 14: "Thompson ZIKO", 15: "G18 ZIKO", 16: "Parafal ZIKO", 17: "P90 ZIKO", 18: "M60 ZIKO", 19: "تطورية ZIKO 19", 20: "تطورية ZIKO 20"}

# ------------------- دوال الـ API الجديدة -------------------
async def fetch_player_info(uid: str) -> dict:
    """جلب جميع معلومات اللاعب من الـ API"""
    url = f"https://foubia-info-ff.vercel.app/{uid}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"خطأ في جلب المعلومات: {resp.status}")
                    return None
    except Exception as e:
        print(f"استثناء في جلب المعلومات: {e}")
        return None

async def fetch_ban_status(uid: str) -> dict:
    """جلب حالة الحظر من الـ API"""
    url = f"https://foubia-ban-check.vercel.app/bancheck?key=xTzPrO&uid={uid}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"خطأ في جلب حالة الحظر: {resp.status}")
                    return None
    except Exception as e:
        print(f"استثناء في جلب حالة الحظر: {e}")
        return None

async def fetch_outfit_image(uid: str, region: str, max_retries: int = 2, delay: int = 3) -> bytes:
    """جلب صورة الأوتفيت مع إعادة المحاولة"""
    url = f"https://ffoutfitapis.vercel.app/outfit-image?uid={uid}&region={region}&key=99day"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://ffoutfitapis.vercel.app/'
    }
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    elif resp.status in [403, 404, 500, 502, 503, 504]:
                        print(f"⚠️ محاولة {attempt+1}: الـ API يعيد {resp.status}. قد تكون الصورة قيد التوليد. ننتظر {delay} ثوانٍ...")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(delay)
                        continue
                    else:
                        print(f"❌ خطأ غير متوقع في جلب الأوتفيت: {resp.status}")
                        return None
        except asyncio.TimeoutError:
            print(f"⚠️ محاولة {attempt+1}: انتهت المهلة. نعيد المحاولة بعد {delay} ثوانٍ...")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            continue
        except Exception as e:
            print(f"❌ استثناء في جلب الأوتفيت: {e}")
            return None
    print("❌ فشلت جميع محاولات جلب الأوتفيت.")
    return None

def get_subscription_keyboard():
    """إنشاء أزرار الاشتراك"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 القناة", url="https://t.me/Ziko_Tim")],
        [InlineKeyboardButton(text="💬 المجموعة", url="https://t.me/MTX_SX_CHAT_TEAM")],
        [InlineKeyboardButton(text="✅ تحقق", callback_data="check_sub")]
    ])
    return keyboard

# ------------------- دوال التحقق من الاشتراك -------------------
async def check_subscription(user_id: int) -> bool:
    try:
        channel_member = await telegram_bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        group_member = await telegram_bot.get_chat_member(REQUIRED_GROUP, user_id)
        return (channel_member.status not in ["left", "kicked"] and
                group_member.status not in ["left", "kicked"])
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك: {e}")
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

# ------------------- دوال التلغرام الأساسية -------------------
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

# ------------------- دالة تسجيل معالجات الأوامر -------------------
async def register_handlers(dp: Dispatcher):
    """تسجيل معالجات الأوامر - مع التعديلات الجديدة"""

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
        
        # المطور يعمل لديه البوت في الخاص
        if user_id == ADMIN_TELEGRAM_ID:
            welcome_text = """
🔥 <b>FPI SX COMMAND</b> 🔥

━━━━━━━━━━━━━━━━━━━━━━

<b>🛠️ ADMIN PANEL</b>

• You have full access
• Bot works in private for you
• Use /help to see all commands

━━━━━━━━━━━━━━━━━━━━━━

👑 <b>Developer:</b> @ZikoB0SS
🌟 <b>Sponsor:</b> @noseyrobot
"""
            await message.reply(welcome_text, parse_mode="HTML")
            return
        
        # المستخدمين العاديين - لا يعمل في الخاص
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
        
        # في المجموعة - التحقق من الاشتراك مع أزرار
        if not await check_subscription(user_id):
            await message.reply(
                "🔒 **Subscription Required**\n\n"
                "Please join our channel and group to use the bot:",
                reply_markup=get_subscription_keyboard()
            )
            return
        
        # قائمة الأوامر الرئيسية
        commands_text = """
🔥 <b>FPI SX COMMAND</b> 🔥

━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 SQUAD COMMANDS</b>
/3 [UID] — Open 3‑player squad
/5 [UID] — Open 5‑player squad
/6 [UID] — Open 6‑player squad
/inv [team_code] [UID] — Invite player to team

━━━━━━━━━━━━━━━━━━━━━━

<b>🕺 DANCE & EMOTE COMMANDS</b>
/dance [code] [UID1] [UID2] ... [1-414] — Perform emote in team
/fast [code] [UID1] ... [emote] [count] — Rapid emote spam (max 50)
/evo [code] [UID1] ... [1-20] — Evolution emote
/play [UID] [1-414] — Basic emote
/ms [team_code] [message] — Send custom message in team (max 6 words)

━━━━━━━━━━━━━━━━━━━━━━

<b>📊 INFO COMMANDS</b>
/outfit [UID] — Get outfit image
/all_info [UID] — Get all player info
/check [UID] — Check ban status

━━━━━━━━━━━━━━━━━━━━━━

🌟 <b>Sponsor:</b> @noseyrobot
👑 <b>Developer:</b> @ZikoB0SS
"""
        await message.reply(commands_text, parse_mode="HTML")

    @dp.message(Command("help"))
    async def help_cmd(message: Message):
        user_id = message.from_user.id
        chat_type = message.chat.type
        
        # المطور في الخاص
        if user_id == ADMIN_TELEGRAM_ID and chat_type == "private":
            commands_text = """
🔥 <b>FPI SX COMMAND</b> 🔥

━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 SQUAD COMMANDS</b>
/3 [UID] — Open 3‑player squad
/5 [UID] — Open 5‑player squad
/6 [UID] — Open 6‑player squad
/inv [team_code] [UID] — Invite player to team

━━━━━━━━━━━━━━━━━━━━━━

<b>🕺 DANCE & EMOTE COMMANDS</b>
/dance [code] [UID1] [UID2] ... [1-414] — Perform emote in team
/fast [code] [UID1] ... [emote] [count] — Rapid emote spam (max 50)
/evo [code] [UID1] ... [1-20] — Evolution emote
/play [UID] [1-414] — Basic emote
/ms [team_code] [message] — Send custom message in team (max 6 words)

━━━━━━━━━━━━━━━━━━━━━━

<b>📊 INFO COMMANDS</b>
/outfit [UID] — Get outfit image
/all_info [UID] — Get all player info
/check [UID] — Check ban status

━━━━━━━━━━━━━━━━━━━━━━

🌟 <b>Sponsor:</b> @noseyrobot
👑 <b>Developer:</b> @ZikoB0SS
"""
            await message.reply(commands_text, parse_mode="HTML")
            return
        
        # في المجموعة
        if chat_type in ["group", "supergroup"]:
            if not await require_subscription(message):
                return
            commands_text = """
🔥 <b>FPI SX COMMAND</b> 🔥

━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 SQUAD COMMANDS</b>
/3 [UID] — Open 3‑player squad
/5 [UID] — Open 5‑player squad
/6 [UID] — Open 6‑player squad
/inv [team_code] [UID] — Invite player to team

━━━━━━━━━━━━━━━━━━━━━━

<b>🕺 DANCE & EMOTE COMMANDS</b>
/dance [code] [UID1] [UID2] ... [1-414] — Perform emote in team
/fast [code] [UID1] ... [emote] [count] — Rapid emote spam (max 50)
/evo [code] [UID1] ... [1-20] — Evolution emote
/play [UID] [1-414] — Basic emote
/ms [team_code] [message] — Send custom message in team (max 6 words)

━━━━━━━━━━━━━━━━━━━━━━

<b>📊 INFO COMMANDS</b>
/outfit [UID] — Get outfit image
/all_info [UID] — Get all player info
/check [UID] — Check ban status

━━━━━━━━━━━━━━━━━━━━━━

🌟 <b>Sponsor:</b> @noseyrobot
👑 <b>Developer:</b> @ZikoB0SS
"""
            await message.reply(commands_text, parse_mode="HTML")
        else:
            # أي شيء آخر - رابط المجموعة
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 Join Group", url="https://t.me/MTX_SX_CHAT_TEAM")]
            ])
            await message.reply(
                "🤖 <b>This bot works only in groups!</b>\n\n"
                "Please join our group to use the bot:",
                reply_markup=markup,
                parse_mode="HTML"
            )

    # أوامر المجموعة الأساسية (3,5,6)
    @dp.message(Command("3", "5", "6"))
    async def squad_size_cmd(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply(f"❌ Usage: /{message.text[1]} [UID]")
            return
        target_uid = parts[1]
        if not target_uid.isdigit():
            await message.reply("❌ Invalid UID!")
            return
        size = int(message.text[1])
        await message.reply(f"🚀 Creating {size}-player squad for UID {target_uid}...")
        try:
            global online_writer, whisper_writer, key, iv, region
            uid = target_uid
            PAc = await OpEnSq(key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
            C = await cHSq(size, uid, key, iv, region)
            await asyncio.sleep(0.3)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
            V = await SEnd_InV(size, uid, key, iv, region)
            await asyncio.sleep(0.3)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
            E = await ExiT(None, key, iv)
            await asyncio.sleep(3.5)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
            await message.reply(f"✅ Squad created and invite sent to {target_uid}!")
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")

    # ================== أمر /inv المعدل ==================
    @dp.message(Command("inv"))
    async def invite_to_team_command(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.strip().split()
        if len(parts) < 3:
            await message.reply(
                "❌ **الاستخدام الصحيح:**\n"
                "`/inv [team_code] [UID]`\n"
                "مثال: `/inv ABC123 123456789`"
            )
            return
        team_code = parts[1]
        target_uid = parts[2]
        if not target_uid.isdigit():
            await message.reply("❌ UID يجب أن يكون أرقاماً فقط.")
            return
        status_msg = await message.reply(
            f"🔄 جاري تنفيذ /inv على الفريق **{team_code}** للهدف `{target_uid}`..."
        )
        asyncio.create_task(
            process_invite_command(
                team_code, target_uid, key, iv, region,
                message.chat.id, status_msg.message_id, message.from_user.id
            )
        )

    # ================== أمر /fast للإيموجي السريع ==================
    @dp.message(Command("fast"))
    async def fast_emote_command(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.strip().split()
        if len(parts) < 3:
            await message.reply(
                "❌ **الاستخدام الصحيح:**\n"
                "`/fast [team_code] [UID1] [UID2] ... [emote_number] [count]`\n"
                "مثال: `/fast ABC123 123456789 789123456 5`  (العدد اختياري، افتراضي 50)"
            )
            return
        team_code = parts[1]
        uids = []
        emote_number = None
        count = 50  # القيمة الافتراضية
        for part in parts[2:]:
            if part.isdigit():
                if len(part) <= 3 and emote_number is None:
                    emote_number = part
                elif len(part) <= 3 and emote_number is not None:
                    count = int(part)
                else:
                    uids.append(part)
            else:
                break
        if not uids:
            await message.reply("❌ لم يتم إدخال أي معرف هدف صحيح.")
            return
        if emote_number is None:
            await message.reply("❌ لم يتم تحديد رقم الإيموجي.")
            return
        emote_number = int(emote_number)
        if emote_number not in ALL_EMOTE:
            await message.reply("❌ رقم الإيموجي غير صالح (يجب أن يكون بين 1 و414).")
            return
        if count < 1 or count > 50:
            await message.reply("❌ عدد التكرارات يجب أن يكون بين 1 و50.")
            return
        status_msg = await message.reply(
            f"🔄 بدء سبام الإيموجي **{emote_number}** في الفريق `{team_code}` "
            f"للأهداف: {', '.join(uids)} بعدد {count} مرة..."
        )
        asyncio.create_task(
            process_fast_emote_command(
                team_code, uids, emote_number, count, key, iv, region,
                message.chat.id, status_msg.message_id, message.from_user.id
            )
        )

    # ================== أمر /dance المحسن ==================
    @dp.message(Command("dance"))
    async def dance_command(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.strip().split()
        if len(parts) < 4:
            await message.reply(
                "❌ **الاستخدام:** `/dance [team_code] [UID1] [UID2] ... [emote_number]`"
            )
            return
        team_code = parts[1]
        uids = []
        emote_number = None
        for part in parts[2:]:
            if part.isdigit() and len(part) <= 3 and emote_number is None:
                emote_number = part
            elif part.isdigit():
                uids.append(part)
        if not uids or emote_number is None:
            await message.reply("❌ بيانات غير صحيحة.")
            return
        emote_number = int(emote_number)
        if emote_number not in ALL_EMOTE:
            await message.reply("❌ رقم إيموجي غير صالح.")
            return
        status_msg = await message.reply(f"🔄 تنفيذ /dance للأهداف {', '.join(uids)}...")
        asyncio.create_task(
            process_dance_command(team_code, uids, emote_number, key, iv, region,
                                  message.chat.id, status_msg.message_id)
        )

    # ================== أمر /outfit ==================
    @dp.message(Command("outfit"))
    async def outfit_cmd(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ Usage: /outfit [UID]\nExample: /outfit 123456789")
            return
        
        uid = parts[1]
        if not uid.isdigit():
            await message.reply("❌ Invalid UID!")
            return
        
        status_msg = await message.reply("🔄 Preparing outfit image... (may take a few seconds)")
        
        info = await fetch_player_info(uid)
        if not info or not info.get('basicinfo'):
            await status_msg.edit_text("❌ Failed to fetch player info.")
            return
        
        region_api = info['basicinfo'][0].get('region', 'ME').lower()
        valid_regions = ['me', 'ind', 'bd', 'sg', 'id', 'th', 'vn', 'ru', 'br', 'na', 'eu']
        if region_api not in valid_regions:
            region_api = 'me'
        
        await status_msg.edit_text(f"🔄 Generating outfit image for region **{region_api.upper()}**...")
        
        image_bytes = await fetch_outfit_image(uid, region_api, max_retries=3, delay=4)
        
        if not image_bytes:
            await status_msg.edit_text("❌ Failed to fetch outfit image.")
            return
        
        photo = BufferedInputFile(image_bytes, filename=f"{uid}_outfit.jpg")
        await message.reply_photo(
            photo=photo, 
            caption=f"🎭 **Player Outfit**\n🆔 `{uid}`\n🌍 Region: **{region_api.upper()}**"
        )
        await status_msg.delete()

    # ================== أمر /all_info ==================
    @dp.message(Command("all_info"))
    async def all_info_cmd(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ Usage: /all_info [UID]\nExample: /all_info 123456789")
            return
        
        uid = parts[1]
        if not uid.isdigit():
            await message.reply("❌ Invalid UID!")
            return
        
        status_msg = await message.reply("🔄 Fetching player info...")
        
        data = await fetch_player_info(uid)
        if not data:
            await status_msg.edit_text("❌ Failed to fetch info. Check UID.")
            return
        
        reply = f"📊 **Player Info** `{uid}`\n"
        reply += "━━━━━━━━━━━━━━━━━━━━\n"
        
        if data.get('basicinfo'):
            b = data['basicinfo'][0]
            reply += f"👤 **Name:** {b.get('username', 'Unknown')}\n"
            reply += f"📈 **Level:** {b.get('level', 'N/A')}\n"
            reply += f"❤️ **Likes:** {b.get('likes', 0):,}\n"
            reply += f"🌍 **Region:** {b.get('region', 'N/A')}\n"
            reply += f"📝 **Bio:** {b.get('bio', 'None')[:50]}...\n"
            reply += f"📅 **Created:** {datetime.fromtimestamp(b.get('createat', 0)).strftime('%Y-%m-%d')}\n"
            reply += f"🕒 **Last Login:** {datetime.fromtimestamp(b.get('lastlogin', 0)).strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if data.get('claninfo'):
            c = data['claninfo'][0]
            reply += f"🏰 **Guild:** {c.get('clanname', 'None')}\n"
            reply += f"🆔 **Guild ID:** `{c.get('clanid', 'N/A')}`\n"
            reply += f"📊 **Guild Level:** {c.get('guildlevel', 'N/A')}\n"
            reply += f"👥 **Members:** {c.get('livemember', 'N/A')}\n\n"
        else:
            reply += "🏰 **Guild:** None\n\n"
        
        if data.get('clanadmin'):
            reply += "👑 **Guild Admins:**\n"
            for admin in data['clanadmin'][:3]:
                reply += f"├─ {admin.get('adminname', 'Unknown')} (Level {admin.get('level', 'N/A')})\n"
        
        reply += "━━━━━━━━━━━━━━━━━━━━"
        
        await status_msg.edit_text(reply, parse_mode='Markdown')

    # ================== أمر /check ==================
    @dp.message(Command("check"))
    async def check_cmd(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ Usage: /check [UID]\nExample: /check 123456789")
            return
        
        uid = parts[1]
        if not uid.isdigit():
            await message.reply("❌ Invalid UID!")
            return
        
        status_msg = await message.reply("🔄 Checking ban status...")
        
        ban_data = await fetch_ban_status(uid)
        if not ban_data:
            await status_msg.edit_text("❌ Failed to check ban status.")
            return
        
        info = await fetch_player_info(uid)
        
        username = "Unknown"
        level = "N/A"
        if info and info.get('basicinfo'):
            username = info['basicinfo'][0].get('username', 'Unknown')
            level = info['basicinfo'][0].get('level', 'N/A')
        
        is_banned = ban_data.get('is_banned', False)
        
        status_emoji = "🚫 **BANNED**" if is_banned else "✅ **NOT BANNED**"
        
        reply = f"🔍 **Ban Check**\n"
        reply += "━━━━━━━━━━━━━━━━━━━━\n"
        reply += f"👤 **Name:** {username}\n"
        reply += f"📈 **Level:** {level}\n"
        reply += f"🆔 **UID:** `{uid}`\n"
        reply += f"🚦 **Status:** {status_emoji}\n"
        reply += "━━━━━━━━━━━━━━━━━━━━"
        
        await status_msg.edit_text(reply, parse_mode='Markdown')

    # ================== أمر /ms لإرسال رسالة مخصصة في الفريق ==================
    @dp.message(Command("ms"))
    async def ms_command(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.strip().split(maxsplit=2)
        if len(parts) < 3:
            await message.reply(
                "❌ **الاستخدام الصحيح:**\n"
                "`/ms [team_code] [الرسالة]`\n"
                "مثال: `/ms ABC123 مرحباً بالجميع`\n"
                "⚠️ الحد الأقصى للرسالة: 6 كلمات."
            )
            return
        team_code = parts[1]
        user_message = parts[2].strip()
        
        # التحقق من عدد الكلمات
        word_count = len(user_message.split())
        if word_count > 6:
            await message.reply(f"❌ الرسالة طويلة جداً! الحد الأقصى 6 كلمات (لديك {word_count}).")
            return
        
        status_msg = await message.reply(
            f"🔄 جاري إرسال الرسالة إلى الفريق **{team_code}**..."
        )
        
        asyncio.create_task(
            process_ms_command(
                team_code, user_message, key, iv, region,
                message.chat.id, status_msg.message_id, message.from_user.id
            )
        )

    # ================== أمر /evo ==================
    @dp.message(Command("evo"))
    async def evo_cmd(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.split()
        if len(parts) < 4:
            await message.reply("❌ Usage: /evo [team_code] [UID] [emote_number 1-20]")
            return
        team_code = parts[1]
        target_uid = parts[2]
        try:
            emote_number = int(parts[3])
            if emote_number < 1 or emote_number > 20:
                await message.reply("❌ Emote number must be between 1 and 20")
                return
        except ValueError:
            await message.reply("❌ Invalid emote number")
            return

        emote_name = EVO_NAMES.get(emote_number, f"Evolution {emote_number}")

        await message.reply(f"🚀 Starting evolution dance: Team {team_code}, Target {target_uid}, Emote {emote_name}")
        try:
            global online_writer, whisper_writer, key, iv, region
            emote_id = EMOTE_MAP.get(emote_number)
            if not emote_id:
                await message.reply("❌ Invalid evolution emote ID!")
                return

            join_packet = await GenJoinSquadsPacket(team_code, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
            await asyncio.sleep(1.5)
            H = await Emote_k(int(target_uid), emote_id, key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            await asyncio.sleep(0.5)
            leave_packet = await ExiT(None, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)

            await message.reply(f"✅ Evolution emote **{emote_name}** sent to `{target_uid}`!")
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")

    # ================== أمر /play ==================
    @dp.message(Command("play"))
    async def play_cmd(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.split()
        if len(parts) < 3:
            await message.reply("❌ Usage: /play [UID] [emote_number 1-414]")
            return
        target_uid = parts[1]
        try:
            emote_number = int(parts[2])
            if emote_number < 1 or emote_number > 414:
                await message.reply("❌ Emote number must be between 1 and 414")
                return
        except ValueError:
            await message.reply("❌ Invalid emote number")
            return

        await message.reply(f"🚀 Sending emote {emote_number} to {target_uid}...")
        try:
            global online_writer, whisper_writer, key, iv, region
            emote_id = ALL_EMOTE.get(emote_number)
            if not emote_id:
                await message.reply("❌ Invalid emote ID!")
                return

            H = await Emote_k(int(target_uid), emote_id, key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)

            await message.reply(f"✅ Emote {emote_number} sent to {target_uid}!")
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")

    # ================== أمر /lag ==================
    @dp.message(Command("lag"))
    async def lag_cmd(message: Message):
        if not await require_subscription(message):
            return
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ Usage: /lag [team_code]")
            return
        team_code = parts[1]
        await message.reply(f"🚀 Starting lag attack on team {team_code}...")
        try:
            global lag_running, lag_task, key, iv, region
            if lag_task and not lag_task.done():
                lag_running = False
                lag_task.cancel()
                await asyncio.sleep(0.1)
            lag_running = True
            lag_task = asyncio.create_task(lag_team_loop(team_code, key, iv, region))
            await message.reply(f"✅ Lag attack started. To stop: /stop_lag")
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")

    # ================== أمر /stop_lag ==================
    @dp.message(Command("stop_lag"))
    async def stop_lag_cmd(message: Message):
        if not await require_subscription(message):
            return
        global lag_running, lag_task
        if lag_task and not lag_task.done():
            lag_running = False
            lag_task.cancel()
            await message.reply("✅ Lag attack stopped.")
        else:
            await message.reply("❌ No active lag attack.")

# ================== دوال معالجة الأوامر الجديدة ==================
async def process_invite_command(team_code: str, target_uid: str, key, iv, region, chat_id: int, status_msg_id: int, user_id: int):
    try:
        join_packet = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
        await asyncio.sleep(1.5)
        invite_packet = await SEnd_InV(5, int(target_uid), key, iv, region)  # size 5 عشوائي
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', invite_packet)
        await asyncio.sleep(1)
        exit_packet = await ExiT(None, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', exit_packet)
        await telegram_bot.edit_message_text(
            f"✅ تمت دعوة `{target_uid}` إلى الفريق `{team_code}` بنجاح!",
            chat_id, status_msg_id,
            parse_mode="HTML"
        )
    except Exception as e:
        await telegram_bot.edit_message_text(
            f"❌ خطأ في تنفيذ /inv: {str(e)}",
            chat_id, status_msg_id
        )

async def process_fast_emote_command(team_code: str, uids: list, emote_number: int, count: int, key, iv, region, chat_id: int, status_msg_id: int, user_id: int):
    try:
        emote_id = ALL_EMOTE[emote_number]
        join_packet = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
        await asyncio.sleep(1.5)
        sent_count = 0
        for i in range(count):
            for uid in uids:
                try:
                    emote_packet = await Emote_k(int(uid), emote_id, key, iv, region)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', emote_packet)
                    sent_count += 1
                    await asyncio.sleep(0.05)
                except Exception as e:
                    print(f"فشل إرسال إيموجي إلى {uid}: {e}")
            await asyncio.sleep(0.1)
        exit_packet = await ExiT(None, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', exit_packet)
        await telegram_bot.edit_message_text(
            f"✅ اكتمل سبام الإيموجي **{emote_number}** في الفريق `{team_code}`!\n"
            f"تم إرسال {sent_count} إيموجي إلى الأهداف: {', '.join(uids)}.",
            chat_id, status_msg_id,
            parse_mode="HTML"
        )
    except Exception as e:
        await telegram_bot.edit_message_text(
            f"❌ خطأ في /fast: {str(e)}",
            chat_id, status_msg_id
        )

async def process_dance_command(team_code: str, uids: list, emote_number: int, key, iv, region, chat_id: int, status_msg_id: int):
    try:
        emote_id = ALL_EMOTE[emote_number]
        join_packet = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
        await asyncio.sleep(1.5)
        for uid in uids:
            emote_packet = await Emote_k(int(uid), emote_id, key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', emote_packet)
            await asyncio.sleep(0.3)
        exit_packet = await ExiT(None, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', exit_packet)
        await telegram_bot.edit_message_text(
            f"✅ تم أداء الإيموجي {emote_number} للأهداف: {', '.join(uids)}.",
            chat_id, status_msg_id
        )
    except Exception as e:
        await telegram_bot.edit_message_text(
            f"❌ خطأ: {str(e)}",
            chat_id, status_msg_id
        )

# ================== دالة معالجة أمر /ms ==================
async def process_ms_command(team_code: str, user_message: str, key, iv, region, chat_id: int, status_msg_id: int, user_id: int):
    try:
        # الانضمام إلى الفريق
        join_packet = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
        await asyncio.sleep(2)  # انتظار حتى يستقر الاتصال

        # إرسال الرسالة 4 مرات بألوان عشوائية
        for i in range(4):
            color = get_random_color()  # استخدام دالة الألوان العشوائية
            colored_message = f"[B][C]{color} {user_message}"
            # إرسال الرسالة إلى الفريق باستخدام safe_send_message مع chat_type=0 (فريق)
            await safe_send_message(0, colored_message, 0, 0, key, iv)
            await asyncio.sleep(0.5)  # تأخير بين الرسائل

        # الخروج من الفريق
        exit_packet = await ExiT(None, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', exit_packet)

        await telegram_bot.edit_message_text(
            f"✅ تم إرسال الرسالة إلى الفريق `{team_code}` بنجاح (4 مرات).",
            chat_id, status_msg_id,
            parse_mode="HTML"
        )
    except Exception as e:
        await telegram_bot.edit_message_text(
            f"❌ خطأ في /ms: {str(e)}",
            chat_id, status_msg_id
        )

# ------------------- دوال اللعبة الأساسية -------------------
async def lag_team_loop(team_code, key, iv, region):
    global lag_running
    count = 0
    while lag_running:
        try:
            join_packet = await GenJoinSquadsPacket(team_code, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
            await asyncio.sleep(0.01)
            leave_packet = await ExiT(None, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)
            count += 1
            print(f"دورة التأخير #{count} للفريق {team_code}")
            await asyncio.sleep(0.01)
        except Exception as e:
            print(f"خطأ في حلقة التأخير: {e}")
            await asyncio.sleep(0.1)

# ------------------- الدالة الرئيسية -------------------
async def MaiiiinE():
    global key, iv, region
    Uid, Pw = '4357299491', '6A6822FB908387D500640BD4B06C1B9C2E36D339348A2A7D2296C3133801C051'

    open_id, access_token = await GeNeRaTeAccEss(Uid, Pw)
    if not open_id or not access_token:
        print("خطأ - حساب غير صالح")
        return None

    PyL = await EncRypTMajoRLoGin(open_id, access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE:
        print("الحساب المستهدف => محظور / غير مسجل!")
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
        print("خطأ في الحصول على المنافذ من بيانات الدخول!")
        return None
    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)

    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port

    OnLine_parts = OnLinePorTs.split(":")
    OnLineiP = OnLine_parts[0]
    OnLineporT = OnLine_parts[1] if len(OnLine_parts) > 1 else "80"

    Chat_parts = ChaTPorTs.split(":")
    ChaTiP = Chat_parts[0]
    ChaTporT = Chat_parts[1] if len(Chat_parts) > 1 else "80"

    acc_name = LoGinDaTaUncRypTinG.AccountName

    equie_emote(ToKen, UrL)
    AutHToKen = await xAuThSTarTuP(int(TarGeT), ToKen, int(timestamp), key, iv)
    ready_event = asyncio.Event()

    # تشغيل بوت التلغرام كمهمة خلفية
    telegram_task = asyncio.create_task(telegram_startup())

    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region))
    task2 = asyncio.create_task(TcPOnLine(OnLineiP, OnLineporT, key, iv, AutHToKen))

    print("🤖 بوت ZAKARIA - متصل")
    print(f"🔹 المعرف: {TarGeT}")
    print(f"🔹 الاسم: {acc_name}")
    print("🔹 الحالة: 🟢 جاهز")
    print("🤖 بوت التلغرام يعمل مع webhook")

    await asyncio.gather(task1, task2, telegram_task)

def handle_keyboard_interrupt(signum, frame):
    print("\n\n🛑 طلب إيقاف البوت...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_keyboard_interrupt)

async def StarTinG():
    while True:
        try:
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)
        except KeyboardInterrupt:
            print("\n🛑 تم إيقاف البوت بواسطة المستخدم")
            break
        except asyncio.TimeoutError:
            print("انتهت صلاحية الرمز! إعادة التشغيل")
        except Exception as e:
            print(f"خطأ في TCP - {e} => إعادة التشغيل ...")

if __name__ == '__main__':
    # تم تعطيل Insta API
    # threading.Thread(target=start_insta_api, daemon=True).start()
    asyncio.run(StarTinG())
