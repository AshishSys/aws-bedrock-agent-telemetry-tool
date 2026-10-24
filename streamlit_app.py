"""
Root entrypoint for Streamlit Community Cloud deployment.
Auto-routes to web/app.py.
"""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Execute main Streamlit app
from web.app import *
