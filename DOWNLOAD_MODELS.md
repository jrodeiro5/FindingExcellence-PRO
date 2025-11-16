# Download Ollama Models

## ✅ Ollama is Running!

Your Ollama service is running at `http://localhost:11434` ✅

## Step 1: Download Models

Open **Command Prompt** and run these commands **one at a time**:

### Command 1: Download Primary Text Model (llama3.1:8b)
```cmd
ollama pull llama3.1:8b
```
**Size:** ~4.7 GB  
**Time:** 5-15 minutes (depends on internet speed)  
**Wait for:** "pulling digest..." messages to complete

---

### Command 2: Download Vision/OCR Model (qwen2.5-vl:7b)
```cmd
ollama pull qwen2.5-vl:7b
```
**Size:** ~4.4 GB  
**Time:** 5-15 minutes  
**Wait for:** "pulling digest..." messages to complete

---

### Command 3: Download Fast Fallback Model (deepseek-r1:1.5b)
```cmd
ollama pull deepseek-r1:1.5b
```
**Size:** ~1 GB  
**Time:** 2-5 minutes  
**Optional:** If this fails, continue anyway (fallback model)

---

## Step 2: Verify Models Downloaded

```cmd
ollama list
```

**Expected output:**
```
NAME                  ID              SIZE      MODIFIED
llama3.1:8b          abcd1234...     4.7GB     2 minutes ago
qwen2.5-vl:7b        efgh5678...     4.4GB     1 minute ago
deepseek-r1:1.5b     ijkl9012...     1.0GB     just now
```

---

## Step 3: Once Models Are Downloaded

Run this to launch everything:
```cmd
start-everything.bat
```

Or manually in 2 terminals:

**Terminal 1 (Backend):**
```cmd
activate.bat
python backend/main.py
```

**Terminal 2 (Frontend):**
```cmd
cd frontend
pnpm run dev
```

Then open: **http://localhost:5173**

---

## ⏱️ Estimated Time

- **Model 1 (llama3.1:8b):** 5-15 min
- **Model 2 (qwen2.5-vl:7b):** 5-15 min
- **Model 3 (deepseek-r1:1.5b):** 2-5 min
- **Total:** ~15-35 minutes

---

## 🚀 Command Quick Reference

```cmd
# Check Ollama status
curl http://localhost:11434/api/tags

# List downloaded models
ollama list

# Download models (run these one at a time)
ollama pull llama3.1:8b
ollama pull qwen2.5-vl:7b
ollama pull deepseek-r1:1.5b

# Start everything
start-everything.bat

# Or start manually
activate.bat && python backend/main.py
cd frontend && pnpm run dev
```

---

## ⚠️ If Download Fails

### Common Issues:

**Issue:** "ollama command not found"
- **Fix:** Restart Command Prompt or computer
- Ollama should be in PATH after installation

**Issue:** "Connection refused"
- **Fix:** Ollama service stopped
- Restart Ollama from Windows Start Menu

**Issue:** "Slow download"
- **Normal:** First model takes longer (network speed dependent)
- Subsequent models should be faster

---

## ✅ Ready When You Are!

1. Open **Command Prompt**
2. Run: `ollama pull llama3.1:8b`
3. Wait for completion
4. Run: `ollama pull qwen2.5-vl:7b`
5. Wait for completion
6. Run: `ollama pull deepseek-r1:1.5b` (optional)
7. Run: `start-everything.bat`
8. Open: http://localhost:5173

**Estimated total time: 15-35 minutes** ⏳
