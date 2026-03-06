import os
import subprocess
import sys

def run_cmd(cmd):
    print(f"Running: {cmd}")
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"Error: {process.stderr}")
    else:
        print(process.stdout)

if __name__ == "__main__":
    print("--- Starting SmartPrice Setup ---")
    run_cmd("python manage.py makemigrations products")
    run_cmd("python manage.py makemigrations accounts")
    run_cmd("python manage.py migrate")
    print("--- Setup Complete ---")
