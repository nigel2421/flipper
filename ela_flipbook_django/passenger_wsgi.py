import os
import sys

try:
    sys.path.insert(0, os.path.dirname(__file__))

    from flipbook_project.wsgi import application
except Exception:
    import traceback
    with open('passenger_report.log', 'w') as f:
        f.write(traceback.format_exc())
    raise