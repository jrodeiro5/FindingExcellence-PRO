"""FastAPI backend for FindingExcellence_PRO"""
import logging
import os
from pathlib import Path
from typing import List, Optional

from ai.ai_services import AISearchService
from ai.batch_analyzer import BatchAnalyzer
from ai.data_analyzer import get_data_summary
from core.content_search import ContentSearch
from core.csv_handler import CSVHandler
from core.excel_handler import ExcelHandler
from core.file_search import FileSearch
from core.json_handler import JSONHandler
from core.markdown_handler import MarkdownHandler
from core.pdf_processor import PDFProcessor
from core.powerpoint_handler import PowerPointHandler
from core.search_history import SearchHistory
from core.text_handler import TextHandler
from core.word_handler import WordHandler
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
search_history = SearchHistory()

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

@app.post("/api/search/history")
async def add_to_search_history(request: FileSearchRequest):
    """Add a search to the history after it's completed."""
    try:
        search_history.add_search(
            keywords=request.keywords,
            folders=request.folders,
            exclude_keywords=request.exclude_keywords,
            start_date=request.start_date,
            end_date=request.end_date,
            case_sensitive=request.case_sensitive,
            extensions=request.supported_extensions
        )
        return {"success": True, "message": "Search added to history"}
    except Exception as e:
        logger.error(f"Error adding to search history: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/search/history")
async def get_search_history(limit: int = 20):
    """Get recent search history."""
    try:
        history = search_history.get_history(limit=limit)
        return {"success": True, "history": history}
    except Exception as e:
        logger.error(f"Error retrieving search history: {e}")
        return {"success": False, "error": str(e), "history": []}

@app.post("/api/search/history/{search_id}")
async def rerun_search(search_id: int):
    """Get a specific search from history for re-running."""
    try:
        search = search_history.get_search_by_id(search_id)
        if search:
            return {"success": True, "search": search}
        else:
            return {"success": False, "error": "Search not found"}
    except Exception as e:
        logger.error(f"Error retrieving search: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/api/search/history/{search_id}")
async def delete_search_history(search_id: int):
    """Delete a search from history."""
    try:
        success = search_history.delete_search(search_id)
        return {"success": success, "message": "Search deleted" if success else "Failed to delete"}
    except Exception as e:
        logger.error(f"Error deleting search: {e}")
        return {"success": False, "error": str(e)}

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
                extracted_text, error = PDFProcessor.extract_text(str(temp_path))
                if error:
                    logger.error(f"PDF extraction error: {error}")
                    raise HTTPException(status_code=400, detail=f"PDF error: {error}")
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
            elif file_ext == '.docx':
                logger.debug(f"Extracting text from Word: {file.filename}")
                extracted_text, error = WordHandler.read_word(str(temp_path))
                if error:
                    logger.error(f"Word extraction error: {error}")
                    raise HTTPException(status_code=400, detail=f"Word error: {error}")
            elif file_ext == '.pptx':
                logger.debug(f"Extracting text from PowerPoint: {file.filename}")
                extracted_text, error = PowerPointHandler.read_powerpoint(str(temp_path))
                if error:
                    logger.error(f"PowerPoint extraction error: {error}")
                    raise HTTPException(status_code=400, detail=f"PowerPoint error: {error}")
            elif file_ext == '.json':
                logger.debug(f"Extracting text from JSON: {file.filename}")
                extracted_text, error = JSONHandler.read_json(str(temp_path))
                if error:
                    logger.error(f"JSON extraction error: {error}")
                    raise HTTPException(status_code=400, detail=f"JSON error: {error}")
            elif file_ext in ['.md', '.markdown', '.mdown', '.mkd', '.mkdn']:
                logger.debug(f"Extracting text from Markdown: {file.filename}")
                extracted_text, error = MarkdownHandler.read_markdown(str(temp_path))
                if error:
                    logger.error(f"Markdown extraction error: {error}")
                    raise HTTPException(status_code=400, detail=f"Markdown error: {error}")
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}. Supported: PDF, XLSX, CSV, TXT, DOCX, PPTX, JSON, MD")

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

@app.post("/api/analyze/batch")
async def analyze_batch(files: List[UploadFile] = File(...), analysis_type: str = "summary"):
    """
    Analyze multiple documents in batch and provide consolidated insights.
    Supports 2-100 files per batch.
    """
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")

    if not files or len(files) < 2:
        raise HTTPException(status_code=400, detail="Batch analysis requires at least 2 files")

    if len(files) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 files per batch")

    try:
        batch_analyses = []
        successful_files = 0
        failed_files = 0
        temp_paths = []

        logger.info(f"Starting batch analysis for {len(files)} files with type: {analysis_type}")

        for idx, file in enumerate(files, 1):
            try:
                # Save uploaded file temporarily
                temp_path = Path(f"temp_uploads/{file.filename}")
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                temp_paths.append(temp_path)

                contents = await file.read()
                with open(temp_path, 'wb') as f:
                    f.write(contents)

                logger.debug(f"[{idx}/{len(files)}] Processing file: {file.filename}")

                # Extract text based on file type
                extracted_text = ""
                file_ext = Path(file.filename).suffix.lower()

                # Use same extraction logic as single file endpoint
                if file_ext == '.pdf':
                    extracted_text, error = PDFProcessor.extract_text(str(temp_path))
                    if error:
                        raise Exception(f"PDF error: {error}")
                elif file_ext in ['.xlsx', '.xls', '.xlsm']:
                    extracted_text, error = ExcelHandler.read_excel(str(temp_path))
                    if error:
                        raise Exception(f"Excel error: {error}")
                elif file_ext == '.csv':
                    extracted_text, error = CSVHandler.read_csv(str(temp_path))
                    if error:
                        raise Exception(f"CSV error: {error}")
                elif file_ext in ['.txt']:
                    extracted_text, error = TextHandler.read_text(str(temp_path))
                    if error:
                        raise Exception(f"Text error: {error}")
                elif file_ext == '.docx':
                    extracted_text, error = WordHandler.read_word(str(temp_path))
                    if error:
                        raise Exception(f"Word error: {error}")
                elif file_ext == '.pptx':
                    extracted_text, error = PowerPointHandler.read_powerpoint(str(temp_path))
                    if error:
                        raise Exception(f"PowerPoint error: {error}")
                elif file_ext == '.json':
                    extracted_text, error = JSONHandler.read_json(str(temp_path))
                    if error:
                        raise Exception(f"JSON error: {error}")
                elif file_ext in ['.md', '.markdown', '.mdown', '.mkd', '.mkdn']:
                    extracted_text, error = MarkdownHandler.read_markdown(str(temp_path))
                    if error:
                        raise Exception(f"Markdown error: {error}")
                else:
                    raise Exception(f"Unsupported file type: {file_ext}")

                if not extracted_text:
                    raise Exception(f"Could not extract text from {file.filename}")

                # Perform analysis
                logger.debug(f"Analyzing {file.filename} with type: {analysis_type}")
                result = ai_service.analyze_document(extracted_text, analysis_type)

                batch_analyses.append({
                    "filename": file.filename,
                    "file_type": file_ext,
                    "extracted_chars": len(extracted_text),
                    "analysis": result
                })

                successful_files += 1
                logger.debug(f"[{idx}/{len(files)}] Analysis complete: {file.filename}")

            except Exception as e:
                failed_files += 1
                logger.warning(f"[{idx}/{len(files)}] Failed to analyze {file.filename}: {str(e)}")
                batch_analyses.append({
                    "filename": file.filename,
                    "error": str(e),
                    "analysis": None
                })

        # Generate consolidated summary
        summary = BatchAnalyzer.prepare_batch_summary(batch_analyses, analysis_type)

        logger.info(f"Batch analysis complete: {successful_files}/{len(files)} successful")

        return {
            "success": True,
            "file_count": len(files),
            "successful": successful_files,
            "failed": failed_files,
            "analysis_type": analysis_type,
            "individual_analyses": batch_analyses,
            "summary": summary
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

    finally:
        # Clean up temp files
        for temp_path in temp_paths:
            try:
                if temp_path.exists():
                    temp_path.unlink()
                    logger.debug(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                logger.warning(f"Could not clean up {temp_path}: {e}")

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
