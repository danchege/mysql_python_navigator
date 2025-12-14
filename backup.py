import subprocess
from datetime import datetime
import config
import os

def backup_database(user, password):
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
        subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)

    return filename
