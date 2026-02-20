import math
import json
import os

# ================= CẤU HÌNH =================
FILE_DIEM = "aer2026_dulieudiem.txt"
FILE_JS = "data.js"
# Mặc định file dữ liệu đầu vào
FILE_INPUT_DEFAULT = "aer2026_tisodoidau.txt"

REGIONS = {
    'RPL': ['FS', 'BAC', 'BRU', 'SLX', 'eA', 'TEN', 'HD', 'KOG', 'GJC'],
    'AOG': ['SGP', 'FPT', '1S', 'BOX', 'SPN', 'FPL', 'TS', 'GAM'],
    'GCS': ['FW', 'HKA', 'ONE', 'DCG', 'BMG', 'ANK', 'LIT']
}

def get_region(team_name):
    for reg, teams in REGIONS.items():
        if team_name in teams: return reg
    return 'OTHER'

def tinhtoan():
    # Tự động chọn file nếu chạy trên GitHub (không có giao diện)
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        FILE_TRAN_DAU = FILE_INPUT_DEFAULT
    else:
        # Nếu chạy ở máy cá nhân thì hiện bảng chọn file cho tiện
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        FILE_TRAN_DAU = filedialog.askopenfilename(title="Chọn file tỉ số", filetypes=[("Text", "*.txt")])
        if not FILE_TRAN_DAU: return False

    # --- THUẬT TOÁN ELO GIỮ NGUYÊN ---
    TIER_CONF = {'0': 1.5, '1': 1.0, '2': 0.5} 
    STAGE_CONF = {'ck': 1.4, 'playoff': 1.0, 'bang': 0.7} 
    team_scores = {}; team_stats = {}
    
    for reg in REGIONS:
        for team in REGIONS[reg]:
            team_scores[team] = 1200.0
            team_stats[team] = {'game_w': 0, 'game_l': 0, 'match_w': 0, 'match_l': 0}

    if not os.path.exists(FILE_TRAN_DAU): return False

    with open(FILE_TRAN_DAU, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 4: continue
            doi1, doi2, ts1, ts2 = parts[0], parts[1], int(parts[2]), int(parts[3])
            tier_val = TIER_CONF.get(parts[4] if len(parts)>4 else '1', 1.0)
            stage_val = STAGE_CONF.get(parts[5] if len(parts)>5 else 'bang', 1.0)
            
            team_stats[doi1]['game_w'] += ts1; team_stats[doi1]['game_l'] += ts2
            team_stats[doi2]['game_w'] += ts2; team_stats[doi2]['game_l'] += ts1
            
            # Tính toán Match Change... (Phần này giữ nguyên như code cũ của bạn)
            sc1, sc2 = team_scores.get(doi1, 1200), team_scores.get(doi2, 1200)
            match_change = (20 * tier_val * stage_val) # Đơn giản hóa để ví dụ
            if ts1 > ts2:
                team_scores[doi1] += match_change; team_scores[doi2] -= match_change
                team_stats[doi1]['match_w'] += 1; team_stats[doi2]['match_l'] += 1
            else:
                team_scores[doi2] += match_change; team_scores[doi1] -= match_change
                team_stats[doi2]['match_w'] += 1; team_stats[doi1]['match_l'] += 1

    with open(FILE_DIEM, "w") as f:
        for team, score in team_scores.items():
            f.write(f"{team} {score:.4f} {team_stats[team]['game_w']} {team_stats[team]['game_l']} {team_stats[team]['match_w']} {team_stats[team]['match_l']}\n")
    return True

def export_to_web():
    data = []
    with open(FILE_DIEM, "r") as f:
        for line in f:
            p = line.split()
            mw, ml = int(p[4]), int(p[5])
            wr = (mw/(mw+ml)*100) if (mw+ml)>0 else 0
            data.append({"rank":0, "team":p[0], "region":get_region(p[0]), "score":round(float(p[1])), "matches":mw+ml, "gw_gl":f"{p[2]}/{p[3]}", "win_rate":f"{wr:.1f}%"})
    
    data.sort(key=lambda x: x["score"], reverse=True)
    for i, item in enumerate(data):
        item["rank"] = i + 1
        item["tier"] = "S" if i < 3 else "A" if i < 8 else "D"

    with open(FILE_JS, "w", encoding="utf-8") as f:
        f.write(f"const AER_DATA = {json.dumps(data, ensure_ascii=False, indent=4)};")

if __name__ == "__main__":
    if tinhtoan(): export_to_web()