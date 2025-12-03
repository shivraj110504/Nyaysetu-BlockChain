import requests
import os

BASE_URL = "http://localhost:9000"

def register(username):
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/register", data={"username": username})
    print(f"Register {username}: {resp.status_code}")
    return session

def get_user_key(session):
    resp = session.get(BASE_URL)
    # Parse HTML to find user key? Or just check data.json directly?
    # Let's check data.json directly for simplicity in this script, 
    # but strictly we should use the UI.
    # However, since I can't easily parse HTML here without bs4 (which might not be installed),
    # I'll read data.json if possible.
    # But I am running this script from the same machine, so I can read the file.
    import json
    if os.path.exists("app/data.json"):
        with open("app/data.json", "r") as f:
            data = json.load(f)
            # Find key for username
            # But I don't know the username stored in session easily without parsing.
            # Wait, I know the username I registered with.
            pass
            
    return resp.text

def verify():
    # 1. Register User A
    session_a = register("UserA")
    
    # 2. Register User B
    session_b = register("UserB")
    
    # Get Keys from data.json
    import json
    import time
    time.sleep(1) # Wait for file save
    
    with open("app/data.json", "r") as f:
        data = json.load(f)
        
    key_a = data["users"]["UserA"]
    key_b = data["users"]["UserB"]
    print(f"Key A: {key_a}")
    print(f"Key B: {key_b}")
    
    # 3. User A Uploads File
    # Create dummy file
    with open("test_upload.txt", "w") as f:
        f.write("This is a secret file.")
        
    files = {'v_file': open('test_upload.txt', 'rb')}
    resp = session_a.post(f"{BASE_URL}/submit", data={"user": "UserA"}, files=files)
    print(f"Upload: {resp.status_code}")
    
    # Get File Key
    with open("app/data.json", "r") as f:
        data = json.load(f)
        # Find file key for test_upload.txt
        file_key = None
        for k, v in data["files"].items():
            if v["filename"] == "test_upload.txt" and v["owner"] == key_a:
                file_key = k
                break
    
    print(f"File Key: {file_key}")
    
    # 4. User A Shares with User B
    resp = session_a.post(f"{BASE_URL}/share", data={
        "file_key": file_key,
        "recipient_key": key_b
    })
    print(f"Share: {resp.status_code}")
    
    # 5. User B Views Shared Files (from User A)
    resp = session_b.post(f"{BASE_URL}/view_shared", data={"sender_key": key_a})
    print(f"View Shared: {resp.status_code}")
    
    if "test_upload.txt" in resp.text:
        print("SUCCESS: File found in shared view.")
    else:
        print("FAILURE: File NOT found in shared view.")
        
    # 6. User B Downloads File
    resp = session_b.get(f"{BASE_URL}/download/{file_key}")
    print(f"Download: {resp.status_code}")
    if resp.text == "This is a secret file.":
        print("SUCCESS: File content verified.")
    else:
        print("FAILURE: File content mismatch.")

if __name__ == "__main__":
    verify()
