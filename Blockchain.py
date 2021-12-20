import json
import hashlib
from uuid import uuid4
from time import time
from Block import Block 
from typing import List
from urllib.parse import urlparse
from flask import jsonify, Flask, request
from re import match


class Blockchain:
    def __init__(self) -> None:
        # first we hardcode the genesis block
        self._genesis = {'index': 0, 
        'hash': hashlib.sha256("thisisthegenesisblock".encode()).hexdigest(),  
        'prev_hash': None, 
        'timestamp':time(), 
        'data': 'my genesis block!!'};
        
        self._chain = [self._genesis]
        self._current_transactions = []
        self._nodes = set()

    @property
    def size(self):
        return len(self._chain)

    @property
    def last_block(self) -> dict:
        if len(self._chain) == 0:
            return None
        return self._chain[-1]

    def new_block(self) -> dict:
        """ Add a new block to the chain"""
        tail = self.last_block()
        next_index = tail.index+1
        next_timestamp = time()
        return Block(next_index, tail.hash, next_timestamp, str(self._current_transactions))

    def verify_block(self, block : Block, previous_block : Block) -> bool:
        if previous_block.index + 1 != block.index:
            return False
        if previous_block.hash != block.prev_hash:
            return False
        return True

    def verify_chain(self, chain : List[Block]) -> bool:
        if chain[0] != self._genesis:
            return False
        for i in range(1, self.size):
            block = chain._chain[i]
            prev_block = chain._chain[i-1]
            if not self.verify_block(block, prev_block):
                return False
        return True

    def replaceChain(self, chain: List[Block]) -> bool:
        if not self.verify_chain(chain):
            return False
        if self.size >= len(chain):
            return False
        self._chain = chain
        return True

    def new_transaction(self, sender, recipient, amount):
        self._current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block.index+1
    
    def register_node(self, address):
        if not match(r'https?://', address):
            address = 'http://'+address
        parsed_url = urlparse(address)
        self._nodes.add(parsed_url.netloc)
        print(f"Added node at address {parsed_url}")


app = Flask(__name__)

node_indenfifier = str(uuid4()).replace('-','')

blockchain = Blockchain()


@app.route("/mine", methods=['GET'])
def mine():
    pass

@app.route("/transactions/new", methods=['POST'])
def new_transaction():
    values = request.get_json()
    
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return "Missing values",400
    
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    res = {'message': f"Transaction will be added to block: {index}"}
    return jsonify(res), 201

@app.route("/nodes/register", methods=['POST'])
def add_peers():
    
    values = request.get_json()
    nodes = values.get('nodes')
    
    if not nodes:
        return "Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    res = {
        'message': "New nodes have been added",
        'node_list': list(blockchain._nodes)
    }

    return jsonify(res), 200

@app.route("/nodes/list", methods=['GET'])
def get_peers():
    res = {
        'peers': list(blockchain._nodes)
    }
    return jsonify(res), 200

@app.route("/chain", methods=['GET'])
def get_chain():
    #print(json.dumps(blockchain._chain, sort_keys=True, default=lambda o: o.__dict__))
    res = {
        'chain': json.dumps(blockchain._chain, sort_keys=True, default=lambda o: o.__dict__),
        'size': blockchain.size
    }
    return jsonify(res), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)