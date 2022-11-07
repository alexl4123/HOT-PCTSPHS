@echo off
call python -m venv env --prompt HeuOpt1
call env\Scripts\activate && pip install -r requirements.txt
pause