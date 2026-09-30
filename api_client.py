import random
import string
import time
import requests
from config import BASE_URL

class HoneyAntsAPI:
    def __init__(self, init_data: str, proxy: str = None):
        self.init_data = init_data.strip()
        self.proxy = proxy
        self.session_id = self._generate_session_id()
        self.seq = 0
        self.headers = {
            "authorization": f"tma {self.init_data}",
            "x-client-session": self.session_id,
            "x-lang": "en",
            "user-agent": "Mozilla/5.0 (Linux; Android 14; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.88 Mobile Safari/537.36 Telegram-Android/11.1.3 (Google Pixel 8 Pro; Android 14; SDK 34; ARM64)",
            "origin": "https://honeyants.fun",
            "referer": "https://honeyants.fun/?tgWebAppStartParam=ref_75FBM8",
            "content-type": "application/json"
        }
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

    def _generate_session_id(self) -> str:
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=10))

    def get_me(self):
        """Ambil data akun & state game terbaru"""
        url = f"{BASE_URL}/api/me"
        try:
            r = self.session.get(url, headers=self.headers, timeout=20)
            if r.status_code == 200:
                return r.json()
            return {"error": r.text, "status_code": r.status_code}
        except Exception as e:
            return {"error": str(e)}

    def send_actions(self, actions_list: list):
        """Kirim batch action ke /api/actions"""
        if not actions_list:
            return {"ok": True, "results": []}

        # Format setiap aksi
        formatted_actions = []
        for act in actions_list:
            self.seq += 1
            formatted_actions.append({
                "id": self.seq,
                "type": act.get("type"),
                "data": act.get("data", {}),
                "t": int(time.time() * 1000)
            })

        url = f"{BASE_URL}/api/actions"
        try:
            r = self.session.post(url, headers=self.headers, json={"actions": formatted_actions}, timeout=25)
            if r.status_code == 200:
                return r.json()
            return {"error": r.text, "status_code": r.status_code}
        except Exception as e:
            return {"error": str(e)}

    def call_action(self, action_type: str, data: dict = None):
        """Panggil endpoint server-result /api/call (contoh: spin, pvpTrain, pvpFight)"""
        url = f"{BASE_URL}/api/call"
        payload = {
            "type": action_type,
            "data": data or {}
        }
        try:
            r = self.session.post(url, headers=self.headers, json=payload, timeout=25)
            if r.status_code == 200:
                return r.json()
            return {"error": r.text, "status_code": r.status_code}
        except Exception as e:
            return {"error": str(e)}

    def get_boss(self):
        """Ambil info boss terkini"""
        url = f"{BASE_URL}/api/boss"
        try:
            r = self.session.get(url, headers=self.headers, timeout=20)
            if r.status_code == 200:
                return r.json()
            return {"error": r.text, "status_code": r.status_code}
        except Exception as e:
            return {"error": str(e)}
