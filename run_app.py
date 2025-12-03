import os
from app import app

port = int(os.environ.get("PORT", 9000))
app.run(host = '0.0.0.0', port = port, debug=True)