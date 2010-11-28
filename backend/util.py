
def seconds_to_timestamp(seconds):
    return "%02i:%02i:%02i:%02i" % (
        seconds // 86400,
        seconds % 86400 // 3600,
        seconds % 3600 // 60,
        seconds % 60,
    )

def timestamp_to_seconds(timestamp):
    if timestamp[0]=='-':
        timestamp = timestamp[1:]
        mult = -1
    else:
        mult = 1
    parts = map(int, timestamp.split(":", 3))
    return mult * ((parts[0] * 86400) + (parts[1] * 3600) + (parts[2] * 60) + parts[3])

