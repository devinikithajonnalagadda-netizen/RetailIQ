@echo off
cd /d C:\MINI_PROJECT
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_USER=root
set MYSQL_PASSWORD=Devinikitha@2
set MYSQL_DATABASE=retailiq_db
.venv\Scripts\python.exe -m streamlit run app.py