import sys

from .infrastructure import apps

sys.modules["checklist.apps"] = apps
