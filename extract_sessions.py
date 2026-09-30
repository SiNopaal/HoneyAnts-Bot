import os
import sys
import asyncio
import urllib.parse
from telethon import TelegramClient, functions, types
from config import API_ID, API_HASH, SESSIONS_DIR, BOT_USERNAME, START_PARAM, DATA_FILE

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def extract_single_session(session_file):
    session_path = os.path.join(SESSIONS_DIR, session_file)
    session_name = os.path.splitext(session_file)[0]
    
    print(f"\n[+] Memproses session: {session_name} ...")
    client = TelegramClient(session_path, API_ID, API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"[-] Session {session_name} tidak terautentikasi (expired/invalid).")
            await client.disconnect()
            return None

        me = await client.get_me()
        print(f"    -> Login sebagai: {me.first_name} (@{me.username or 'NoUsername'}) [ID: {me.id}]")

        bot = await client.get_input_entity(BOT_USERNAME)

        # 1. Kirim /start jika belum pernah
        try:
            await client.send_message(bot, f"/start {START_PARAM}")
            await asyncio.sleep(1.5)
        except Exception as e:
            pass

        # 2. Request Webview
        req = functions.messages.RequestAppWebViewRequest(
            peer=bot,
            app=types.InputBotAppShortName(bot_id=bot, short_name="app"),
            platform='android',
            start_param=START_PARAM
        )
        res = await client(req)
        await client.disconnect()

        # 3. Parse Webview URL fragment
        if "#" in res.url:
            fragment = res.url.split('#')[1]
            params = dict(urllib.parse.parse_qsl(fragment))
            tg_data = params.get('tgWebAppData', '')
            if tg_data:
                print(f"    [OK] Ekstraksi tgWebAppData berhasil ({len(tg_data)} chars)")
                return tg_data
        print(f"    [-] Gagal menemukan tgWebAppData di URL: {res.url[:100]}...")
        return None
    except Exception as e:
        print(f"    [!] Error pada session {session_name}: {e}")
        try:
            await client.disconnect()
        except Exception:
            pass
        return None

async def extract_all():
    print("="*60)
    print("      HONEYANTS BOT - TELETHON SESSION EXTRACTOR")
    print("="*60)
    
    if not os.path.exists(SESSIONS_DIR):
        print(f"[-] Folder sessions tidak ditemukan: {SESSIONS_DIR}")
        return

    session_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".session")]
    if not session_files:
        print("[-] Tidak ada file .session yang ditemukan.")
        return

    print(f"[*] Ditemukan {len(session_files)} file session di {SESSIONS_DIR}")
    
    results = []
    for sf in session_files:
        tg_data = await extract_single_session(sf)
        if tg_data:
            results.append(tg_data)
        await asyncio.sleep(1)

    if results:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            for d in results:
                f.write(d + "\n")
        print("\n" + "="*60)
        print(f"[SUCCESS] Berhasil mengekstrak {len(results)} akun ke {DATA_FILE}")
        print("="*60)
    else:
        print("\n[-] Tidak ada data yang berhasil diekstrak.")

if __name__ == "__main__":
    asyncio.run(extract_all())
