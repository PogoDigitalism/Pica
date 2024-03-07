import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..'))
sys.path.insert(0, project_root)

from PicaClient import client_base

s = client_base.Client(host_name="localhost")
s.open()