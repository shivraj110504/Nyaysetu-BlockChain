# Import libraries
import random
import requests
from Block import Block

class Blockchain:
    """
    Blockchain class managing the chain, pending transactions, and consensus.
    Implements proof of work with two different nonce generation strategies.
    """
    
    # Difficulty for proof of work (number of leading zeros required)
    difficulty = 3
    
    def __init__(self, db=None):
        """
        Initialize blockchain with genesis block and sync with DB.
        
        Args:
            db: MongoDB database instance for persistence
        """
        self.pending = []  # Pending transactions waiting to be mined
        self.chain = []  # The blockchain
        self.peers = set()  # Set of peer nodes for consensus
        self.db = db
        
        # Try to load chain from DB
        loaded_chain = self.load_from_db() if self.db is not None else []
        
        if loaded_chain:
            self.chain = loaded_chain
            print(f"Loaded blockchain from DB: {len(self.chain)} blocks")
        else:
            # Create genesis block
            genesis_block = Block(0, [], "0")
            genesis_block.hash = genesis_block.generate_hash()
            self.chain.append(genesis_block)
            
            # Save genesis to DB if sync available
            if self.db is not None:
                self.save_block_to_db(genesis_block)
                print("Created and saved genesis block to DB")

    def load_from_db(self):
        """Load the blockchain from MongoDB."""
        if self.db is None: return []
        
        blocks_col = self.db["blocks"]
        cursor = blocks_col.find().sort("index", 1)
        
        chain = []
        for b_data in cursor:
            block = Block(
                b_data["index"],
                b_data["transactions"],
                b_data["prev_hash"]
            )
            block.timestamp = b_data.get("timestamp", block.timestamp)
            block.nonce = b_data.get("nonce", 0)
            block.hash = b_data.get("hash")
            chain.append(block)
        
        return chain

    def save_block_to_db(self, block):
        """Save a validated block to the MongoDB blocks collection."""
        if self.db is None: return
        
        blocks_col = self.db["blocks"]
        # Check if block already exists to avoid duplicates
        if blocks_col.find_one({"index": block.index}):
            return
            
        blocks_col.insert_one({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "prev_hash": block.prev_hash,
            "nonce": block.nonce,
            "hash": block.hash
        })
    
    def add_block(self, block, hashl):
        """
        Add a validated block to the chain.
        
        Args:
            block (Block): Block to add
            hashl (str): Hash of the block
            
        Returns:
            bool: True if block was added, False otherwise
        """
        if prev_hash == block.prev_hash and self.is_valid(block, hashl):
            block.hash = hashl
            self.chain.append(block)
            # Sync with DB
            self.save_block_to_db(block)
            return True
        return False
    
    def mine(self):
        """
        Mine pending transactions into a new block.
        
        Returns:
            int|bool: Index of mined block, or False if no pending transactions
        """
        if len(self.pending) > 0:
            last_block = self.last_block()
            
            # Create new block
            new_block = Block(
                last_block.index + 1,
                self.pending,
                last_block.hash
            )
            
            # Run proof of work (using random nonce by default)
            hashl = self.p_o_w(new_block)
            
            # Add block to chain
            self.add_block(new_block, hashl)
            
            # Clear pending transactions
            self.pending = []
            
            return new_block.index
        return False
    
    def p_o_w(self, block):
        """
        Proof of Work using random nonce generation.
        This method provides better security and performance at higher difficulties.
        
        Args:
            block (Block): Block to mine
            
        Returns:
            str: Valid hash meeting difficulty requirement
        """
        block.nonce = 0
        get_hash = block.generate_hash()
        
        while not get_hash.startswith("0" * Blockchain.difficulty):
            block.nonce = random.randint(0, 99999999)
            get_hash = block.generate_hash()
        
        return get_hash
    
    def p_o_w_2(self, block):
        """
        Proof of Work using incremental nonce.
        Alternative method that increments nonce sequentially.
        
        Args:
            block (Block): Block to mine
            
        Returns:
            str: Valid hash meeting difficulty requirement
        """
        block.nonce = 0
        get_hash = block.generate_hash()
        
        while not get_hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            get_hash = block.generate_hash()
        
        return get_hash
    
    def add_pending(self, transaction):
        """
        Add a new transaction to pending list.
        
        Args:
            transaction: Transaction data to add
        """
        self.pending.append(transaction)
    
    def check_chain_validity(self, chain):
        """
        Check if a given chain is valid.
        
        Args:
            chain (list): List of blocks to validate
            
        Returns:
            bool: True if chain is valid, False otherwise
        """
        result = True
        prev_hash = "0"
        
        for block in chain:
            block_hash = block.hash
            
            # Verify hash validity and linkage
            if self.is_valid(block, block.hash) and prev_hash == block.prev_hash:
                block.hash = block_hash
                prev_hash = block_hash
            else:
                result = False
                break
        
        return result
    
    def is_valid(self, block, block_hash):
        """
        Check if a block's hash is valid.
        
        Args:
            block (Block): Block to validate
            block_hash (str): Hash to verify
            
        Returns:
            bool: True if hash is valid, False otherwise
        """
        # Check if hash meets difficulty requirement
        if block_hash.startswith("0" * Blockchain.difficulty):
            # Verify hash matches block data
            if block.generate_hash() == block_hash:
                return True
        return False
    
    def last_block(self):
        """
        Get the last block in the chain.
        
        Returns:
            Block: Last block in chain
        """
        return self.chain[-1]
    
    # ========== CONSENSUS MECHANISM ==========
    
    def register_peer(self, peer_address):
        """
        Register a new peer node.
        
        Args:
            peer_address (str): URL of peer node (e.g., "http://127.0.0.1:8801")
        """
        self.peers.add(peer_address)
    
    def consensus(self):
        """
        Consensus algorithm - longest chain wins.
        Replaces our chain with the longest valid chain from peers.
        
        Returns:
            bool: True if chain was replaced, False otherwise
        """
        longest_chain = None
        current_len = len(self.chain)
        
        # Check all peer nodes
        for peer in self.peers:
            try:
                response = requests.get(f"{peer}/chain", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    length = data['length']
                    chain_data = data['chain']
                    
                    # Reconstruct chain from JSON
                    chain = []
                    for block_data in chain_data:
                        block = Block(
                            block_data['index'],
                            block_data['transactions'],
                            block_data['prev_hash']
                        )
                        block.timestamp = block_data.get('timestamp', block.timestamp)
                        block.nonce = block_data['nonce']
                        block.hash = block_data['hash']
                        chain.append(block)
                    
                    # Keep track of longest valid chain
                    if length > current_len and self.check_chain_validity(chain):
                        current_len = length
                        longest_chain = chain
            except Exception as e:
                # Skip peer if unreachable
                print(f"Error connecting to peer {peer}: {e}")
                continue
        
        # Replace chain if longer valid chain found
        if longest_chain:
            self.chain = longest_chain
            return True
        
        return False
    
    def announce_block(self, block):
        """
        Announce a newly mined block to all peers.
        
        Args:
            block (Block): Block to announce
        """
        for peer in self.peers:
            try:
                url = f"{peer}/add_block"
                block_data = {
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "transactions": block.transactions,
                    "prev_hash": block.prev_hash,
                    "nonce": block.nonce,
                    "hash": block.hash
                }
                requests.post(url, json=block_data, timeout=2)
            except Exception as e:
                print(f"Error announcing block to {peer}: {e}")
                continue
