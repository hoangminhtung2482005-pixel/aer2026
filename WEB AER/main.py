import math
import json
import os
import tkinter as tk
from tkinter import filedialog

# ================= CẤU HÌNH =================
FILE_DIEM = "aer2026_dulieudiem.txt"
FILE_JS = "data.js"

REGIONS = {
    'RPL': ['FS', 'BAC', 'BRU', 'SLX', 'eA', 'TEN', 'HD', 'KOG', 'GJC'],
    'AOG': ['SGP', 'FPT', '1S', 'BOX', 'SPN', 'FPL', 'TS', 'GAM'],
    'GCS': ['FW', 'HKA', 'ONE', 'DCG', 'BMG', 'ANK', 'LIT']
}

def get_region(team_name):
    for reg, teams in REGIONS.items():
        if team_name in teams: return reg
    return 'OTHER'

# ================= 1. HÀM TÍNH ĐIỂM ELO =================
def tinhtoan():
    # --- BẬT CỬA SỔ CHỌN FILE ---
    root = tk.Tk()
    root.attributes('-topmost', True) # Ép cửa sổ nổi lên trên cùng
    root.withdraw() # Ẩn cửa sổ gốc
    
    # Mở bảng chọn file
    FILE_TRAN_DAU = filedialog.askopenfilename(
        title="📍 Hãy chọn file TXT chứa tỉ số thi đấu",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if not FILE_TRAN_DAU:
        print("❌ Bạn chưa chọn file! Đã hủy tính toán.")
        return False
        
    print(f"✅ Đã nạp dữ liệu từ: {FILE_TRAN_DAU}")
    
    # --- PHẦN THUẬT TOÁN GIỮ NGUYÊN ---
    TIER_CONF = {'0': 1.5, '1': 1.0, '2': 0.5} 
    STAGE_CONF = {'ck': 1.4, 'playoff': 1.0, 'bang': 0.7, 'vongloai': 0.5} 
    DEFAULT_TIER = 1.0; DEFAULT_STAGE = 1.0
    
    BASE_VAL = 20; X_VAL = 1; Y_VAL = 12; MIN_PROTECTED = 5
    RDP_BASE = 30; RDP_DENOMINATOR = 1200
    CP_GLOBAL = 75; CP_LOCAL = 50
    HARD_PENALTY_RATIO = 0.7; SOFT_PENALTY_RATIO = 0.3 
    
    team_scores = {}; team_stats = {} 

    def is_protected(w, l):
        return (w==4 and l<=1) or (w==3 and l<=1) or (w==2 and l==0)

    for reg in REGIONS:
        for team in REGIONS[reg]:
            team_scores[team] = 1200.0
            team_stats[team] = {'game_w': 0, 'game_l': 0, 'match_w': 0, 'match_l': 0}

    with open(FILE_TRAN_DAU, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 4: continue
            
            doi1, doi2 = parts[0], parts[1]
            ts1, ts2 = int(parts[2]), int(parts[3])
            tier_in = parts[4] if len(parts) >= 5 else '1'
            stage_in = parts[5] if len(parts) >= 6 else 'bang'
            
            tier_val = TIER_CONF.get(tier_in, DEFAULT_TIER)
            stage_val = STAGE_CONF.get(stage_in, DEFAULT_STAGE)
            
            team_stats[doi1]['game_w'] += ts1; team_stats[doi1]['game_l'] += ts2
            team_stats[doi2]['game_w'] += ts2; team_stats[doi2]['game_l'] += ts1
            
            if ts1 > ts2:
                team_stats[doi1]['match_w'] += 1; team_stats[doi2]['match_l'] += 1
            elif ts2 > ts1:
                team_stats[doi2]['match_w'] += 1; team_stats[doi1]['match_l'] += 1
            
            CURRENT_BASE = BASE_VAL * tier_val * stage_val
            sc1 = team_scores.get(doi1, 1200.0)
            sc2 = team_scores.get(doi2, 1200.0)
            total_games = ts1 + ts2 if (ts1+ts2) > 0 else 1
            sf1 = 1 + ts1/total_games; sf2 = 1 + ts2/total_games
            winner = ""; loser = ""; match_change = 0
            
            if ts1 > ts2: 
                winner = doi1; loser = doi2; sc_winner = sc1; sc_loser = sc2
                diff = sc1 - sc2
                base_earn = CURRENT_BASE * sf1
                adj = ((diff * X_VAL) / Y_VAL) * tier_val * stage_val
                match_change = base_earn - adj
                min_prot = 1 if tier_in == '2' else MIN_PROTECTED 
                if is_protected(ts1, ts2) and match_change < min_prot: match_change = min_prot
                
            elif ts2 > ts1: 
                winner = doi2; loser = doi1; sc_winner = sc2; sc_loser = sc1
                diff = sc2 - sc1
                base_earn = CURRENT_BASE * sf2
                adj = ((diff * X_VAL) / Y_VAL) * tier_val * stage_val
                match_change = base_earn - adj
                min_prot = 1 if tier_in == '2' else MIN_PROTECTED
                if is_protected(ts2, ts1) and match_change < min_prot: match_change = min_prot
            
            is_shockwave = False
            if winner != "" and sc_winner < sc_loser and match_change > 0 and tier_in != '2':
                is_shockwave = True

            if not is_shockwave:
                if winner == doi1:
                    team_scores[doi1] += match_change; team_scores[doi2] -= match_change
                elif winner == doi2:
                    team_scores[doi2] += match_change; team_scores[doi1] -= match_change
            else:
                team_scores[winner] += match_change 
                victims = []
                sum_distance = 0
                for t, s in team_scores.items():
                    if t != winner: 
                        if s > sc_winner and s <= sc_loser:
                            is_victim = False
                            if tier_in == '0': is_victim = True 
                            else: 
                                if get_region(t) == get_region(loser): is_victim = True 
                            if is_victim:
                                dist = s - sc_winner
                                if dist > 0:
                                    victims.append({'team': t, 'dist': dist})
                                    sum_distance += dist
                if victims and sum_distance > 0:
                    hard_pool = match_change * HARD_PENALTY_RATIO
                    soft_pool = match_change * SOFT_PENALTY_RATIO
                    team_scores[loser] -= hard_pool
                    for v in victims:
                        ratio = v['dist'] / sum_distance
                        team_scores[v['team']] -= (soft_pool * ratio)
                else:
                    team_scores[loser] -= match_change

    with open(FILE_DIEM, "w") as f:
        for team, score in team_scores.items():
            gw = team_stats[team]['game_w']; gl = team_stats[team]['game_l']
            mw = team_stats[team]['match_w']; ml = team_stats[team]['match_l']
            f.write(f"{team} {score:.4f} {gw} {gl} {mw} {ml}\n")
    return True

# ================= 2. HÀM XUẤT RA WEB (data.js) =================
def export_to_web():
    data = []
    if not os.path.exists(FILE_DIEM): return

    with open(FILE_DIEM, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 6:
                team = parts[0]; score = float(parts[1])
                gw, gl = int(parts[2]), int(parts[3])
                mw, ml = int(parts[4]), int(parts[5])
                
                matches_played = mw + ml
                win_rate = (mw / matches_played * 100) if matches_played > 0 else 0.0
                
                data.append({
                    "rank": 0, "team": team, "region": get_region(team),
                    "score": round(score), "matches": matches_played,
                    "gw_gl": f"{gw}/{gl}", "win_rate": f"{win_rate:.1f}%"
                })

    data.sort(key=lambda x: x["score"], reverse=True)
    total = len(data)
    for i, item in enumerate(data):
        item["rank"] = i + 1
        if i < int(total * 0.1): item["tier"] = "S"
        elif i < int(total * 0.3): item["tier"] = "A"
        elif i < int(total * 0.5): item["tier"] = "B"
        elif i < int(total * 0.75): item["tier"] = "C"
        else: item["tier"] = "D"

    with open(FILE_JS, "w", encoding="utf-8") as f:
        json_string = json.dumps(data, ensure_ascii=False, indent=4)
        f.write(f"const AER_DATA = {json_string};\n")

if __name__ == "__main__":
    print("⏳ Bước 1: Đang chờ chọn file dữ liệu...")
    if tinhtoan():
        print("⏳ Bước 2: Đang đóng gói dữ liệu cho Web...")
        export_to_web()
        print("✅ HOÀN TẤT! Hãy mở trình duyệt, ấn F5 để xem Bảng Xếp Hạng mới nhất.")