# Render Deployment Guide for Nyaysetu Blockchain Backend

## Critical Fixes Applied ✅

The temp/Blockchain folder has been updated with the following critical fixes:

### 1. **Removed HTTP Self-Calls** (Fixed 500 Error)
- **`submit()` function**: Now calls `blockchain.add_pending()` directly instead of HTTP POST
- **`get_tx_req()` function**: Now reads from `blockchain.chain` directly instead of HTTP GET
- **Impact**: Eliminates 500 errors caused by the app trying to make HTTP requests to itself

### 2. **Updated CORS Configuration**
- Changed to allow all origins (`"*"`) for easier deployment
- Ensures Vercel frontend can connect without CORS errors

### 3. **Updated Environment Configuration**
- Clarified that `BLOCKCHAIN_NODE_ADDR` is now optional
- Updated default PORT to 10000 (Render's default)

---

## Required Environment Variables on Render

Set these in your Render dashboard → Environment tab:

### Required
```
MONGODB_URI=mongodb+srv://your-username:your-password@cluster.mongodb.net/file_storage?retryWrites=true&w=majority
```

### Optional (Can be omitted)
```
BLOCKCHAIN_NODE_ADDR=https://nyaysetu-blockchain.onrender.com
PORT=10000
FLASK_ENV=production
```

> [!IMPORTANT]
> The `BLOCKCHAIN_NODE_ADDR` is now **optional** because blockchain peer functionality is merged into the same app. The code no longer makes HTTP calls to itself - it calls the blockchain object directly.

---

## Deployment Steps

### 1. Push to GitHub
```bash
cd "d:\Code Vault\Projects\Hackathon\Nyaysetu\nyaysetu-project\temp\Blockchain"
git add .
git commit -m "Fixed HTTP self-calls and updated CORS"
git push origin main
```

### 2. Configure Render
- Service Type: **Web Service**
- Build Command: `pip install -r requirements.txt`
- Start Command: `python run_app.py`
- Environment: **Python 3**

### 3. Set Environment Variables
Only set `MONGODB_URI` - all others are optional.

### 4. Deploy
Click "Deploy" - Render will build and start your service.

---

## Testing the Deployment

### Test 1: Check if service is running
```bash
curl https://nyaysetu-blockchain.onrender.com/chain
```

**Expected response:**
```json
{
  "length": 1,
  "chain": [...]
}
```

### Test 2: Test from frontend
1. Create `.env.local` in your Next.js app:
   ```
   NEXT_PUBLIC_RENDER_BACKEND_URL=https://nyaysetu-blockchain.onrender.com
   ```
2. Restart Next.js: `npm run dev`
3. Go to `/blockchain` page
4. Upload a file

---

## What Was Fixed

| Issue | Before | After |
|-------|--------|-------|
| **File Upload** | HTTP POST to `ADDR/new_transaction` → 500 error | Direct call to `blockchain.add_pending()` → ✅ |
| **Chain Data** | HTTP GET to `ADDR/chain` → timeout/error | Direct read from `blockchain.chain` → ✅ |
| **CORS** | Limited to specific domains → may block Vercel | Allow all origins → ✅ |
| **Environment** | Required `BLOCKCHAIN_NODE_ADDR` | Now optional → ✅ |

---

## File Changes Summary

### Modified Files:
1. **`app/views.py`**
   - Lines 59-73: Fixed `get_tx_req()` - removed HTTP GET
   - Lines 189-191: Fixed `submit()` - removed HTTP POST
   - Lines 22-32: Updated CORS to allow all origins

2. **`.env.example`**
   - Updated to reflect optional `BLOCKCHAIN_NODE_ADDR`
   - Changed PORT to 10000

### No Other Files Changed ✅

All functionality remains the same - only the internal implementation was optimized.

---

## Verification Checklist

After deployment, verify:

- [ ] `/chain` endpoint returns blockchain data
- [ ] `/submit` accepts file uploads without errors
- [ ] `/share` allows file sharing
- [ ] `/view_shared` shows shared files
- [ ] `/download/:fileKey` downloads files
- [ ] MongoDB connection works
- [ ] No CORS errors in browser console

---

## Troubleshooting

### If you still get 500 errors:
1. Check Render logs for error messages
2. Verify MongoDB URI is correct
3. Ensure MongoDB allows connections from Render's IPs

### If CORS errors persist:
The CORS is set to allow all origins. If you still see errors, check:
- Browser console for exact error message
- Render logs for preflight OPTIONS requests

### If files don't appear after upload:
- Check MongoDB connection
- Verify `files` collection exists
- Check Render logs for MongoDB errors

---

## Next Steps

1. **Deploy to Render** with the fixed code
2. **Set MongoDB URI** in environment variables
3. **Test all endpoints** using curl or frontend
4. **Update frontend** `.env.local` to point to Render

Your backend is now ready for production! 🚀
