from __future__ import with_statement
import string
try:
    import json
except ImportError:
    import simplejson as json
from backend.util import timestamp_to_seconds, seconds_to_timestamp

class TranscriptParser(object):
    """
    Runs through a transcript file working out and storing the
    byte offsets.
    """

    def __init__(self, path):
        self.path = path

    def get_lines(self, offset):
        with open(self.path) as fh:
            fh.seek(offset)
            for line in fh:
                yield line

    def get_chunks(self, offset=0):
        """
        Reads the log lines from the file in order and yields them.
        """
        current_chunk = None
        reuse_line = None
        lines = iter(self.get_lines(offset))
        while lines or reuse_line:
            # If there's a line to reuse, use that, else read a new
            # line from the file.
            if reuse_line:
                line = reuse_line
                reuse_line = None
            else:
                try:
                    line = lines.next()
                except StopIteration:
                    break
                offset += len(line)
                line = line.decode("utf8")
            # If it's a comment or empty line, ignore it.
            if not line.strip() or line.strip()[0] == "#":
                continue
            # If it's a timestamp header, make a new chunk object.
            elif line[0] == "[":
                # Read the timestamp
                try:
                    timestamp = int(line[1:].split("]")[0])
                except ValueError:
                    timestamp = timestamp_to_seconds(line[1:].split("]")[0])
                if current_chunk:
                    yield current_chunk
                # Start a new log line item
                current_chunk = {
                    "timestamp": timestamp,
                    "lines": [],
                    "meta": {},
                    "offset": offset - len(line),
                }
            # If it's metadata, read the entire thing.
            elif line[0] == "_":
                # Meta item
                name, blob = line.split(":", 1)
                while True:
                    try:
                        line = lines.next()
                    except StopIteration:
                        break
                    offset += len(line)
                    line = line.decode("utf8")
                    if not line.strip() or line.strip()[0] == "#":
                        continue
                    if line[0] in string.whitespace:
                        blob += line
                    else:
                        reuse_line = line
                        break
                # Parse the blob
                blob = blob.strip()
                if blob:
                    try:
                        data = json.loads(blob)
                    except ValueError:
                        try:
                            data = json.loads('"%s"' % blob)
                        except ValueError:
                            print "Error: Invalid json at timestamp %s, key %s" % \
                                            (seconds_to_timestamp(timestamp), name)
                            continue
                    current_chunk['meta'][name.strip()] = data
            # If it's a continuation, append to the current line
            elif line[0] in string.whitespace:
                # Continuation line
                if not current_chunk:
                    print "Error: Continuation line before first timestamp header. Timestamp %s" % \
                                                                        (seconds_to_timestamp(timestamp))
                elif not current_chunk['lines']:
                    print "Error: Continuation line before first speaker name. Timestamp %s" % \
                                                                        (seconds_to_timestamp(timestamp))
                else:
                    current_chunk['lines'][-1]['text'] += " " + line.strip()
            # If it's a new line, start a new line. Shock.
            else:
                # New line of speech
                try:
                    speaker, text = line.split(":", 1)
                except ValueError:
                    print "Error: First speaker line not in Name: Text format."
                else:
                    line = {
                        "speaker": speaker.strip(),
                        "text": text.strip(),
                    }
                    current_chunk['lines'].append(line)
        # Finally, if there's one last chunk, yield it.
        if current_chunk:
            yield current_chunk

class MetaParser(TranscriptParser):
    
    def get_meta(self):
        try:
            with open(self.path) as fh:
                return json.load(fh)
        except ValueError as e:
            raise ValueError("JSON decode error in file %s: %s" % (self.path, e))
        return json.load(fh)
