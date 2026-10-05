from datetime import datetime, timezone
from pathlib import Path


def extract_file_timeline(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("Evidence file not found")

    stat = path.stat()

    return [
        {
            "event_type": "FILE_CREATED",
            "event_time": datetime.fromtimestamp(
                stat.st_ctime,
                tz=timezone.utc
            ),
            "title": "Evidence File Created",
            "description": f"File {path.name} was created.",
            "source": path.name,
            "severity": "Informational"
        },
        {
            "event_type": "FILE_MODIFIED",
            "event_time": datetime.fromtimestamp(
                stat.st_mtime,
                tz=timezone.utc
            ),
            "title": "Evidence File Modified",
            "description": f"File {path.name} was last modified.",
            "source": path.name,
            "severity": "Informational"
        }
    ]