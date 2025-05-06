import sys
import os

# Proje dizinini path'e ekle
project_home = os.path.expanduser('~/ikaschurn')
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from dash_dashboard import app  # dash_dashboard.py içindeki app objesi

# WSGI uygulaması
application = app.server
