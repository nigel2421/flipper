import publications
import os
import sys

print(f"publications location: {publications.__file__}")
print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    from publications.ai_utils import generate_summary_from_text
    import inspect
    print(f"generate_summary_from_text location: {inspect.getfile(generate_summary_from_text)}")
except Exception as e:
    print(f"Error importing: {e}")
