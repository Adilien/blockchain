import hashlib
import json
from flask import Flask, jsonify, request
from time import time
from uuid import uuid4


class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # genesis block
        self.new_block(previous_hash=1, proof=100)

    # add a new block to the chain
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)

        return block

    # add a new transaction to the list of transactions
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_block):

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        if guess_hash[:4] == "0000":
            return True

        return False

    # hash a block by using SHA-256 hash function
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # return last block in the chain
    @property
    def last_block(self):
        return self.chain[-1]


# setting up Flask
app = Flask(__name__)
identify_node = str(uuid4()).replace('-', '')
blockchain = BlockChain()


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']

    if not all(fields in values for fields in required):
        return 'Missing fields', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}

    return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = blockchain.last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient=identify_node,
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'New Block has been forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


