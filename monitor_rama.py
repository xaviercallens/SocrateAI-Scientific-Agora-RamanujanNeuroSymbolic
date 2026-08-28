#!/usr/bin/env python3
"""
Root launcher for RAMA Real-Time Execution Monitor & Observatory
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from tools.monitor_rama import main

if __name__ == "__main__":
    main()
