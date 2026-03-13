# -*- coding: utf-8 -*-
# By AbdeeLkarim BesTo

import requests, json, binascii, time, urllib3, base64, datetime, re, socket, threading, random, os, asyncio, ssl
from protobuf_decoder.protobuf_decoder import Parser
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from Pb2 import MajoRLoGinrEq_pb2, MajoRLoGinrEs_pb2, PorTs_pb2, DEcwHisPErMsG_pb2, sQ_pb2
import aiohttp  # هذا السطر هو المهم لإزالة الخطأ

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# المفاتيح الثابتة
Key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
Iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# -------------------------------------------------------------------
# دوال التشفير المساعدة
# -------------------------------------------------------------------
async def EnC_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return cipher.encrypt(pad(bytes.fromhex(HeX), AES.block_size)).hex()

async def DEc_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return unpad(cipher.decrypt(bytes.fromhex(HeX)), AES.block_size).hex()

async def EnC_PacKeT(HeX, K, V):
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()

async def DEc_PacKeT(HeX, K, V):
    return unpad(AES.new(K, AES.MODE_CBC, V).decrypt(bytes.fromhex(HeX)), 16).hex()

async def EnC_Uid(H, Tp):
    e, H = [], int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0))
        H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

async def EnC_Vr(N):
    if N < 0: return b''
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

def DEc_Uid(H):
    n = s = 0
    for b in bytes.fromhex(H):
        n |= (b & 0x7F) << s
        if not b & 0x80: break
        s += 7
    return n

# -------------------------------------------------------------------
# دوال بناء ProtoBuf
# -------------------------------------------------------------------
async def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return (await EnC_Vr(field_header)) + (await EnC_Vr(value))

async def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return (await EnC_Vr(field_header)) + (await EnC_Vr(len(encoded_value))) + encoded_value

async def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = await CrEaTe_ProTo(value)
            packet.extend(await CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(await CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(await CrEaTe_LenGTh(field, value))
    return packet

async def DecodE_HeX(H):
    R = hex(H)
    F = str(R)[2:]
    if len(F) == 1: F = "0" + F
    return F

async def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {'wire_type': result.wire_type}
        if result.wire_type == "varint":
            field_data['data'] = result.data
        elif result.wire_type in ("string", "bytes"):
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = await Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

async def DeCode_PackEt(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_dict = await Fix_PackEt(parsed_results)
        return json.dumps(parsed_results_dict)
    except Exception as e:
        print(f"error {e}")
        return None

# -------------------------------------------------------------------
# دوال توليد User-Agent و Avatar وألوان عشوائية
# -------------------------------------------------------------------
def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i+3] for i in range(0, len(str(n)), 3))

async def Ua():
    versions = ['4.0.18P6','4.0.19P7','4.0.20P1','4.1.0P3','4.1.5P2','4.2.1P8',
                '4.2.3P1','5.0.1B2','5.0.2P4','5.1.0P1','5.2.0B1','5.2.5P3',
                '5.3.0B1','5.3.2P2','5.4.0P1','5.4.3B2','5.5.0P1','5.5.2P3']
    models = ['SM-A125F','SM-A225F','SM-A325M','SM-A515F','SM-A725F','SM-M215F','SM-M325FV',
              'Redmi 9A','Redmi 9C','POCO M3','POCO M4 Pro','RMX2185','RMX3085',
              'moto g(9) play','CPH2239','V2027','OnePlus Nord','ASUS_Z01QD']
    android_versions = ['9','10','11','12','13','14']
    languages = ['en-US','es-MX','pt-BR','id-ID','ru-RU','hi-IN']
    countries = ['USA','MEX','BRA','IDN','RUS','IND']
    return f"GarenaMSDK/{random.choice(versions)}({random.choice(models)};Android {random.choice(android_versions)};{random.choice(languages)};{random.choice(countries)};)"

async def ArA_CoLor():
    Tp = ["32CD32","00BFFF","00FA9A","90EE90","FF4500","FF6347","FF69B4","FF8C00","FF6347","FFD700",
          "FFDAB9","F0F0F0","F0E68C","D3D3D3","A9A9A9","D2691E","CD853F","BC8F8F","6A5ACD","483D8B",
          "4682B4","9370DB","C71585","FF8C00","FFA07A"]
    return random.choice(Tp)

async def xBunnEr():
    bN = [902000154,902047010,902000306,902000160,902048020,902048021,902000305,902000003,
          902000016,902000017,902000019,902031010,902043025,902043024,902000020,902000021,
          902000023,902000070,902000087,902000108,902000011,902049020,902049018,902049017,
          902049016,902049015,902049003,902033016,902033017,902033018,902048018,902000306,
          902000305,902000079,902051034]
    return random.choice(bN)

# -------------------------------------------------------------------
# دوال الحصول على Access Token من Garena
# -------------------------------------------------------------------
async def GeNeRaTeAccEss(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": await Ua(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as resp:
            if resp.status != 200:
                return None, None
            data = await resp.json()
            return data.get("open_id"), data.get("access_token")

async def encrypted_proto(encoded_hex):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    padded = pad(encoded_hex, AES.block_size)
    return cipher.encrypt(padded)

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.120.1"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    return await encrypted_proto(string)

# -------------------------------------------------------------------
# دوال الاتصال الأساسية (MajorLogin, GetLoginData)
# -------------------------------------------------------------------
Hr = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': "OB52"
}

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as resp:
            if resp.status == 200:
                return await resp.read()
            return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization'] = f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as resp:
            if resp.status == 200:
                return await resp.read()
            return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(MajoRLoGinResPonsE)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet)//2)[2:]
    if uid_length == 9: headers = '0000000'
    elif uid_length == 8: headers = '00000000'
    elif uid_length == 10: headers = '000000'
    elif uid_length == 7: headers = '000000000'
    else: headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"

def equie_emote(JWT, url):
    try:
        url = f"{url}/ChooseEmote"
        headers = {
            "Accept-Encoding": "gzip",
            "Authorization": f"Bearer {JWT}",
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Expect": "100-continue",
            "ReleaseVersion": "OB51",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4.11f1",
        }
        data = bytes.fromhex("CA F6 83 22 2A 25 C7 BE FE B5 1F 59 54 4D B3 13")
        requests.post(url, headers=headers, data=data, verify=False)
    except:
        pass

# -------------------------------------------------------------------
# دوال فك تشفير الرسائل الواردة
# -------------------------------------------------------------------
async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto

async def decode_team_packet(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = sQ_pb2.recieved_chat()
    proto.ParseFromString(packet)
    return proto

# -------------------------------------------------------------------
# دوال إرسال الحزم عبر TCP (مهمة للاتصال باللعبة)
# -------------------------------------------------------------------
async def SEndPacKeT(OnLinE, ChaT, TypE, PacKeT):
    if TypE == 'ChaT' and ChaT:
        whisper_writer.write(PacKeT)
        await whisper_writer.drain()
    elif TypE == 'OnLine':
        online_writer.write(PacKeT)
        await online_writer.drain()

async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer, whisper_writer, insquad, joining_team, region
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            writer.write(bytes.fromhex(AutHToKen))
            await writer.drain()
            print("تم إرسال رمز المصادقة. دخول في حلقة القراءة...")
            while True:
                data2 = await reader.read(9999)
                if not data2:
                    print("تم إغلاق الاتصال من قبل الخادم.")
                    break
                # هنا يمكن إضافة معالجة الحزم إذا لزم الأمر
        except Exception as e:
            print(f"خطأ في TcPOnLine: {e}")
        finally:
            if online_writer:
                online_writer.close()
                await online_writer.wait_closed()
                online_writer = None
            await asyncio.sleep(reconnect_delay)

async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region, reconnect_delay=0.5):
    global whisper_writer, online_writer
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
                # معالجة الرسائل الواردة إذا لزم الأمر
        except Exception as e:
            print(f"خطأ في TcPChaT: {e}")
        finally:
            if whisper_writer:
                whisper_writer.close()
                await whisper_writer.wait_closed()
                whisper_writer = None
            await asyncio.sleep(reconnect_delay)

# -------------------------------------------------------------------
# دوال بناء الحزم المختلفة (الموجودة أصلاً في ملفك)
# -------------------------------------------------------------------
async def GeneRaTePk(Pk, N, K, V):
    PkEnc = await EnC_PacKeT(Pk, K, V)
    _ = await DecodE_HeX(int(len(PkEnc) // 2))
    if len(_) == 2: HeadEr = N + "000000"
    elif len(_) == 3: HeadEr = N + "00000"
    elif len(_) == 4: HeadEr = N + "0000"
    elif len(_) == 5: HeadEr = N + "000"
    else: HeadEr = N + "000000"
    return bytes.fromhex(HeadEr + _ + PkEnc)

async def OpEnSq(K, V, region):
    fields = {1: 1, 2: {2: "\u0001", 3: 1, 4: 1, 5: "en", 9: 1, 11: 1, 13: 1, 14: {2: 5756, 6: 11, 8: "1.111.5", 9: 2, 10: 4}}}
    packet_type = '0515'
    if region.lower() == "ind": packet_type = '0514'
    elif region.lower() == "bd": packet_type = "0519"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet_type, K, V)

async def cHSq(Nu, Uid, K, V, region):
    fields = {1: 17, 2: {1: int(Uid), 2: 1, 3: int(Nu-1), 4: 62, 5: "\u001a", 8: 5, 13: 329}}
    packet_type = '0515'
    if region.lower() == "ind": packet_type = '0514'
    elif region.lower() == "bd": packet_type = "0519"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet_type, K, V)

async def SEnd_InV(Nu, Uid, K, V, region):
    fields = {1: 2, 2: {1: int(Uid), 2: region, 4: int(Nu)}}
    packet_type = '0515'
    if region.lower() == "ind": packet_type = '0514'
    elif region.lower() == "bd": packet_type = "0519"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet_type, K, V)

async def ExiT(idT, K, V):
    fields = {1: 7, 2: {1: 12480598706}}  # idT قد لا يستخدم هنا في الكود الأصلي
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def Emote_k(TarGeT, idT, K, V, region):
    fields = {1: 21, 2: {1: 804266360, 2: 909000001, 5: {1: TarGeT, 3: idT}}}
    packet_type = '0515'
    if region.lower() == "ind": packet_type = '0514'
    elif region.lower() == "bd": packet_type = "0519"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet_type, K, V)

async def GenJoinSquadsPacket(code, K, V):
    fields = {1: 4, 2: {4: bytes.fromhex("01090a0b121920"), 5: str(code), 6: 6, 8: 1, 9: {2: 800, 6: 11, 8: "1.111.1", 9: 5, 10: 1}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def AuthClan(CLan_Uid, AuTh, K, V):
    fields = {1: 3, 2: {1: int(CLan_Uid), 2: 1, 4: str(AuTh)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1201', K, V)

async def AutH_Chat(T, uid, code, K, V):
    fields = {1: T, 2: {1: uid, 3: "en", 4: str(code)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, V)

async def GeTSQDaTa(D):
    uid = D['5']['data']['1']['data']
    chat_code = D["5"]["data"]["14"]["data"]
    squad_code = D["5"]["data"]["31"]["data"]
    return uid, chat_code, squad_code

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
async def xSEndMsg(Msg , Tp , Tp2 , id , K , V):
    fields = {1: id , 2: Tp2 , 3: Tp, 4: Msg, 5: 1735129800, 7: 2, 9: {1: "xBesTo - C4", 2: int(await xBunnEr()), 3: 901048020, 4: 330, 5: 1001000001, 8: "xBesTo - C4", 10: 1, 11: 1, 13: {1: 2}, 14: {1: 12484827014, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}, 12: 0}, 10: "en", 13: {3: 1}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)

async def xSEndMsgsQ(Msg , id , K , V):
    fields = {1: id , 2: id , 4: Msg , 5: 1756580149, 7: 2, 8: 904990072, 9: {1: "xBe4!sTo - C4", 2: await xBunnEr(), 4: 330, 5: 1001000001, 8: "xBe4!sTo - C4", 10: 1, 11: 1, 13: {1: 2}, 14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}}, 10: "en", 13: {2: 2, 3: 1}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)
# -------------------------------------------------------------------
# باقي الدوال الأخرى (موجودة في ملفك الأصلي)
# -------------------------------------------------------------------
# يمكنك إضافة بقية الدوال مثل redzed, RejectMSGtaxt, xSEndMsg, ... إلخ
# لكن ما سبق يكفي لتشغيل البوت.
