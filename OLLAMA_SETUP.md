# Ollama Setup Guide for FindingExcellence PRO

## ✅ Ollama Installed & Running

Your Ollama service is already running at `http://localhost:11434`. Great!

## 📥 Step 1: Pull Required Models

Run this in **Windows Command Prompt** (NOT PowerShell):

```cmd
cd C:\Users\[YourUsername]\Desktop\FindingExcellence_PRO
pull-models.bat
```

This will download:
- **llama3.1:8b** (~4.7 GB) - Primary text/search model
- **qwen2.5-vl:7b** (~4.4 GB) - Vision/OCR model (state-of-the-art)
- **deepseek-r1:1.5b** (~1 GB) - Fast fallback model

**Total: ~10 GB**

### Or Pull Manually:
If you prefer to pull models manually, run these one at a time:

```cmd
ollama pull llama3.1:8b
ollama pull qwen2.5-vl:7b
ollama pull deepseek-r1:1.5b
```

## 📝 Step 2: Create .env File

Create a file named `.env` in the project root with:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=qwen2.5-vl:7b
OLLAMA_TEMPERATURE=0.3
OLLAMA_MAX_TOKENS=2000

APP_NAME=FindingExcellence_PRO
APP_VERSION=2.0.0

DEFAULT_SEARCH_FOLDERS=C:\Users\[YourUsername]\Desktop,C:\Users\[YourUsername]\Downloads
MAX_WORKERS=4
LOG_LEVEL=INFO
LOG_FILE=finding_excellence.log
```

Replace `[YourUsername]` with your Windows username.

## 🐍 Step 3: Install Python Dependencies

```cmd
activate.bat
pip install -r backend/requirements.txt
```

## 🚀 Step 4: Start the Backend

```cmd
python backend/main.py
```

You should see:
```
AI service initialized with Ollama at http://localhost:11434
Uvicorn running on http://127.0.0.1:8000
```

## 🎨 Step 5: Start the Frontend (New Terminal)

```cmd
cd frontend
pnpm install
pnpm run dev
```

Frontend will be available at http://localhost:5173

## ✨ Step 6: Test Features

### Natural Language Search
1. Go to "File Search" tab
2. Toggle "AI Search" mode
3. Try: "Find all PDF files from last month"
4. Watch as Ollama parses your query and searches!

### Document Analysis
1. Go to "AI Analysis" tab
2. Paste document content
3. Select analysis type: Summary, Trends, Anomalies, or Insights
4. Click "Analyze Document"

### OCR (Text from Images)
1. Go to "AI Analysis" tab (OCR button coming soon in UI)
2. Provide image URL or file path
3. Extract text with Qwen2.5-VL

## 📊 Performance Expectations

### Hardware Dependent:

**CPU-Only (Intel i7/Ryzen 7):**
- Text inference: 10-20 tokens/sec
- Natural language search: 5-10 seconds
- Document analysis: 10-20 seconds
- OCR: 15-30 seconds per image

**With GPU (NVIDIA RTX 3060+):**
- Text inference: 40-70 tokens/sec
- Natural language search: 1-2 seconds
- Document analysis: 2-5 seconds
- OCR: 5-10 seconds per image

**Optional GPU Acceleration:**
Set in `.env`:
```env
OLLAMA_GPU_LAYERS=-1   # Use all GPU layers (requires NVIDIA GPU)
```

## 🔧 Troubleshooting

### Ollama Not Responding
```cmd
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If error: Start Ollama from Windows Start Menu
# Look for "Ollama" or restart Windows
```

### Models Not Found
```cmd
# List downloaded models
ollama list

# Check storage location
# Default: C:\Users\[USERNAME]\.ollama\models\
```

### Backend Says "AI service not available"
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check backend logs for connection errors
3. Ensure `OLLAMA_HOST=http://localhost:11434` in `.env`

### Slow Response Times
- CPU-only inference is slow by design (but private!)
- First request may be slower (model loading)
- If unacceptable, consider GPU acceleration or reducing model size

## 📚 Model Details

### llama3.1:8b (Primary Text Model)
- **Size:** 4.7 GB
- **Speed:** 10-20 tok/sec (CPU)
- **Best for:** Natural language understanding, search parsing, document analysis
- **Downloads:** 105+ million (most popular)

### qwen2.5-vl:7b (Vision/OCR Model)
- **Size:** 4.4 GB
- **Speed:** 15-30 sec per image (CPU)
- **Best for:** OCR, image text extraction, document scanning
- **Accuracy:** 75% (beats GPT-4o on OCR benchmarks!)
- **Downloads:** 1+ million

### deepseek-r1:1.5b (Fast Fallback)
- **Size:** 1 GB
- **Speed:** 20-30 tok/sec (CPU)
- **Best for:** Quick fallback if primary model fails
- **Quality:** Good for simple tasks, reasoning-focused

## 🎯 Architecture

```
You (Desktop)
    ↓
FindingExcellence PRO (React + Electron)
    ↓
FastAPI Backend (Python)
    ↓
Ollama Local Service
    ↓
Models (llama3.1:8b, qwen2.5-vl:7b)
    ↓
Results (100% Private - Never leaves your machine)
```

## 🔒 Privacy Guarantee

✅ **No cloud calls**
✅ **No data sent to third parties**
✅ **No API keys required**
✅ **All processing local**
✅ **File content never transmitted**

Your search queries, documents, and images are processed entirely on your machine!

## 📖 More Information

- **Ollama Docs:** https://ollama.com
- **Model Details:** https://ollama.com/search
- **Project CLAUDE.md:** See full development guide
- **Backend API:** http://localhost:8000/docs (Swagger UI when running)

## ✅ Verification Checklist

- [ ] Ollama installed and running
- [ ] Models downloaded (10 GB total)
- [ ] `.env` file created
- [ ] Python dependencies installed
- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Can perform natural language search
- [ ] Can analyze documents
- [ ] Can extract text from images (OCR)

Happy searching! 🚀
