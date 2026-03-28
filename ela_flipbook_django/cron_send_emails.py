import os
import subprocess
import sys
from pathlib import Path

# Standalone script to run publication email notification command
# Targeted for cron/scheduler use

def run_email_cron():
    # Get the base directory of the project
    base_dir = Path(__file__).resolve().parent
    manage_py = base_dir / "manage.py"
    
    print("--- Starting Publication Email Notification Cron Job ---")
    
    # Run the management command
    # Using sys.executable to ensure we use the same environment
    cmd = [sys.executable, str(manage_py), "send_publication_emails"]
    
    try:
        # Run and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        
        if result.stderr:
            print("Errors (stderr):", result.stderr)
            
        if "Successfully sent notification emails" in result.stdout:
            print("Email notification process completed successfully.")
        elif "No new publications" in result.stdout:
            print("Nothing to send. Cron job complete.")
        else:
            print("Process completed.")
            
    except Exception as e:
        print(f"Failed to execute email cron job: {e}")

if __name__ == "__main__":
    run_email_cron()
