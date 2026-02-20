@echo off
color 0A
echo ===================================================
echo   DANG LAY DU LIEU VA DAY LEN GITHUB...
echo ===================================================

:: Lệnh này sẽ tự động copy đè file từ chỗ khác mang về đây
copy /Y "C:\Users\ASUS\Downloads\AER 2026\aer2026_tisodoidau.txt" .

git add .
git commit -m "Cap nhat ket qua tu may tinh"
git push origin main

echo.
echo ===================================================
echo   THANH CONG TRET DE! 
echo   Robot Github dang nhan nguyen lieu de "nau". 
echo   F5 Web sau 1-2 phut nua nhe!
echo ===================================================
pause