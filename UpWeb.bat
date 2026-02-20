@echo off
color 0A
echo ===================================================
echo   DANG DONG BO VA DAY DU LIEU LEN GITHUB...
echo ===================================================

:: Copy file tu cho khac ve day (Nho giu nguyen duong dan file cua ban nhe)
copy /Y "DÁN_ĐƯỜNG_DẪN_FILE_TXT_CỦA_BẠN_VÀO_ĐÂY" .

:: Đóng gói file
git add .
git commit -m "Cap nhat ket qua tu may tinh"

:: Keo du lieu tren web ve truoc de dong bo (tranh loi do)
git pull origin main --rebase

:: Day du lieu moi nhat len web
git push origin main

echo.
echo ===================================================
echo   THANH CONG TRET DE! 
echo   Robot Github dang nhan nguyen lieu de "nau". 
echo   F5 Web sau 1-2 phut nua nhe!
echo ===================================================
pause