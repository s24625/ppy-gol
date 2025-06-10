@echo off
pip install pdoc3
REM Generacja HTML
bin\pdoc3 --html --output-dir docs game_of_life.py --force
REM Konwersja HTML na PDF
bin\wkhtmltopdf docs\game_of_life.html docs\game_of_life.pdf