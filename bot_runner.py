import time
import random
import string
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

            # 5c. Clean Moldy Food
            if config.AUTO_CLEAN_NEST:
                for f in foods:
                    if f.get("moldy"):
                        actions_queue.append({"type": "clean", "data": {"cid": cid, "fid": f.get("id")}})
                        self.log("CLEAN", f"Koloni {cname}: Membersihkan makanan berjamur ID {f.get('id')}...", Fore.YELLOW)

            if actions_queue:
                act_res = self.api.send_actions(actions_queue)
                if act_res.get("state"):
                    self.state = act_res["state"]
                self.log("COLONY", f"Koloni {cname}: {len(actions_queue)} aksi perawatan selesai.", Fore.GREEN)
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

        # 5e. Beli & Beri Pakan untuk Naikkan Level & Power Koloni
        inv = self.state.get("inv", {})
        if config.AUTO_BUY_FOOD and inv.get("kurt", 0) < 2 and self.state.get("fero", 0) >= 10:
            self.log("SHOP", "Membeli pakan ulat (kurt) untuk meningkatkan pertumbuhan & Power koloni...", Fore.YELLOW)
            act_res = self.api.send_actions([{"type": "buyFood", "data": {"k": "kurt", "n": 2}}])
            if act_res.get("state"):
                self.state = act_res["state"]
                inv = self.state.get("inv", {})
            sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        if config.AUTO_FEED_ANTS:
            for col in self.state.get("colonies", []):
                cid = col.get("id")
                cur_foods = col.get("foods", [])
                if len(cur_foods) < 3 and inv.get("kurt", 0) > 0:
                    fid = "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
                    self.log("FEED", f"Koloni {col.get('name')}: Memberi makan ulat (XP & Worker Boost)...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "feed", "data": {"cid": cid, "type": "kurt", "fid": fid}}])
                    if act_res.get("state"):
                        self.state = act_res["state"]
                        inv = self.state.get("inv", {})
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5f. Gabung Clan & Serang Boss Monster (Cooldown 2 Jam)
        if config.AUTO_JOIN_CLAN and not self.state.get("clan"):
            clan_list = self.state.get("clanList", [])
            open_clans = [c for c in clan_list if c.get("mode") == "open" and c.get("members", 0) < c.get("cap", 30)]
            if open_clans:
                target_clan = open_clans[0]
                self.log("CLAN", f"Bergabung ke Clan: {target_clan.get('name')} (Anggota: {target_clan.get('members')}/{target_clan.get('cap')})...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "clanJoin", "data": {"id": target_clan.get("id")}}])
                if act_res.get("state"):
                    self.state = act_res["state"]
                    self.log("CLAN", f"Berhasil bergabung ke Clan {target_clan.get('name')}!", Fore.GREEN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

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
                self.log("UPGRADE", f"Koloni {col.get('name')}: Upgrade Sarang ke Ytong (Kapasitas +100%, +60 XP, Power Boost)...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "equip", "data": {"cid": cid, "kind": "nest", "lv": 1}}])
                if act_res.get("state"):
                    self.state = act_res["state"]
                    self.log("UPGRADE", f"Sarang Koloni {col.get('name')} berhasil ditingkatkan!", Fore.GREEN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5h. Klaim Milestone Pemula (First Steps Bonus)
        first_data = self.state.get("first", {})
        for f_id in ["f1", "f2", "f3", "f4", "f5", "f6"]:
            if not first_data.get(f_id):
                self.log("FIRST", f"Mengklaim reward milestone pemula: {f_id}...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "firstClaim", "data": {"id": f_id}}])
                if act_res.get("state"):
                    self.state = act_res["state"]
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5i. Klaim Season Battle Pass Gratis
        pass_data = self.state.get("pass", {})
        pass_xp = pass_data.get("xp", 0)
        claimed_f = pass_data.get("cf", {})
        max_tier = max(1, pass_xp // 100)
        for lv in range(1, max_tier + 1):
            if str(lv) not in claimed_f and lv not in claimed_f:
                self.log("PASS", f"Mengklaim Season Pass Tier {lv}...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "passClaim", "data": {"track": "f", "lv": lv}}])
                if act_res.get("state"):
                    self.state = act_res["state"]
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 5j. Klaim Clan Quests (Jika dalam Clan)
        if self.state.get("clan"):
            cq_data = self.state.get("cq", {})
            cq_prog = cq_data.get("prog", {})
            cq_claimed = cq_data.get("claimed", {})
            for cq_id in ["donate", "boss", "pvp"]:
                if cq_prog.get(cq_id, 0) > 0 and not cq_claimed.get(cq_id):
                    self.log("CLAN_QUEST", f"Mengklaim Clan Quest: {cq_id} (+20 War Power)...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "cqClaim", "data": {"id": cq_id}}])
                    if act_res.get("state"):
                        self.state = act_res["state"]
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 6. Social Tasks Claim

        if config.AUTO_CLAIM_SOCIAL:
            social_state = self.state.get("social", {})
            for sq in SOCIAL_QUESTS:
                qid = sq["id"]
                qname = sq["name"]
                if qid not in social_state:
                    self.log("SOCIAL", f"Membuka & mengklaim tugas: {qname}...", Fore.YELLOW)
                    # Open
                    self.api.send_actions([{"type": "socialOpen", "data": {"id": qid}}])
                    sleep_random(1.0, 2.0)
                    # Claim
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

        # 9. Referral Commission Claim
        if config.AUTO_CLAIM_REFERRAL:
            ref_pending = self.state.get("ref", {}).get("pending", 0)
            if ref_pending >= 1:
                self.log("REFERRAL", f"Mengklaim komisi referral: {ref_pending / 100:.2f} GRAM...", Fore.YELLOW)
                act_res = self.api.send_actions([{"type": "refClaim", "data": {}}])
                if act_res.get("state"):
                    self.state = act_res["state"]
                self.log("REFERRAL", "Komisi referral berhasil diklaim!", Fore.GREEN)
                sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 10. Expeditions
        if config.AUTO_EXPEDITION:
            exp_list = self.state.get("exp", [])
            # Collect done expeditions
            for exp in exp_list:
                if exp.get("done") is False and exp.get("res"):
                    eid = exp.get("id")
                    self.log("EXPEDITION", f"Mengklaim hasil ekspedisi ID: {eid}...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "expCollect", "data": {"id": eid}}])
                    if act_res.get("state"):
                        self.state = act_res["state"]
                    self.log("EXPEDITION", "Hasil ekspedisi berhasil dikumpulkan!", Fore.GREEN)
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

            # Start new expedition if idle
            if colonies:
                active_col = colonies[0]
                if not active_col.get("exp"):
                    eid = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
                    self.log("EXPEDITION", f"Mengirim ekspedisi baru (Wilayah orman) untuk koloni {active_col.get('name')}...", Fore.YELLOW)
                    act_res = self.api.send_actions([{"type": "expStart", "data": {"cid": active_col.get("id"), "r": "orman", "id": eid}}])
                    if act_res.get("state"):
                        self.state = act_res["state"]
                        self.log("EXPEDITION", "Ekspedisi berhasil diberangkatkan!", Fore.GREEN)
                    sleep_random(config.DELAY_BETWEEN_ACTIONS_MIN, config.DELAY_BETWEEN_ACTIONS_MAX)

        # 11. PVP Free Training
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

        # Summary State & Cooldown Tracking
        server_time = self.state.get("serverTime", int(time.time() * 1000))
        account_cds = []
        for col in self.state.get("colonies", []):
            b_ready = col.get("bossReady", 0)
            if b_ready > server_time:
                account_cds.append(int((b_ready - server_time) / 1000))

        min_cd = min(account_cds) if account_cds else None
        cd_info = f" | Next Boss Hit: {min_cd // 60}m {min_cd % 60}s" if min_cd else " | Boss Hit: SIAP!"
        self.log("DONE", f"Semua siklus otomatis selesai untuk {user_name} (AMBER: {self.state.get('fero')}, GRAM: {self.state.get('gram', 0):.4f}){cd_info}", Fore.MAGENTA)
        return True, min_cd

