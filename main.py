import json
import os

# ================= CẤU HÌNH =================
# Đường dẫn tới file điểm ĐÃ ĐƯỢC TÍNH SẴN ở máy của bạn
FILE_DIEM_GOC = r"C:\Users\ASUS\Downloads\AER 2026\aer2026_dulieudiem.txt"

# Nơi xuất dữ liệu cho Web
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

def export_to_web():
    if not os.path.exists(FILE_DIEM_GOC):
        print(f"LỖI: Không tìm thấy file tại {FILE_DIEM_GOC}")
        print("Hãy chắc chắn bạn đã chạy tool tính điểm bên kia trước!")
        return

    data = []
    with open(FILE_DIEM_GOC, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            # Bỏ qua các dòng bị lỗi hoặc dòng nếu có
            if len(parts) < 6 or "source" in line: continue
            
            try:
                team = parts[0]
                score = float(parts[1])
                gw, gl = int(parts[2]), int(parts[3])
                mw, ml = int(parts[4]), int(parts[5])
                
                matches = mw + ml
                wr = (mw / matches * 100) if matches > 0 else 0
                
                data.append({
                    "team": team,
                    "region": get_region(team),
                    "score": round(score),
                    "matches": matches,
                    "gw_gl": f"{gw}/{gl}",
                    "win_rate": f"{wr:.1f}%"
                })
            except Exception as e:
                pass # Bỏ qua dòng lỗi

    # Sắp xếp theo điểm từ cao xuống thấp
    data.sort(key=lambda x: x["score"], reverse=True)

    # Thuật toán chia Tier y hệt như bản gốc của bạn
    total_teams = len(data)
    idx_s = int(total_teams * 0.10)
    idx_a = int(total_teams * 0.30)
    idx_b = int(total_teams * 0.50)
    idx_c = int(total_teams * 0.75)

    for i, item in enumerate(data):
        item["rank"] = i + 1
        if i < idx_s: item["tier"] = "S"
        elif i < idx_a: item["tier"] = "A"
        elif i < idx_b: item["tier"] = "B"
        elif i < idx_c: item["tier"] = "C"
        else: item["tier"] = "D"

    # Ghi ra file JS
    with open(FILE_JS, "w", encoding="utf-8") as f:
        f.write(f"const AER_DATA = {json.dumps(data, ensure_ascii=False, indent=4)};")
    
    print("-> Đã lấy thành công dữ liệu điểm và xuất ra data.js cho Web!")

if __name__ == "__main__":
    export_to_web()