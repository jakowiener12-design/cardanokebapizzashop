#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "== Cardano Backend wird eingerichtet =="
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
if [ ! -d venv ]; then "$PY" -m venv venv; fi
. venv/bin/activate
pip install -q -r requirements.txt
python manage.py migrate
python manage.py seed_menu
python manage.py init_admin
python manage.py init_info
echo ""
echo "==================================================="
echo " Shop:        http://127.0.0.1:8000/"
echo " Admin-Panel: http://127.0.0.1:8000/admin/"
echo " Login:       admin / CardanoAdmin#2026"
echo "==================================================="
echo ""
python manage.py runserver
