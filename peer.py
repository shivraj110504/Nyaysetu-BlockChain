# Import libraries
import json
import argparse
from flask import Flask, request, jsonify
from Blockchain import Blockchain
from Block import Block

# Create Flask app
app = Flask(__name__)

# Create blockchain instance
blockchain = Blockchain()

# Store port for this peer
peer_port = 8800


@app.route("/new_transaction", methods=["POST"])
def new_transaction():
    """
    Add a new transaction to pending transactions.
    
    Request body should contain:
    - user: Username
    - v_file: Filename
    - file_data: File content (Base64 encoded)
    - file_size: Size of file in bytes
    """
    file_data = request.get_json()
    required_fields = ["user", "v_file", "file_data", "file_size"]
    
    # Validate required fields
    for field in required_fields:
        if not file_data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    # Add to pending transactions
    blockchain.add_pending(file_data)
    
    return jsonify({"message": "Transaction added to pending"}), 201


@app.route("/chain", methods=["GET"])
def get_chain():
    """
    Get the entire blockchain (after running consensus).
    This ensures we return the most up-to-date chain.
    """
    # Run consensus to sync with peers
    blockchain.consensus()
    
    # Convert chain to JSON-serializable format
    chain = []
    for block in blockchain.chain:
        chain.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "prev_hash": block.prev_hash,
            "nonce": block.nonce,
            "hash": block.hash
        })
    
    print(f"Chain Len: {len(chain)}")
    
    return jsonify({
        "length": len(chain),
        "chain": chain
    })


@app.route("/mine", methods=["GET"])
def mine_unconfirmed_transactions():
    """
    Mine pending transactions into a new block.
    After mining, announce the block to all peers.
    """
    result = blockchain.mine()
    
    if result:
        # Get the newly mined block
        new_block = blockchain.chain[result]
        
        # Announce to all peers
        blockchain.announce_block(new_block)
        
        return jsonify({
            "message": f"Block #{result} mined successfully",
            "index": result,
            "hash": new_block.hash
        }), 200
    else:
        return jsonify({"message": "No pending transactions to mine"}), 200


@app.route("/pending_tx")
def get_pending_tx():
    """Get all pending transactions."""
    return jsonify({
        "count": len(blockchain.pending),
        "transactions": blockchain.pending
    })


@app.route("/add_block", methods=["POST"])
def validate_and_add_block():
    """
    Receive and validate a block from another peer.
    Add it to the chain if valid.
    """
    block_data = request.get_json()
    
    # Create block from received data
    block = Block(
        block_data["index"],
        block_data["transactions"],
        block_data["prev_hash"]
    )
    block.timestamp = block_data.get("timestamp", block.timestamp)
    block.nonce = block_data["nonce"]
    hashl = block_data["hash"]
    
    # Try to add the block
    added = blockchain.add_block(block, hashl)
    
    if not added:
        return jsonify({"message": "Block discarded by node"}), 400
    
    return jsonify({"message": "Block added to chain"}), 201


@app.route("/register_node", methods=["POST"])
def register_node():
    """
    Register a new peer node.
    
    Request body should contain:
    - node_address: Full URL of peer (e.g., "http://127.0.0.1:8801")
    """
    node_address = request.get_json().get("node_address")
    
    if not node_address:
        return jsonify({"error": "Missing node_address"}), 400
    
    # Add peer to our list
    blockchain.register_peer(node_address)
    
    # Return current chain for the new peer to sync
    chain = []
    for block in blockchain.chain:
        chain.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "prev_hash": block.prev_hash,
            "nonce": block.nonce,
            "hash": block.hash
        })
    
    
    return jsonify({
        "message": "Node registered successfully",
        "total_peers": len(blockchain.peers),
        "chain": chain
    }), 201


@app.route("/sync_chain", methods=["GET"])
def sync_chain():
    """
    Force synchronization with all peers using consensus.
    Returns whether the chain was updated.
    """
    replaced = blockchain.consensus()
    
    if replaced:
        return jsonify({
            "message": "Chain replaced with longer chain from network",
            "length": len(blockchain.chain)
        }), 200
    else:
        return jsonify({
            "message": "Chain is up to date",
            "length": len(blockchain.chain)
        }), 200


@app.route("/peers", methods=["GET"])
def get_peers():
    """Get list of registered peer nodes."""
    return jsonify({
        "count": len(blockchain.peers),
        "peers": list(blockchain.peers)
    })


@app.route("/info", methods=["GET"])
def get_info():
    """Get blockchain information."""
    return jsonify({
        "port": peer_port,
        "chain_length": len(blockchain.chain),
        "pending_transactions": len(blockchain.pending),
        "difficulty": blockchain.difficulty,
        "peers": len(blockchain.peers)
    })


if __name__ == "__main__":
    # Parse command line arguments for port
    parser = argparse.ArgumentParser(description='Run blockchain peer node')
    parser.add_argument('--port', type=int, default=8800, help='Port to run peer on')
    args = parser.parse_args()
    
    peer_port = args.port
    
    print(f"Starting blockchain peer on port {peer_port}")
    print(f"Difficulty: {blockchain.difficulty}")
    print(f"Genesis block hash: {blockchain.chain[0].hash}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=peer_port, debug=True)
