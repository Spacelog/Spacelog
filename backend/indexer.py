import redis
import pprint

from parser import FileParser

if __name__ == "__main__":
    indexer = FileParser("../transcript-file-format/a13/TEC")
    pprint.pprint(list(indexer.get_chunks()))



