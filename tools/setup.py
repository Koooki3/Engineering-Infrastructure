#!/usr/bin/env python3
"""Portable entry point to the three-Kit bootstrap and lifecycle CLI."""

from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'adaptive-skills-kit/adaptive-skills/tools'))

from skills import main

if __name__ == '__main__':
    sys.exit(main())
