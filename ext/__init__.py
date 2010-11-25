import os
import sys

our_dir = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(our_dir, "redis-py"))
sys.path.insert(0, os.path.join(our_dir, "Django-1.3-alpha-1"))
