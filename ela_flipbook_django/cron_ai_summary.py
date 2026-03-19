import os
import subprocess
import sys
from pathlib import Path

# Standalone script to run AI summary generation command
# Targeted for cron/scheduler use

def run_ai_cron():
    # Process 3 articles at once as requested
    limit = 3
    
    # Get the base directory of the project
    base_dir = Path(__file__).resolve().parent
    manage_py = base_dir / "manage.py"
    
    print("--- Starting AI Summary Cron Job ---")
    
    # Run the management command
    # Using sys.executable to ensure we use the same environment
    cmd = [sys.executable, str(manage_py), "generate_ai_summaries", "--limit", str(limit)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        
        if result.stderr:
            print("Errors:", result.stderr)
            
        if "Successfully generated summary" in result.stdout:
            print("Successfully processed articles in this batch.")
        elif "Processing 0 articles" in result.stdout:
            print("All articles have summaries. Cron job can be considered complete.")
            # Logic for disposal or disabling could go here
            
    except Exception as e:
        print(f"Failed to execute cron job: {e}")

if __name__ == "__main__":
    run_ai_cron()
