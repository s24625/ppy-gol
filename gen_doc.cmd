@echo off
REM Generacja HTML
bin\pdoc3 --html --output-dir docs main.py --force
REM Konwersja HTML na PDF
bin\wkhtmltopdf docs/game_of_life.html docs/game_of_life.pdf --load-error-handling ignore