import json
from datetime import datetime

def parse_text_log(file_content):
    logs = []
    current_time = datetime.now()
    for line in file_content.splitlines():
        if not line or not line.strip():
            continue
        logs.append({
            "timestamp": current_time.strftime('%Y-%m-%d %H:%M:%S') ,
            "level": "UNKNOWN",
            "message": line.strip()
        })
    return logs



def parse_json_log(file_content):
    logs = []
    for line in file_content.splitlines():
        try:
            log = json.loads(line)
            logs.append({
                "timestamp": log.get("time") or log.get("timestamp"),
                "level": log.get("level", "UNKNOWN"),
                "message": log.get("message") or log.get("msg")
            })
        except json.JSONDecodeError:
            continue
    return logs


def parse_log_file(filename, file_content):
    if filename.endswith(".json"):
        return parse_json_log(file_content)
    else:
        return parse_text_log(file_content)
