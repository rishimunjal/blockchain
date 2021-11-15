# Module 1 Cryptocurrency
#pip install Flask
#download desktop version of postman
#required only for a plain blockchain
import datetime
import hashlib
import json

#required for flask UI
#request module for creating nodes in a decentralized blockchain
from flask import Flask, jsonify,request

#to check nodes in the blockchain
import requests

#to create address of each node in the node
from uuid import uuid 
from urllib.parse import urlparse

#Part 1 building a blockchain
#create cryptocurrency (transactions make blockchain a cryptocurrency)
#add transactions + add consensus 

class blockchain:
    
    def __init__(self):
        self.chain = []
        #transactions before they are added to the block
        self.transactions = []
        
        #should not be in any particular order
        self.node = set()
        
        #genesis block of the chain
        self.create_block(proof = 1, previous_hash = '0')
          
   #create block
    def create_block(self, proof, previous_hash):
        
        block = {'index':len(self.chain) + 1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash':previous_hash,
                 'transactions': self.transactions}
        
        #clear the transactions once added to block
        self.transactions = []
        self.chain.append(block)
        
        return block
        
    def get_previous_block(self):
        return self.chain[-1]
     
    #mine block
    def proof_of_work(self, previous_proof):
        new_proof = 1 # Why 1 because we are going to increment by 1
        
        check_proof = False
        
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
                
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        
        previous_block = chain[0]
        
        block_index = 1
        
        while block_index < len(chain):
            
            current_block = chain[block_index]
            
            #has of previous block should be same as the previous hash of current block
            if current_block ['previous_hash'] != self.hash(previous_block):
                return False                
            
            #take proof of previous block, current proof, compute hash operation of previous / 
            hash_operation = hashlib.sha256(str(current_block['proof']**2 - previous_block['proof']**2).encode()).hexdigest()
            
            if hash_operation[:4] != "0000":
               return False
           
            previous_block = current_block
            current_block= chain[block_index]
            block_index += 1
            
        return True
        
    #methods for cryptocurrency
    def add_transactions ( self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        
        #retun the index where the block is to be added
        return previous_block['index'] + 1
    
    def add_node (self, address):
        parsedurl = urlparse(address)
        self.nodes.add(parsedurl.netloc)
        
    
    #called inside a specific node - thats why just 
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        
        max_length = len(self.blockchain)
        
        for node in network:
            response = requests.get('http://{node}/get_chain')
            
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                
        if longest_chain:
            self.chain = longest_chain
            return True
        
        
        return False
            
            
        
        
       
# create a web-app using flask
app = Flask(__name__)

#creating an address for the node on port 5000
# When miner mines - gets crypto .. therefore need address from the node address
#uuid will return randon unique id
node_address  = str(uuid.uuid4()).replace('-', '')


#create the blockchain 
blockchain = blockchain()


# mine http://127.0.0.1:5000/
@app.route('/mine_block', methods = ['GET'])

def mine_block():
    #solve proof of work based on proof in the last block
  
    previous_block = blockchain.get_previous_block()
    
    proof = blockchain.proof_of_work (previous_block ['proof'])
    blockchain.add_transactions(sender = node_address,reciever = 'Rishi', amount = 1 )
    
    previous_hash = blockchain.hash(previous_block)

    block = blockchain.create_block(proof, previous_hash)
    
    response = {'message': 'congratulation!! you just mined a new block.',
                'index': block['index'],
                'timestamp':block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactionss']}

    return jsonify(response,200)

#get full blockchain

#decentralize blockchain



@app.route('/get_chain',methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    return (jsonify(response,200))



@app.route('/is_valid', methods = ['GET'])
def is_valid():
    response  = {'is_chain_valid': blockchain.is_chain_valid(blockchain.chain)}
    
    return (jsonify(response,200))    
    

#add new transaction to blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    #announce transaction.. in POSTMAN we will create sender, reciever, amount
    json = request.get_json()
    
    keys = {'sender','receiver', 'amount'}
    
    if not all (key in json for key in keys):
        return 'missing keys',400
    
    index = blockchain.add_transactions(sender = json['sender'], receiver =  json['receiver'], amount = json['amount'])
    
    response = {'message': f'This transaciton will be added to block {index}'}
    
    return jsonify(response),201


#part 3 = decentralize block chain
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    
    json = request.get_json()
    nodes = json.get('nodes')
    
    if nodes is None:
        return 'no nodes', 400
    
    for node in nodes:
        blockchain.add_node(node)
        
    response = {'message': 'all the nodes are now connected. The Altcoin blockchain now contains the following nodes',
                'total_nodes': list(blockchain.nodes)}
    
    return jsonify(response), 201

        
@app.route('/replace_chain', methods = ['GET'])

def replace_chain():
    is_chain_replaced = blockchain.replace_chain()

    if is_chain_replaced:
        response = {'message': 'The nodes have different chain so the chain was replaced',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'all good - the chain is the largest',
                              'chain': blockchain.chain}

    return jsonify(response),200
#run the app       

app.run(host = '0.0.0.0', port = '5000')