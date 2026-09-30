import time
import random
import string
import math
from datetime import datetime, timezone

class Fore:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    LIGHTBLACK_EX = "\033[90m"

class Style:
    RESET_ALL = "\033[0m"
    BRIGHT = "\033[1m"

from api_client import HoneyAntsAPI
import config

def calc_workers(col):
    if not col:
        return 0
    deff = col.get("dEff", 0)
    return round(1 + 399 / (1 + math.exp(-(deff - 20) / 4.2)))



DAILY_QUESTS = [
    {"id": "collect", "name": "Panen Madu (3x)", "req": 3},
    {"id": "feed", "name": "Beri Makanan (5x)", "req": 5},
    {"id": "hunt", "name": "Buru Mangsa (2x)", "req": 2},
    {"id": "water", "name": "Siram Sarang (3x)", "req": 3},
    {"id": "pvp", "name": "Pertarungan Koloni (1x)", "req": 1}
]

SOCIAL_QUESTS = [
    {"id": "payout", "name": "Follow Telegram Payout"},
    {"id": "news", "name": "Follow Announcement Channel"},
    {"id": "chat", "name": "Join Chat Group"},
    {"id": "tag", "name": "Add #HoneyAnts to name"}
]

def sleep_random(min_s, max_s):
    time.sleep(random.uniform(min_s, max_s))

def check_act_ok(act_res):
    if not isinstance(act_res, dict):
        return False, "Response tidak valid"
    results = act_res.get("results", [])
    if not results:
        return False, act_res.get("error", "Tidak ada hasil respon")
    first = results[0]
    if first.get("ok"):
        return True, None
    return False, first.get("error") or first.get("code") or "Aksi ditolak server"

class BotRunner:

    def __init__(self, init_data: str, account_index: int = 1, proxy: str = None):
        self.init_data = init_data
        self.account_index = account_index
        self.api = HoneyAntsAPI(init_data, proxy)
        self.state = {}

    def log(self, tag: str, msg: str, color: str = Fore.WHITE):
        prefix = f"{Fore.CYAN}[Akun #{self.account_index}]{Style.RESET_ALL}"
        tag_fmt = f"{color}[{tag}]{Style.RESET_ALL}"
        print(f"{prefix} {tag_fmt} {msg}")

    def run_account(self):
        self.log("INIT", "Mengambil informasi akun & status game...", Fore.YELLOW)
        res = self.api.get_me()
        if "error" in res or "state" not in res:
            self.log("ERROR", f"Gagal login: {res.get('error')}", Fore.RED)
            return False, None


        self.state = res["state"]
        profile = self.state.get("profile", {})
        user_name = profile.get("name") or "User"
        user_id = profile.get("id") or "-"
        fero = self.state.get("fero", 0)
        gram = self.state.get("gram", 0)
        colonies = self.state.get("colonies", [])

        self.log("USER", f"Nama: {Fore.GREEN}{user_name}{Fore.WHITE} (ID: {user_id}) | AMBER: {Fore.YELLOW}{fero}{Fore.WHITE} | GRAM: {Fore.YELLOW}{gram:.4f}{Fore.WHITE} | Koloni: {len(colonies)}", Fore.CYAN)

        # 1. Tutorial Check
        if not self.state.get("tut", {}).get("done"):
            self.log("TUTORIAL", "Menyelesaikan tutorial pemula...", Fore.YELLOW)
            act_res = self.api.send_actions([{"type": "tutDone", "data": {}}])
            if act_res.get("state"):
                self.state = act_res["state"]
                self.log("TUTORIAL", "Tutorial selesai! Hadiah didapatkan (+2 Madu, +2 Ulat).", Fore.GREEN)
            sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 2. Klaim Ratu Gratis (Jika belum punya koloni)
        if config.AUTO_CLAIM_FREE_QUEEN and (not colonies or not self.state.get("freeClaimed")):
            queen_names = ["Apex", "Titan", "Nova", "Amber", "Ruby", "Shadow", "Alpha", "QueenBee"]
            q_name = random.choice(queen_names) + str(random.randint(10, 99))
            nid = "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
            self.log("FREE_QUEEN", f"Mengklaim Ratu Koloni Gratis: {q_name}...", Fore.YELLOW)
            act_res = self.api.send_actions([{"type": "claimFree", "data": {"name": q_name, "nid": nid}}])
            if act_res.get("state"):
                self.state = act_res["state"]
                colonies = self.state.get("colonies", [])
                self.log("FREE_QUEEN", f"Ratu {q_name} berhasil ditempatkan di sarang!", Fore.GREEN)
            sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 3. Daily Streak Reward
        if config.AUTO_DAILY_REWARD:
            daily = self.state.get("daily", {})
            self.log("DAILY", f"Memeriksa login streak harian (Streak: {daily.get('streak', 0)})...", Fore.YELLOW)
            act_res = self.api.send_actions([{"type": "daily", "data": {}}])
            if act_res.get("state"):
                self.state = act_res["state"]
                self.log("DAILY", f"Bonus harian berhasil diklaim! (Streak: {self.state.get('daily', {}).get('streak', 1)})", Fore.GREEN)
            sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 4. Free Spin
        if config.AUTO_FREE_SPIN:
            self.log("SPIN", "Mencoba Free Spin Harian...", Fore.YELLOW)
            spin_res = self.api.call_action("spin", {"n": 1, "paid": False})
            if "result" in spin_res:
                self.log("SPIN", f"Spin Berhasil! Hadiah: {spin_res.get('result')}", Fore.GREEN)
                if spin_res.get("state"):
                    self.state = spin_res["state"]
            else:
                err = spin_res.get("error", "Free spin belum tersedia hari ini")
                self.log("SPIN", f"Info Spin: {err}", Fore.LIGHTBLACK_EX)
            sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5. Colony Care: Collect, Water, Clean, Feed
        colonies = self.state.get("colonies", [])
        for col in colonies:
            cid = col.get("id")
            cname = col.get("name")
            honey = col.get("honey", 0)
            hum = col.get("hum", 100)
            foods = col.get("foods", [])

            actions_queue = []

            # 5a. Collect Honey
            if config.AUTO_COLLECT_HONEY and honey > 0.0001:
                actions_queue.append({"type": "collect", "data": {"cid": cid}})
                self.log("COLLECT", f"Koloni {cname}: Memanen {honey:.4f} madu...", Fore.YELLOW)

            # 5b. Water Nest
            if config.AUTO_WATER_NEST and hum < 80:
                actions_queue.append({"type": "water", "data": {"cid": cid}})
                self.log("WATER", f"Koloni {cname}: Menyiram sarang (Kelembaban saat ini {hum:.1f}%)...", Fore.YELLOW)

            # 5c. Clean Moldy Food & Live Prey Hunting
            if config.AUTO_CLEAN_NEST:
                for f in foods:
                    if f.get("moldy"):
                        actions_queue.append({"type": "clean", "data": {"cid": cid, "fid": f.get("id")}})
                        self.log("CLEAN", f"Koloni {cname}: Membersihkan makanan berjamur ID {f.get('id')}...", Fore.YELLOW)
                    elif f.get("alive") or f.get("huntT"):
                        actions_queue.append({"type": "hunt", "data": {"cid": cid, "fid": f.get("id")}})
                        self.log("HUNT", f"Koloni {cname}: Mengklaim hasil buruan serangga (+15 XP & Quest)...", Fore.YELLOW)

            if actions_queue:
                act_res = self.api.send_actions(actions_queue)
                if act_res.get("state"):
                    self.state = act_res["state"]
                self.log("COLONY", f"Koloni {cname}: {len(actions_queue)} aksi perawatan & buruan selesai.", Fore.GREEN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5d. Optimasi Kasta Tentara (Soldier Power Boost)
        colonies = self.state.get("colonies", [])
        if config.AUTO_OPTIMIZE_CASTE:
            for col in colonies:
                caste = col.get("caste", {})
                if caste.get("s", 0) < 30:
                    cid = col.get("id")
                    self.log("CASTE", f"Koloni {col.get('name')}: Mengoptimalkan kasta militer (Soldier 30% untuk ATK Power tinggi)...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "caste", "data": {"cid": cid, "f": 45, "n": 25, "s": 30}}])
                    if act_res.get("state"):
                        self.state = act_res["state"]
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5d2. Pertahankan Koloni dari Serangan Invasi Musuh (Colony Defense)
        for col in self.state.get("colonies", []):
            if col.get("inv") and not col.get("dead"):
                cid = col.get("id")
                self.log("DEFEND", f"Koloni {col.get('name')}: TERDETEKSI SERANGAN INVASI MUSUH! Melakukan pertahanan manual...", Fore.RED)
                def_res = self.api.call_action("defend", {"cid": cid})
                if isinstance(def_res, dict) and def_res.get("win"):
                    self.log("DEFEND", f"Pertahanan Koloni Berhasil! Musuh dipukul mundur (+8 Season XP)!", Fore.GREEN)
                elif isinstance(def_res, dict):
                    self.log("DEFEND", f"Status Pertahanan: {def_res.get('win', 'Selesai')}", Fore.CYAN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5e. Beli & Beri Pakan Lengkap: Madu (Bal), Lalat (Sinek), Ulat (Kurt), Belalang (Cekirge)
        ALL_FOODS = [
            {"id": "sinek", "name": "Lalat (Sinek)", "buy_price": 5, "min_buy_fero": 15, "min_w": 0, "desc": "Protein pemula & latihan berburu"},
            {"id": "kurt", "name": "Ulat Hongkong (Kurt)", "buy_price": 30, "min_buy_fero": 35, "min_w": 0, "desc": "Protein utama pembentukan prajurit"},
            {"id": "cekirge", "name": "Belalang (Cekirge)", "buy_price": 50, "min_buy_fero": 65, "min_w": 5, "desc": "Super protein & ratu boost"},
            {"id": "bal", "name": "Madu (Bal)", "buy_price": 25, "min_buy_fero": 30, "min_w": 0, "desc": "Energi stamina pekerja"},
        ]

        inv = self.state.get("inv", {})
        # Beli pakan otomatis jika habis dan AMBER mencukupi
        if getattr(config, "AUTO_BUY_FOOD", True):
            fero = self.state.get("fero", 0)
            for item in ALL_FOODS:
                f_id = item["id"]
                if inv.get(f_id, 0) < 1 and fero >= item["min_buy_fero"]:
                    buy_n = 2 if f_id == "sinek" else 1
                    total_cost = item["buy_price"] * buy_n
                    act_res = self.api.send_actions([{"type": "buyFood", "data": {"k": f_id, "n": buy_n}}])
                    ok, _ = check_act_ok(act_res)
                    if ok:
                        self.state = act_res.get("state", self.state)
                        inv = self.state.get("inv", {})
                        fero = self.state.get("fero", fero - total_cost)
                        self.log("SHOP", f"Beli {buy_n}x pakan {item['name']} di toko! ({item['desc']})", Fore.GREEN)
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # Beri makan koloni secara lengkap ke arena
        if getattr(config, "AUTO_FEED_ANTS", True):
            for col in self.state.get("colonies", []):
                cid = col.get("id")
                w_count = calc_workers(col)
                for item in ALL_FOODS:
                    f_id = item["id"]
                    # Belalang membutuhkan minimal 5 pekerja aktif
                    if f_id == "cekirge" and w_count < 5:
                        continue
                    if inv.get(f_id, 0) > 0:
                        fid = "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
                        act_res = self.api.send_actions([{"type": "feed", "data": {"cid": cid, "type": f_id, "fid": fid}}])
                        ok, err = check_act_ok(act_res)
                        if ok:
                            self.state = act_res.get("state", self.state)
                            inv = self.state.get("inv", {})
                            self.log("FEED", f"Koloni {col.get('name')}: Menaruh {item['name']} ke arena (+2 XP)! ({item['desc']})", Fore.GREEN)
                        else:
                            self.log("FEED", f"Koloni {col.get('name')}: Info pakan {item['name']}: {err}", Fore.LIGHTBLACK_EX)
                        sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)


        # 5f. Gabung Clan & Serang Boss Monster
        if config.AUTO_JOIN_CLAN and not self.state.get("clan"):
            clan_list = self.state.get("clanList", [])
            # Hitung estimasi power koloni tertinggi
            est_power = 100
            if colonies:
                c0 = colonies[0]
                workers = calc_workers(c0)
                est_power = max(100, workers * 7)

            # 1. Cari clan terbuka (mode open) yang slotnya tersedia dan power mencukupi
            eligible_open = [c for c in clan_list if c.get("mode") == "open" and c.get("members", 0) < c.get("cap", 30) and est_power >= c.get("min", 0)]
            if eligible_open:
                target_clan = eligible_open[0]
                self.log("CLAN", f"Mencoba bergabung ke Clan {target_clan.get('name')} (Min Power: {target_clan.get('min')}, Slot: {target_clan.get('members')}/{target_clan.get('cap')})...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "clanJoin", "data": {"id": target_clan.get("id")}}])
                ok, err = check_act_ok(act_res)
                if ok:
                    self.state = act_res.get("state", self.state)
                    self.log("CLAN", f"Berhasil bergabung ke Clan {target_clan.get('name')}!", Fore.GREEN)
                else:
                    self.log("CLAN", f"Gagal masuk Clan {target_clan.get('name')}: {err}", Fore.LIGHTBLACK_EX)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)
            else:
                clan_req = self.state.get("clanReq", [])
                open_clans = [c for c in clan_list if c.get("mode") == "open" and c.get("members", 0) < c.get("cap", 30)]
                lowest_open_min = min([c.get("min", 0) for c in open_clans]) if open_clans else 250

                if not clan_req:
                    approval_clans = [c for c in clan_list if c.get("mode") == "approval" and c.get("members", 0) < c.get("cap", 30) and est_power >= c.get("min", 0)]
                    if approval_clans:
                        req_target = approval_clans[0]
                        self.log("CLAN", f"Mengajukan izin masuk ke Clan: {req_target.get('name')} (Min Power: {req_target.get('min')})...", Fore.YELLOW)
                        act_res = self.api.send_actions([{"type": "clanRequest", "data": {"id": req_target.get("id")}}])
                        ok, err = check_act_ok(act_res)
                        if ok:
                            self.log("CLAN", f"Permintaan izin gabung Clan {req_target.get('name')} terkirim (menunggu persetujuan ketua)!", Fore.GREEN)
                        else:
                            self.log("CLAN", f"Info Clan Request: {err}", Fore.LIGHTBLACK_EX)
                        sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)
                    else:
                        self.log("CLAN", f"Kekuatan saat ini (~{est_power} Power) belum mencukupi klan terbuka/approval (butuh min {lowest_open_min} Power). Menunggu slot terbuka / peningkatan power...", Fore.LIGHTBLACK_EX)
                else:
                    self.log("CLAN", f"Permintaan izin gabung Clan sedang ditinjau ketua klan. Menunggu persetujuan...", Fore.LIGHTBLACK_EX)

        if config.AUTO_ATTACK_BOSS and self.state.get("clan"):
            boss_info = self.api.get_boss()
            boss_data = boss_info.get("boss") if isinstance(boss_info, dict) and "boss" in boss_info else boss_info
            if isinstance(boss_data, dict) and boss_data.get("status") == "alive":
                b_name = str(boss_data.get("type", "Boss Monster")).capitalize()
                b_hp = boss_data.get("hp", 0)
                self.log("BOSS", f"Monster Boss Terdeteksi: {b_name} (HP: {b_hp:,})", Fore.RED)
                server_time = self.state.get("serverTime", int(time.time() * 1000))
                for col in self.state.get("colonies", []):
                    if not col.get("dead"):
                        cid = col.get("id")
                        cname = col.get("name")
                        boss_ready = col.get("bossReady", 0)
                        if boss_ready > server_time:
                            rem_s = int((boss_ready - server_time) / 1000)
                            self.log("BOSS", f"Koloni {cname} cooldown istirahat: {rem_s // 60} menit {rem_s % 60} detik lagi.", Fore.LIGHTBLACK_EX)
                            continue
                        self.log("BOSS", f"Koloni {cname} menyerang {b_name}...", Fore.YELLOW)
                        hit_res = self.api.call_action("bossHit", {"cid": cid})
                        if isinstance(hit_res, dict) and ("dmg" in hit_res or "crit" in hit_res):
                            dmg = hit_res.get("dmg", 0)
                            crit = " [CRITICAL HIT!]" if hit_res.get("crit") else ""
                            self.log("BOSS", f"Serangan Berhasil! Damage: {Fore.RED}{dmg:,}{crit}{Fore.GREEN} | HP Boss: {hit_res.get('hp', 0):,}", Fore.GREEN)
                            col["bossReady"] = server_time + 7200000
                        else:
                            err = hit_res.get("error") if isinstance(hit_res, dict) else str(hit_res)
                            self.log("BOSS", f"Status Serangan: {err or 'Cooldown sedang berjalan'}", Fore.LIGHTBLACK_EX)
                        sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5g. Upgrade Sarang / Nest Koloni untuk Gandakan Kapasitas Pekerja (+60 XP & Power)
        for col in self.state.get("colonies", []):
            cid = col.get("id")
            nest_lv = col.get("nest", 0)
            if nest_lv == 0 and self.state.get("fero", 0) >= 30:
                act_res = self.api.send_actions([{"type": "equip", "data": {"cid": cid, "kind": "nest", "lv": 1}}])
                ok, err = check_act_ok(act_res)
                if ok:
                    self.state = act_res.get("state", self.state)
                    self.log("UPGRADE", f"Sarang Koloni {col.get('name')} berhasil ditingkatkan ke Ytong!", Fore.GREEN)
                else:
                    self.log("UPGRADE", f"Info upgrade sarang: {err}", Fore.LIGHTBLACK_EX)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5h. Klaim Milestone Pemula (First Steps Bonus f1-f8)
        first_data = self.state.get("first", {})
        for f_id in ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"]:
            if not first_data.get(f_id):
                act_res = self.api.send_actions([{"type": "firstClaim", "data": {"id": f_id}}])
                ok, err = check_act_ok(act_res)
                if ok:
                    self.state = act_res.get("state", self.state)
                    self.log("FIRST", f"Reward milestone pemula {f_id} berhasil diklaim!", Fore.GREEN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5i. Klaim Season Battle Pass Gratis
        pass_data = self.state.get("pass", {})
        pass_xp = pass_data.get("xp", 0)
        claimed_f = pass_data.get("cf", {})
        max_tier = max(1, pass_xp // 100)
        for lv in range(1, max_tier + 1):
            if str(lv) not in claimed_f and lv not in claimed_f:
                act_res = self.api.send_actions([{"type": "passClaim", "data": {"track": "f", "lv": lv}}])
                ok, err = check_act_ok(act_res)
                if ok:
                    self.state = act_res.get("state", self.state)
                    self.log("PASS", f"Season Pass Tier {lv} berhasil diklaim!", Fore.GREEN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)


        # 5j. Klaim Clan Quests (Jika dalam Clan: hunt, collect, win, exp, donate)
        if self.state.get("clan"):
            cq_data = self.state.get("cq", {})
            cq_prog = cq_data.get("prog", {})
            cq_claimed = cq_data.get("claimed", {})
            for cq_id in ["hunt", "collect", "win", "exp", "donate"]:
                if cq_prog.get(cq_id, 0) > 0 and not cq_claimed.get(cq_id):
                    self.log("CLAN_QUEST", f"Mengklaim Clan Quest: {cq_id} (+War Power)...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "cqClaim", "data": {"id": cq_id}}])
                    ok, _ = check_act_ok(act_res)
                    if ok:
                        self.state = act_res.get("state", self.state)
                        self.log("CLAN_QUEST", f"Clan Quest '{cq_id}' berhasil diklaim!", Fore.GREEN)
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

            # 5k. Buka Peti Harian Clan (Clan Chest)
            today_utc = datetime.now(timezone.utc)
            today_str = f"{today_utc.year}-{today_utc.month}-{today_utc.day}"
            if config.AUTO_CLAIM_CLAN_CHEST and self.state.get("clanChest") != today_str:
                self.log("CLAN_CHEST", "Membuka & mengklaim Peti Harian Klan...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "clanChest", "data": {}}])
                ok, err = check_act_ok(act_res)
                if ok:
                    self.state = act_res.get("state", self.state)
                    self.log("CLAN_CHEST", "Peti Harian Klan berhasil dibuka & hadiah diperoleh!", Fore.GREEN)
                else:
                    self.log("CLAN_CHEST", f"Info Peti Klan: {err}", Fore.LIGHTBLACK_EX)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

            # 5l. Klaim Hadiah Akhir Clan War (Jika Selesai)
            cw = self.state.get("cw", {})
            if cw.get("last") and not cw.get("lc"):
                self.log("CLAN_WAR", "Mengklaim hadiah akhir Clan War pekan lalu...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "cwClaim", "data": {}}])
                ok, err = check_act_ok(act_res)
                if ok:
                    self.state = act_res.get("state", self.state)
                    self.log("CLAN_WAR", "Hadiah Clan War berhasil diklaim!", Fore.GREEN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5m. Peti Harian VIP (Jika Aktif)
        today_utc = datetime.now(timezone.utc)
        today_str = f"{today_utc.year}-{today_utc.month}-{today_utc.day}"
        vip = self.state.get("vip", {})
        if vip.get("active") and vip.get("chest") != today_str:
            self.log("VIP", "Mengklaim Peti Harian VIP...", Fore.YELLOW)
            act_res = self.api.send_actions([{"type": "vipChest", "data": {}}])
            ok, err = check_act_ok(act_res)
            if ok:
                self.state = act_res.get("state", self.state)
                self.log("VIP", "Peti Harian VIP berhasil diklaim!", Fore.GREEN)
            sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 6. Social Tasks Claim
        if config.AUTO_CLAIM_SOCIAL:
            social_state = self.state.get("social", {})
            for sq in SOCIAL_QUESTS:
                qid = sq["id"]
                qname = sq["name"]
                if qid not in social_state:
                    self.log("SOCIAL", f"Membuka & mengklaim tugas: {qname}...", Fore.YELLOW)
                    self.api.send_actions([{"type": "socialOpen", "data": {"id": qid}}])
                    sleep_random(1.0, 2.0)
                    act_res = self.api.send_actions([{"type": "socialClaim", "data": {"id": qid}}])
                    if act_res.get("state"):
                        self.state = act_res["state"]
                    self.log("SOCIAL", f"Tugas {qname} berhasil diklaim!", Fore.GREEN)
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 7. Daily Tasks Claim
        if config.AUTO_CLAIM_TASKS:
            tasks_data = self.state.get("tasks", {})
            prog = tasks_data.get("prog", {})
            claimed = tasks_data.get("claimed", {})

            for q in DAILY_QUESTS:
                qid = q["id"]
                req_val = q["req"]
                cur_val = prog.get(qid, 0)
                if cur_val >= req_val and qid not in claimed:
                    self.log("TASKS", f"Mengklaim Quest Harian: {q['name']} ({cur_val}/{req_val})...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "taskClaim", "data": {"id": qid}}])
                    if act_res.get("state"):
                        self.state = act_res["state"]
                    self.log("TASKS", f"Quest {q['name']} berhasil diklaim!", Fore.GREEN)
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 8. Gifts Claim
        if config.AUTO_CLAIM_GIFTS:
            gifts_inbox = self.state.get("gifts", {}).get("inbox", [])
            if gifts_inbox:
                self.log("GIFTS", f"Mengklaim {len(gifts_inbox)} hadiah di kotak masuk...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "giftsClaim", "data": {}}])
                if act_res.get("state"):
                    self.state = act_res["state"]
                self.log("GIFTS", "Hadiah kotak masuk berhasil diklaim!", Fore.GREEN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 9. Milestones Claim (Pencapaian Ekosistem)
        if config.AUTO_CLAIM_MILESTONES:
            claimed_miles = self.state.get("miles", {})
            milestones = [
                ("m_col2", "Mendirikan 2 Koloni", len(colonies) >= 2),
                ("m_nest", "Upgrade Sarang ke Ytong", any(c.get("nest", 0) >= 1 for c in colonies)),
                ("m_feed", "Pasang Feeder Keramik", any(c.get("feeder", 0) >= 3 for c in colonies)),
                ("m_win5", "Menang 5 Pertarungan PVP", self.state.get("pvp", {}).get("wins", 0) >= 5),
            ]
            for m_id, m_desc, is_met in milestones:
                if is_met and m_id not in claimed_miles:
                    self.log("MILESTONE", f"Mengklaim Milestone: {m_desc}...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "mileClaim", "data": {"id": m_id}}])
                    ok, err = check_act_ok(act_res)
                    if ok:
                        self.state = act_res.get("state", self.state)
                        self.log("MILESTONE", f"Milestone '{m_desc}' berhasil diklaim!", Fore.GREEN)
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 10. Referral Commission & Tier Claim
        if config.AUTO_CLAIM_REFERRAL:
            ref_data = self.state.get("ref", {})
            ref_pending = ref_data.get("pending", 0)
            if ref_pending >= 1:
                self.log("REFERRAL", f"Mengklaim komisi referral: {ref_pending / 100:.2f} GRAM...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "refClaim", "data": {}}])
                if act_res.get("state"):
                    self.state = act_res["state"]
                self.log("REFERRAL", "Komisi referral berhasil diklaim!", Fore.GREEN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

            friends_count = len(ref_data.get("friends", []))
            claimed_reft = self.state.get("reft", {})
            for tier in [1, 3, 10, 25]:
                if friends_count >= tier and str(tier) not in claimed_reft and tier not in claimed_reft:
                    self.log("REFERRAL", f"Mengklaim milestone tier undangan ({tier} teman)...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "refTierClaim", "data": {"n": tier}}])
                    ok, err = check_act_ok(act_res)
                    if ok:
                        self.state = act_res.get("state", self.state)
                        self.log("REFERRAL", f"Hadiah tier {tier} teman berhasil diklaim!", Fore.GREEN)
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 11. Expeditions (Penjelajahan Alam)
        if config.AUTO_EXPEDITION:
            exp_list = self.state.get("exp", [])
            clock = self.state.get("clock", 0)

            # Collect completed expeditions
            for exp in exp_list:
                if not exp.get("done") and (exp.get("ready") or exp.get("res") or clock >= exp.get("end", float("inf"))):
                    eid = exp.get("id")
                    self.log("EXPEDITION", f"Mengklaim hasil ekspedisi ID: {eid}...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "expCollect", "data": {"id": eid}}])
                    ok, err = check_act_ok(act_res)
                    if ok:
                        self.state = act_res.get("state", self.state)
                        self.log("EXPEDITION", f"Hasil ekspedisi {eid} berhasil dikumpulkan!", Fore.GREEN)
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

            # Start new expedition if idle and has enough workers
            if colonies:
                active_col = colonies[0]
                w_count = calc_workers(active_col) - int(active_col.get("away", 0))
                if not active_col.get("exp"):
                    chosen_reg = None
                    if w_count >= 25:
                        chosen_reg = {"r": 1, "name": "Kum Tepeleri (Gurun - Hadiah Tinggi)"}
                    elif w_count >= 13:
                        chosen_reg = {"r": 0, "name": "Yeil Orman (Hutan)"}

                    if chosen_reg:
                        eid = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
                        self.log("EXPEDITION", f"Mengirim ekspedisi ke {chosen_reg['name']} untuk koloni {active_col.get('name')} (Pekerja aktif: {w_count})...", Fore.YELLOW)
                        act_res = self.api.send_actions([{"type": "expStart", "data": {"cid": active_col.get("id"), "r": chosen_reg["r"], "id": eid}}])
                        ok, err = check_act_ok(act_res)
                        if ok:
                            self.state = act_res.get("state", self.state)
                            self.log("EXPEDITION", f"Ekspedisi {chosen_reg['name']} berhasil diberangkatkan!", Fore.GREEN)
                        else:
                            self.log("EXPEDITION", f"Info Ekspedisi: {err}", Fore.LIGHTBLACK_EX)
                        sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)
                    else:
                        self.log("EXPEDITION", f"Pekerja aktif ({w_count}) belum mencukupi ekspedisi minimal (butuh min 13 pekerja). Melanjutkan tugas lain...", Fore.LIGHTBLACK_EX)

        # 12. PVP Free Training
        if config.AUTO_PVP_TRAIN and colonies:
            pvp_data = self.state.get("pvp", {})
            tn = pvp_data.get("tn", 0)
            if tn < 1:
                active_col = colonies[0]
                self.log("PVP", f"Memulai latihan pertempuran gratis untuk koloni {active_col.get('name')}...", Fore.YELLOW)
                train_res = self.api.call_action("pvpTrain", {"cid": active_col.get("id")})
                if "opp" in train_res:
                    won = train_res.get("win", False)
                    res_str = f"{Fore.GREEN}MENANG" if won else f"{Fore.RED}KALAH"
                    self.log("PVP", f"Hasil Latihan PVP: {res_str} | Payout: {train_res.get('payout')}", Fore.CYAN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # Summary State & Multi-Cooldown Tracking
        server_time = self.state.get("serverTime", int(time.time() * 1000))
        clock = self.state.get("clock", 0)
        account_cds = []

        # Cooldown Serangan Boss
        for col in self.state.get("colonies", []):
            b_ready = col.get("bossReady", 0)
            if b_ready > server_time:
                account_cds.append(int((b_ready - server_time) / 1000))

        # Cooldown Ekspedisi Berlangsung
        for exp in self.state.get("exp", []):
            if not exp.get("done") and exp.get("end", 0) > clock:
                rem_exp_s = int((exp["end"] - clock) * 86400)
                if rem_exp_s > 0:
                    account_cds.append(rem_exp_s)

        min_cd = min(account_cds) if account_cds else None
        cd_info = f" | Next Action CD: {min_cd // 60}m {min_cd % 60}s" if min_cd else " | Semua Aksi: SIAP!"
        self.log("DONE", f"Semua siklus otomatis selesai untuk {user_name} (AMBER: {self.state.get('fero')}, GRAM: {self.state.get('gram', 0):.4f}){cd_info}", Fore.MAGENTA)
        return True, min_cd

