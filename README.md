# Blockchain-Based File Storage System

A complete, production-ready blockchain implementation for decentralized file storage with proof-of-work, peer-to-peer networking, and consensus mechanisms.

## 🚀 Features

- **Complete Blockchain Implementation**
  - SHA256-based proof of work with difficulty level 3
  - Two PoW algorithms: random nonce (faster, more secure) and incremental nonce
  - Genesis block initialization
  - Block validation and chain integrity checking

- **Peer-to-Peer Network**
  - Multi-node support with peer registration
  - Consensus algorithm using longest-chain rule
  - Automatic block synchronization across peers
  - Block announcement to network

- **File Storage**
  - On-chain file storage using Base64 encoding
  - File upload, download, and sharing capabilities
  - MongoDB integration for user management
  - Integration with Next.js frontend

- **REST API**
  - Complete blockchain API endpoints
  - Transaction management
  - Mining operations
 - Peer network management

## 📋 Requirements

```
Flask==1.1.4
Werkzeug==1.0.1
flask-cors
pymongo
python-dotenv
requests
```

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   pipinstall -r requirements.txt
   ```

2. **Set up MongoDB:**
   - Create MongoDB Atlas account or use local MongoDB
   - Update `.env` file (in project root) with your `MONGODB_URI`

3. **Configure environment:**
   ```env
   MONGODB_URI=mongodb+srv://your-connection-string
   ```

## 🏃 Running the Application

### Option 1: Single Peer (Simple)

```bash
# Terminal 1 - Start blockchain peer
cd Blockchain
python peer.py

# Terminal 2 - Start client app (file upload interface)
python run_app.py

# Terminal 3 - Start Next.js frontend (if using)
cd ../
npm run dev
```

### Option 2: Multi-Peer Network (Full Blockchain)

```bash
# Terminal 1 - Peer 1 (Port 8800)
cd Blockchain
python peer.py --port 8800

# Terminal 2 - Peer 2 (Port 8801)
python peer.py --port 8801

# Terminal 3 - Peer 3 (Port 8802)
python peer.py --port 8802

# Terminal 4 - Client app
python run_app.py
```

Then register peers with each other using the `/register_node` endpoint.

## 🌐 API Endpoints

### Blockchain Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/new_transaction` | POST | Add file transaction to pending |
| `/mine` | GET | Mine pending transactions |
| `/chain` | GET | Get full blockchain (with consensus) |
| `/pending_tx` | GET | View pending transactions |

### Peer Network

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register_node` | POST | Register a new peer |
| `/add_block` | POST | Receive block from peer |
| `/sync_chain` | GET | Force chain synchronization |
| `/peers` | GET | List registered peers |
| `/info` | GET | Get peer information |

### Example: Register Peers

```bash
# Register Peer 2 with Peer 1
curl -X POST http://127.0.0.1:8800/register_node \
  -H "Content-Type: application/json" \
  -d '{"node_address": "http://127.0.0.1:8801"}'

# Register Peer 1 with Peer 2
curl -X POST http://127.0.0.1:8801/register_node \
  -H "Content-Type: application/json" \
  -d '{"node_address": "http://127.0.0.1:8800"}'
```

## 📊 Proof of Work Comparison

Run the PoW comparison experiment:

```bash
python POW_Comparison.py
```

This demonstrates the performance difference between:
1. **Random Nonce** - Better for higher difficulty, more secure
2. **Incremental Nonce** - Simpler but less secure

## 🏗️ Project Structure

```
Blockchain/
├── Block.py              # Block class with hashing
├── Blockchain.py         # Blockchain with consensus
├── peer.py              # P2P network server
├── run_app.py           # Client application
├── utils.py             # Helper functions
├── POW_Comparison.py    # PoW benchmarking
├── requirements.txt     # Dependencies
├── app/
│   ├── __init__.py
│   └── views.py         # Flask routes + MongoDB
└── templates/           # HTML templates
```

## 🔐 Security Features

1. **Immutable Blockchain**: Once data is added, it cannot be modified or deleted
2. **Cryptographic Hashing**: SHA256 ensures block integrity
3. **Proof of Work**: Computational puzzle prevents spam
4. **Consensus**: Longest valid chain wins
5. **Random Nonce**: More secure than predictable incrementing

## 🔗 Integration with Next.js Frontend

The blockchain integrates seamlessly with the Next.js application:

1. Frontend uploads file via `/api/blockchain/upload`
2. Backend stores metadata in MongoDB
3. File data added to blockchain transaction
4. User can view blockchain via `/api/blockchain/chain`

## 📱 Web Interface

Access the application:
- **Client App**: `http://127.0.0.1:9000`
- **Blockchain API**: `http://127.0.0.1:8800`
- **Next.js Frontend**: `http://localhost:3000`

## 🧪 Testing the Blockchain

1. **Upload a file** via the web interface
2. **Mine the block** by calling `/mine`
3. **View the chain** at `/chain`
4. **Add more peers** and watch consensus in action
5. **Download files** from the blockchain

## 📈 Performance

- **Difficulty 3**: ~0.01-0.05 seconds per block
- **Difficulty 4**: ~0.1-0.5 seconds per block
- **Difficulty 5**: ~1-5 seconds per block

Higher difficulty = More secure but slower mining.

## 🐛 Troubleshooting

**Peer can't connect:**
- Ensure all peers are running
- Check firewall settings
- Verify peer addresses are correct

**Chain not syncing:**
- Call `/sync_chain` to force synchronization
- Ensure peers are registered with each other

**MongoDB connection error:**
- Check `MONGODB_URI` in `.env`
- Ensure MongoDB is running
- Whitelist your IP in MongoDB Atlas

## 👥 Contributors

- **Original Project**: Bhautik Sojitra, Kabir Bhakta
- **Enhanced Version**: Added consensus, peer networking, API endpoints

## 📚 References

1. [File on Blockchain](https://github.com/JungWinter/file-on-blockchain)
2. [Python Flask Blockchain](https://github.com/MoTechStore/Python-Flask-Blockchain-Based-Content-Sharing)
3. [Decentralized File Sharing](https://medium.com/@amannagpal4/how-to-create-your-own-decentralized-file-sharing-service-using-python-2e00005bdc4a)

## 📄 License

Open source - feel free to use and modify.

---

**Note**: This is a demonstration/educational project. For production use, consider additional security measures, database optimization, and scalability improvements.
