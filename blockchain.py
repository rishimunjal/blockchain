# Module 1 blockchain
#pip install Flask
#download desktop version of postman
import datetime
import hashlib
import json

#Part 1 building a blockchain

class blockchain:
    
    def __init__(self):
        self.chain = []
        
        #genesis block of the chain
        self.create_block(proof = 1, previous_hash = '0')
          
   #create block
    def create_block(self, proof, previous_hash):
        
        block = {'index':len(self.chain) + 1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash':previous_hash}
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
        
       
# create a web-app using flask

from flask import Flask, jsonify
app = Flask(__name__)

#create the blockchain 
blockchain = blockchain()

# mine http://127.0.0.1:5000/
@app.route('/mine_block', methods = ['GET'])

def mine_block():
    #solve proof of work based on proof in the last block
  
    previous_block = blockchain.get_previous_block()
    
    proof = blockchain.proof_of_work (previous_block ['proof'])
    previous_hash = blockchain.hash(previous_block)

    block = blockchain.create_block(proof, previous_hash)
    
    response = {'message': 'congratulation!! you just mined a new block.',
                'index': block['index'],
                'timestamp':block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}

    return jsonify(response,200)

#get full blockchain

@app.route('/get_chain',methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    return (jsonify(response,200))



@app.route('/is_valid', methods = ['GET'])
def is_valid():
    response  = {'is_chain_valid': blockchain.is_chain_valid(blockchain.chain)}
    
    return (jsonify(response,200))    
    
    
    

#run the app       

app.run(host = '0.0.0.0', port = '5000')