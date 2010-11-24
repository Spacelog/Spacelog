import redis
import pprint

from parser import FileParser

if __name__ == "__main__":
    indexer = FileParser("test.txt")
    pprint.pprint(list(indexer.get_chunks()))


