import time
from hashlib import sha256
import json

# Multiple blocks linked together will make a blockchain
class Block:
    """
    Block class representing a single block in the blockchain.
    Each block contains index, timestamp, transactions, previous hash, and nonce.
    """
    
    def __init__(self, index, transactions, prev_hash):
        """
        Initialize a new block.
        
        Args:
            index (int): Index/position of the block in the chain
            transactions (list): List of transactions/file data
            prev_hash (str): Hash of the previous block
        """
        self.index = index
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.timestamp = time.time()  # Unix timestamp when block was created
        self.nonce = 0  # Nonce for proof of work
        self.hash = None  # Will be set after mining
    
    def generate_hash(self):
        """
        Generate SHA256 hash from all block data.
        
        Returns:
            str: Hexadecimal hash string
        """
        # Combine all block data
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "prev_hash": self.prev_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        
        return sha256(block_string.encode()).hexdigest()
    
    def compute_hash(self):
        """
        Alias for generate_hash() for compatibility.
        
        Returns:
            str: Hexadecimal hash string
        """
        return self.generate_hash()
    
    def add_t(self, transaction):
        """
        Add a transaction to the block's transaction list.
        
        Args:
            transaction: Transaction data to add
        """
        self.transactions.append(transaction)
    
    def __dict__(self):
        """
        Convert block to dictionary for JSON serialization.
        
        Returns:
            dict: Block data as dictionary
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "prev_hash": self.prev_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }