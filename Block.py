from hashlib import sha256
import json

def Block(index : int, prev_hash : str, 
                timestamp : int, data="") -> None:
    return {
        'index': index,
        'hash': hash(index, prev_hash, timestamp, data),
        'prev_hash': prev_hash,
        'timestamp': timestamp,
        'data': data
    }
    

def hash(index : int, prev_hash : str, timestamp : int, data=""):
    return str(sha256(str(index) + prev_hash + str(timestamp) + data));



