# Paste your version of blockchain.py from the basic_block_gp
# folder here

import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)
    
    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
​
        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block
​
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        if len(self.chain) > 0:
            block_string = json.dumps(self.last_block, sort_keys=True)
            guess = f'{block_string}{proof}'.encode()
            current_hash = hashlib.sha256(guess).hexdigest()
        else:
            current_hash = ""
            
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'hash': current_hash,
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block
        
    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block
​
        :param block": <dict> Block
        "return": <str>
        """
    
        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        # TODO: Hash this string using sha256
        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()
    
        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hex_hash

    def new_transaction(self, sender, recepient, amount):
        transaction = {
            "sender": sender,
            "recepient": recepient,
            "amount": float(amount),
            "timestamp": time(),
            "id": str(uuid4())
        }

        self.current_transactions.append(transaction)

        return self.current_transactions.index(transaction)


    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        guess = f"{block_string}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "000000" 
 
# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['POST'])
def mine():
    # Run the proof of work algorithm to get the next proof
    data = request.get_json()

    if 'proof' not in data or 'id' not in data:
        response = {
            'success' : 404,
            'message' : 'Missing id or proof',
        }
        
        return jsonify(response), 400

    proof = data['proof']
    recepeint = data['id']

    

    try:
        last_block = blockchain.last_block
        previous_hash = blockchain.hash(last_block)
        block = blockchain.new_block(proof, previous_hash)
        index = blockchain.new_transaction("0", recepeint, 1)


       
        response = {
            "status": "SUCCESS",
            "block": block,
            "reward": f"Reward amount: {index} qoins"
        }
    except ValueError:
        response = {
            'success' : False,
            'message' : 'Bad Proof'
        }



    return jsonify(response), 200
    

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last_block' : blockchain.chain[-1]
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def transactions():

    data =request.get_json()

    if 'sender' not in data or 'recipient' not in data or 'amount' not in data:

        response = {
            'success' : 404,
            'message' : 'Missing id or proof',
        }
        
        return jsonify(response), 400

    sender = data['sender']
    recipient = data['recipient']
    amount = data['amount']

    index = blockchain.new_transaction(sender, recipient, amount)

    response = {
        "message": f"Transactions will be included in block {index}"
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 