import os
import sys

# Ensure repository root is on sys.path so `import shared` works in all test modules.
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
