"""Test helpers. Run all tests from the project folder with:  python -m unittest -v"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def read_sample(name):
    """Contents of a sample program stored next to the tests (e.g. 'valid.txt')."""
    with open(os.path.join(HERE, name), encoding="utf-8-sig") as f:
        return f.read()
