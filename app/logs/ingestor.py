from app.logs.file_reader import read_log_file_from_offset
from app.logs.parser import parse_log_file
from app.models.log_entry import LogEntry
from app.extensions import db
from datetime import datetime


def ingest_logs_from_source(source):
    # Read only NEW content
    content, new_offset = read_log_file_from_offset(
        source.file_path,
        source.last_read_offset or 0
    )

    if not content.strip():
        return  # No new logs

    parsed_logs = parse_log_file(source.file_path, content)

    for log in parsed_logs:
        entry = LogEntry(
            timestamp=log.get("timestamp"),
            level=log.get("level"),
            message=log.get("message"),
            source_id=source.id
        )
        db.session.add(entry)

    # Update offset AFTER successful insert
    source.last_read_offset = new_offset
    db.session.add(source)

    db.session.commit()
