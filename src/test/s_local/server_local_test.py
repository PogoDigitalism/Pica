import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..'))
sys.path.insert(0, project_root)

from server import socket_base

s = socket_base.Server(host_name="localhost")
s.open()