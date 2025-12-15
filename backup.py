# File: backup.py
import subprocess
from datetime import datetime
import config
import os

def backup_database(user, password):
    """Create a backup of the current database"""
    if not config.current_db:
        raise Exception("No database selected")

    os.makedirs("backups", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backups/{config.current_db}_{timestamp}.sql"

    cmd = [
        "mysqldump",
        "-u", user,
        f"-p{password}",
        "--routines",
        "--events",
        "--triggers",
        config.current_db
    ]

    with open(filename, "w") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Backup failed: {result.stderr}")

    return filename

def export_database(user, password):
    """Export the current database (same as backup but in exports folder)"""
    if not config.current_db:
        raise Exception("No database selected")

    os.makedirs("exports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exports/{config.current_db}_export_{timestamp}.sql"

    cmd = [
        "mysqldump",
        "-u", user,
        f"-p{password}",
        "--routines",
        "--events",
        "--triggers",
        "--complete-insert",  # Use complete INSERT statements
        config.current_db
    ]

    with open(filename, "w") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Export failed: {result.stderr}")

    return filename