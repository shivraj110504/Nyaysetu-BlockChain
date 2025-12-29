import base64
import json
import os
import requests
import uuid
from flask import render_template, redirect, request, send_file, session, flash, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from app import app
from timeit import default_timer as timer
from pymongo import MongoClient
from dotenv import load_dotenv
# Import blockchain classes for peer functionality
from Blockchain import Blockchain as BlockchainClass
from Block import Block

# Load environment variables from the root .env file (2 levels up)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path)

app.secret_key = "super_secret_key_for_hackathon" # Set a secret key for sessions

# Production-ready CORS configuration
# Allow all origins for easier deployment - you can restrict this later
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Allow all origins (Vercel, localhost, etc.)
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False,  # Set to False when using origins="*"
        "expose_headers": ["Content-Type"]
    }
})

# MongoDB Connection
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/file_storage")
client = MongoClient(MONGODB_URI)
db = client["file_storage"] # Explicitly use file_storage database
users_col = db["users"]
files_col = db["files"]

# Initialize Blockchain (for peer functionality)
blockchain = BlockchainClass(db=db)

# Stores all the post transaction in the node
request_tx = []
#store filename
files = {}
#destiantion for upload files
UPLOAD_FOLDER = "app/static/Uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# store  address
ADDR = os.environ.get("BLOCKCHAIN_NODE_ADDR", "http://127.0.0.1:8800")

#create a list of requests that peers has send to upload files
def get_tx_req():
    global request_tx
    try:
        # Get chain data directly from blockchain object (no HTTP call needed)
        content = []
        for block in blockchain.chain:
            # block.transactions is a list of transaction dicts
            for trans in block.transactions:
                trans_copy = trans.copy()
                trans_copy["index"] = block.index
                trans_copy["hash"] = block.prev_hash
                content.append(trans_copy)
        request_tx = sorted(content, key=lambda k: k["hash"], reverse=True)
    except Exception as e:
        print(f"DEBUG: Error in get_tx_req: {e}")
        request_tx = []


# Loads and runs the home page
@app.route("/")
def index():
    get_tx_req()
    user_key = session.get("user_key")
    username = session.get("username")
    
    my_files = []
    
    if user_key:
        # Find my files
        cursor = files_col.find({"owner": user_key})
        for f_data in cursor:
            my_files.append({
                "filename": f_data["filename"],
                "file_key": f_data["file_key"]
            })

    return render_template("index.html",
                           title="FileStorage",
                           subtitle="A Decentralized Network for File Storage/Sharing",
                           node_address=ADDR,
                           request_tx=request_tx,
                           user_key=user_key,
                           username=username,
                           my_files=my_files)


@app.route("/api/get_key/<string:username>", methods=["GET"])
def get_key(username):
    user = users_col.find_one({"username": username})
    if user:
        return jsonify({"user_key": user["key"]})
    return jsonify({"error": "User not found"}), 404

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    print(f"DEBUG: Registering user: {username}")
    
    user = users_col.find_one({"username": username})
    
    if user:
        print(f"DEBUG: User found. Key: {user['key']}")
        session["user_key"] = user["key"]
        session["username"] = username
    else:
        print("DEBUG: User NOT found. Creating new key.")
        # Generate new key
        new_key = str(uuid.uuid4())
        users_col.insert_one({"username": username, "key": new_key})
        session["user_key"] = new_key
        session["username"] = username
        print(f"DEBUG: New key generated: {new_key}")
        
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/submit", methods=["POST"])
# When new transaction is created it is processed and added to transaction
def submit():
    # Get userKey from form data (passed from Next.js)
    user_key = request.form.get("userKey")
    username_from_form = request.form.get("username")
    
    if not user_key:
        print("DEBUG: No userKey in form data during submit")
        return jsonify({"error": "Missing userKey"}), 400
        
    start = timer()
    # Get username from form or session
    user = username_from_form or session.get("username", "unknown")
    print(f"DEBUG: Submitting file for user: {user}, Key: {user_key}")

    up_file = request.files.get("v_file")
    
    if not up_file or up_file.filename == '':
        return jsonify({"error": "No file provided"}), 400

    # Read file content upfront to avoid stream exhaustion
    file_content = up_file.read()
    file_size = len(file_content)
    
    # Create a unique filename to avoid collisions
    timestamp = int(timer() * 1000)
    unique_id = str(uuid.uuid4())[:8]
    original_filename = up_file.filename
    secure_name = f"{timestamp}_{unique_id}_{secure_filename(original_filename)}"
    
    # Save the uploaded file in destination (for immediate access)
    upload_path = os.path.join("app/static/Uploads/", secure_name)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    with open(upload_path, "wb") as f:
        f.write(file_content)
        
    # Generate File Key
    file_key = str(uuid.uuid4())
    
    # Store file content in MongoDB for persistence across server restarts
    # This is critical for Render's ephemeral filesystem
    file_base64 = base64.b64encode(file_content).decode('utf-8')
    
    # Save Metadata + Content to MongoDB
    files_col.insert_one({
        "file_key": file_key,
        "filename": original_filename, 
        "secure_name": secure_name,   
        "owner": user_key,
        "shared_with": [],
        "file_content": file_base64,
        "file_size": file_size,
        "created_at": timer()
    })
    print(f"DEBUG: File saved to MongoDB. FileKey: {file_key}, Owner: {user_key}")

    # Create a transaction object
    post_object = {
        "user": user,
        "v_file" : original_filename,
        "file_key": file_key,
        "file_data" : "Binary Content Stored in DB", # Placeholder for chain view
        "file_size" : file_size
    }
   
    # Submit transaction directly to blockchain
    blockchain.add_pending(post_object)
    print(f"DEBUG: Transaction added to blockchain pending transactions")
    
    end = timer()
    print(f"DEBUG: Upload completed in {end - start}s")
    return jsonify({"success": True, "message": "File uploaded successfully", "file_key": file_key}), 200

@app.route("/share", methods=["POST"])
def share_file():
    # Get data from form (for Next.js API compatibility)
    file_key = request.form.get("file_key")
    recipient_key = request.form.get("recipient_key")
    owner_key = request.form.get("userKey") or session.get("user_key")
    
    if not file_key or not recipient_key or not owner_key:
        return jsonify({"error": "Missing required fields"}), 400
    
    print(f"DEBUG: Sharing file {file_key} from {owner_key} to {recipient_key}")
    
    # Check ownership and share
    result = files_col.update_one(
        {"file_key": file_key, "owner": owner_key},
        {"$addToSet": {"shared_with": recipient_key}}
    )
    
    if result.matched_count == 0:
        print(f"DEBUG: File not found or not owned by {owner_key}")
        return jsonify({"error": "File not found or not owned by you"}), 404
    
    if result.modified_count > 0:
        print(f"DEBUG: File shared successfully")
        return jsonify({"success": True, "message": "File shared successfully"}), 200
    else:
        print(f"DEBUG: File already shared with this user")
        return jsonify({"success": True, "message": "File already shared with this user"}), 200


@app.route("/view_shared", methods=["POST"])
def view_shared():
    # Get keys from form data (for Next.js API compatibility)
    sender_key = request.form.get("sender_key")
    my_key = request.form.get("userKey") or session.get("user_key")
    
    if not sender_key or not my_key:
        return jsonify({"error": "Missing sender_key or userKey"}), 400
    
    shared_files = []
    
    # Find files shared by sender_key with my_key
    cursor = files_col.find({"owner": sender_key, "shared_with": my_key})
    for f_val in cursor:
        shared_files.append({
            "filename": f_val["filename"],
            "file_key": f_val["file_key"],
            "secure_name": f_val["secure_name"]
        })
    
    # If called from API, return JSON
    if request.form.get("userKey"):
        return jsonify({"files": shared_files}), 200
    
    # If called from Flask template, render HTML
    return render_template("shared_files.html", files=shared_files)

#creates a download link for the file
@app.route("/download/<string:file_key>", methods = ["GET"])
def download_file_key(file_key):
    f_data = files_col.find_one({"file_key": file_key})
    
    if f_data:
        p = os.path.join(app.root_path, "static" , "Uploads", f_data["secure_name"])
        
        # Check if file exists on disk. If not, restore from MongoDB.
        if not os.path.exists(p):
            print(f"DEBUG: File {p} missing from disk. Restoring from MongoDB.")
            if "file_content" in f_data:
                try:
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                    content = base64.b64decode(f_data["file_content"])
                    with open(p, "wb") as f:
                        f.write(content)
                except Exception as e:
                    print(f"DEBUG: Error restoring file: {e}")
                    return "Error restoring file from cloud storage", 500
            else:
                return "File content not found in database", 404
                
        return send_file(p, as_attachment=True, download_name=f_data["filename"])
            
    return "File not found or access denied"

@app.route("/submit/<string:variable>",methods = ["GET"])
def download_file(variable):
    p = os.path.join(app.root_path, "static" , "Uploads", secure_filename(variable))
    return send_file(p,as_attachment=True)


# ========== BLOCKCHAIN PEER ROUTES (merged from peer.py) ==========

@app.route("/new_transaction", methods=["POST"])
def new_transaction():
    """Add new transaction to the blockchain"""
    file_data = request.get_json()
    required_fields = ["user", "v_file", "file_data", "file_size"]
    
    for field in required_fields:
        if not file_data.get(field):
            return "Transaction does not have valid fields!", 404
    
    blockchain.add_pending(file_data)
    return "Success", 201


@app.route("/chain", methods=["GET"])
def get_chain():
    """Get the entire blockchain"""
    chain = []
    for block in blockchain.chain:
        # Call __dict__() as a method, not attribute
        chain.append(block.__dict__())
    
    print("Chain Len: {0}".format(len(chain)))
    return json.dumps({"length": len(chain), "chain": chain})


@app.route("/mine", methods=["GET"])
def mine_unconfirmed_transactions():
    """Mine pending transactions"""
    result = blockchain.mine()
    if result:
        return "Block #{0} mined successfully.".format(result)
    else:
        return "No pending transactions to mine."


@app.route("/pending_tx")
def get_pending_tx():
    """Get pending transactions"""
    return json.dumps(blockchain.pending)


@app.route("/add_block", methods=["POST"])
def validate_and_add_block():
    """Validate and add a block to the chain"""
    block_data = request.get_json()
    
    # Create a new block with the received data
    block = Block(
        block_data["index"],
        block_data["transactions"],
        block_data["prev_hash"]
    )
    hashl = block_data["hash"]
    
    # Try to add the block
    added = blockchain.add_block(block, hashl)
    
    if not added:
        return "The Block was discarded by the node.", 400
    
    return "The block was added to the chain.", 201
