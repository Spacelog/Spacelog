import redis
import string
import simplejson
import pprint

class Indexer(object):
    """
    Runs through a transcript file working out and storing the
    byte offsets.
    """

    def __init__(self, filename):
        self.filename = filename

    def get_chunks(self):
        """
        Reads the log lines from the file in order and yields them.
        """
        with open(self.filename) as fh:
            current_chunk = None
            lines = list(reversed(list(fh)))
            while lines:
                line = lines.pop()
                if not line.strip() or line[0] == "#":
                    continue
                elif line[0] == "[":
                    # Read the timestamp
                    timestamp = int(line[1:].split("]")[0])
                    if current_chunk:
                        yield current_chunk
                    # Start a new log line item
                    current_chunk = {
                        "timestamp": timestamp,
                        "lines": [],
                        "meta": {},
                    }
                elif line[0] == "_":
                    # Meta item
                    name, blob = line.split(":", 1)
                    while True:
                        line = lines.pop()
                        if line[0] in string.whitespace:
                            blob += line
                        else:
                            lines.append(line)
                            break
                    # Parse the blob
                    try:
                        data = simplejson.loads(blob)
                    except simplejson.JSONDecodeError:
                        print "Error: Invalid json at timestamp %s, key %s" % (timestamp, name)
                    current_chunk['meta'][name.strip()] = data
                elif line[0] in string.whitespace:
                    # Continuation line
                    current_chunk['lines'][-1]['text'] += " " + line.strip()
                else:
                    # New line of speech
                    author, text = line.split(":", 1)
                    line = {
                        "author": author.strip(),
                        "text": text.strip(),
                    }
                    current_chunk['lines'].append(line)
            if current_chunk:
                yield current_chunk

if __name__ == "__main__":
    indexer = Indexer("test.txt")
    pprint.pprint(list(indexer.get_chunks()))


