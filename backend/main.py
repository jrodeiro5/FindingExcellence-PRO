"""FastAPI backend for FindingExcellence_PRO"""
import logging
import os
from pathlib import Path
from typing import List, Optional

from ai.ai_services import AISearchService
from ai.data_analyzer import get_data_summary
from core.content_search import ContentSearch
from core.csv_handler import CSVHandler
from core.excel_handler import ExcelHandler
from core.file_search import FileSearch
from core.pdf_processor import PDFProcessor
from core.text_handler import TextHandler
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.logging_setup import setup_logging

load_dotenv()
logger = setup_logging()

app = FastAPI(
    title="FindingExcellence_PRO API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

file_search = FileSearch()
content_search = ContentSearch()

# Initialize Ollama-based AI service (100% local, no external API calls)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ai_service = None
try:
    ai_service = AISearchService(ollama_host=OLLAMA_HOST)
    logger.info(f"AI service initialized with Ollama at {OLLAMA_HOST}")
except ConnectionError as e:
    logger.warning(f"Ollama not available: {e}. Running without AI features.")
except Exception as e:
    logger.warning(f"AI init failed: {e}")

class FileSearchRequest(BaseModel):
    keywords: List[str]
    exclude_keywords: Optional[List[str]] = []
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    file_types: List[str] = ['.xlsx', '.xls', '.xlsm', '.pdf']
    folders: List[str]

class ContentSearchRequest(BaseModel):
    file_paths: List[str]
    keywords: List[str]
    case_sensitive: bool = False
    search_type: str = "excel"

class NaturalLanguageSearchRequest(BaseModel):
    query: str
    folders: List[str]

class AIAnalysisRequest(BaseModel):
    content: str
    analysis_type: str = "summary"

class OCRRequest(BaseModel):
    image_url: str
    extract_tables: bool = False

@app.get("/")
async def root():
    return {"app": "FindingExcellence_PRO", "version": "2.0.0", "ai_enabled": ai_service is not None}

@app.post("/api/search/filename")
async def search_by_filename(request: FileSearchRequest):
    try:
        excel_extensions = tuple(ext for ext in request.file_types if ext in ['.xlsx', '.xls', '.xlsm'])
        results = file_search.search_by_filename(
            folder_paths=request.folders,
            filename_keywords=request.keywords,
            exclude_keywords=request.exclude_keywords,
            start_date=request.start_date,
            end_date=request.end_date,
            supported_extensions=excel_extensions if excel_extensions else ('.xlsx',)
        )
        return {"success": True, "count": len(results), "results": [{"filename": r[0], "path": r[1], "modified": r[2], "type": r[1].split('.')[-1]} for r in results]}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/natural-language")
async def natural_language_search(request: NaturalLanguageSearchRequest):
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")
    try:
        nl_result = ai_service.natural_language_search(request.query)
        if not nl_result["success"]:
            raise HTTPException(status_code=500, detail=nl_result.get("error"))
        search_params = nl_result["search_params"]
        results = file_search.search_by_filename(
            folder_paths=request.folders,
            filename_keywords=search_params.get("keywords", []),
            exclude_keywords=search_params.get("exclude_keywords", []),
            start_date=search_params.get("start_date"),
            end_date=search_params.get("end_date")
        )
        return {"success": True, "query": request.query, "parsed_params": search_params, "count": len(results), "results": [{"filename": r[0], "path": r[1], "modified": r[2]} for r in results], "ai_cost": nl_result.get("cost", 0)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/content")
async def search_content(request: ContentSearchRequest):
    try:
        if request.search_type == "pdf":
            all_results = {}
            for file_path in request.file_paths:
                results = PDFProcessor.search_content(file_path, request.keywords, request.case_sensitive)
                if results:
                    all_results[file_path] = results
        else:
            all_results = content_search.search_files_contents(
                files_to_search=request.file_paths,
                keywords=request.keywords,
                case_sensitive=request.case_sensitive
            )
        return {"success": True, "file_count": len(request.file_paths), "files_with_matches": len(all_results), "results": all_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...), analysis_type: str = "summary"):
    """
    Upload and analyze a document file (PDF, CSV, XLSX, TXT).
    Extracts text and returns AI analysis.
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")

    try:
        # Save uploaded file temporarily
        temp_path = Path(f"temp_uploads/{file.filename}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        contents = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(contents)

        logger.info(f"Processing file: {file.filename} ({file.content_type})")

        # Extract text based on file type
        extracted_text = ""
        file_ext = Path(file.filename).suffix.lower()

        try:
            if file_ext == '.pdf':
                logger.debug(f"Extracting text from PDF: {file.filename}")
                extracted_text = PDFProcessor.extract_text(str(temp_path))
            elif file_ext in ['.xlsx', '.xls', '.xlsm']:
                logger.debug(f"Extracting text from Excel: {file.filename}")
                extracted_text, error = ExcelHandler.read_excel(str(temp_path))
                if error:
                    logger.error(f"Excel extraction error: {error}")
                    raise HTTPException(status_code=400, detail=f"Excel error: {error}")
            elif file_ext == '.csv':
                logger.debug(f"Extracting text from CSV: {file.filename}")
                extracted_text, error = CSVHandler.read_csv(str(temp_path))
                if error:
                    logger.error(f"CSV extraction error: {error}")
                    raise HTTPException(status_code=400, detail=f"CSV error: {error}")
            elif file_ext in ['.txt']:
                logger.debug(f"Extracting text from TXT: {file.filename}")
                extracted_text, error = TextHandler.read_text(str(temp_path))
                if error:
                    logger.error(f"Text extraction error: {error}")
                    raise HTTPException(status_code=400, detail=f"Text error: {error}")
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")

            if not extracted_text:
                logger.warning(f"No text extracted from: {file.filename}")
                raise HTTPException(status_code=400, detail=f"Could not extract text from {file.filename}")

            logger.info(f"Extracted {len(extracted_text)} characters from {file.filename}")

            # For tabular data (CSV/Excel), use hybrid approach:
            # 1. Extract statistics with polars/pandas (fast, accurate)
            # 2. Send condensed summary to LLM for interpretation
            if file_ext in ['.csv', '.xlsx', '.xls', '.xlsm']:
                logger.info(f"Using hybrid analysis for tabular data: {file.filename}")
                data_summary, data_metadata = get_data_summary(str(temp_path), file_ext)

                # Create prompt with structured data summary
                analysis_prompt = f"""Analyze this dataset and provide insights:

{data_summary}

Provide:
1. Key findings and patterns
2. Data quality observations
3. Actionable recommendations"""

                logger.debug(f"Sending {len(data_summary)} char data summary to LLM")
                result = ai_service.analyze_document(analysis_prompt, analysis_type)

                logger.info(f"Hybrid analysis complete for {file.filename}")
                return {
                    "success": True,
                    "filename": file.filename,
                    "file_type": file_ext,
                    "extracted_chars": len(extracted_text),
                    "data_stats": data_metadata,
                    "analysis": result
                }

            # For text-based files (PDF, TXT), send directly to LLM
            logger.debug(f"Analyzing text with AI (type: {analysis_type})")
            result = ai_service.analyze_document(extracted_text, analysis_type)

            logger.info(f"Analysis complete for {file.filename}")
            return {
                "success": True,
                "filename": file.filename,
                "file_type": file_ext,
                "extracted_chars": len(extracted_text),
                "analysis": result
            }

        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
                logger.debug(f"Cleaned up temp file: {temp_path}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/ocr")
async def ocr_image(request: OCRRequest):
    """Extract text from images using vision models (Qwen2.5-VL)"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")
    try:
        result = ai_service.ocr_from_image(request.image_url, request.extract_tables)
        return result
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/usage/stats")
async def get_usage_stats():
    if not ai_service:
        return {"ai_enabled": False}
    return {"ai_enabled": True, **ai_service.get_usage_stats()}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
