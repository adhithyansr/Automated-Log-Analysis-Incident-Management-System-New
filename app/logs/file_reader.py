def read_log_file(file_path):
    """
    Reads full file content.
    For now, re-reads entire file (manual update use case).
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_log_file_from_offset(file_path, offset):
    """
    Reads log file starting from the given byte offset.
    Handles file truncation (resets offset to 0 if file shrank).
    Returns (new_content, new_offset)
    """
    import os
    file_size = os.path.getsize(file_path)
    
    if offset > file_size:
        offset = 0
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(offset)
        content = f.read()
        new_offset = f.tell()

    return content, new_offset