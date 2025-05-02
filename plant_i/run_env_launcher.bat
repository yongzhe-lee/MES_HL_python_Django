@echo off
REM Visual Studio Developer Command Prompt 초기화
call "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat"

REM run_env.bat (가상환경 activate 및 runserver) 실행
call "%~dp0run_env.bat"

pause
