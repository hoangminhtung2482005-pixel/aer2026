@echo off
color 0A
echo ===================================================
echo   DANG DONG BO VA DAY DU LIEU LEN GITHUB...
echo ===================================================

:: Copy file tu thu muc Downloads ve day
copy /Y "C:\Users\ASUS\Downloads\AER 2026\aer2026_tisodoidau.txt" .

:: Dong goi file
git add .
git commit -m "Cap nhat ket qua tu may tinh"

:: Keo du lieu tren web ve truoc de dong bo (tranh loi do)
git pull origin main --rebase

:: Day du lieu moi nhat len web
git push origin main

echo.
echo ===================================================
echo   THANH CONG TOAN DIEN! 
echo   Robot Github dang nhan nguyen lieu de "nau". 
echo   F5 Web sau 1-2 phut nua nhe!
echo ===================================================
pause