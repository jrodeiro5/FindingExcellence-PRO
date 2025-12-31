"""Semantic chunking using Chonkie for intelligent document splitting"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ChunkingService:
    """Document chunking service for large file processing"""

    # Threshold for when to use semantic chunking
    LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10MB

    def __init__(self):
        """Initialize chunkers"""
        try:
            from chonkie import SemanticChunker, SentenceChunker, TokenChunker

            # Initialize different chunking strategies
            self.semantic_chunker = SemanticChunker(
                chunk_size=512,
                chunk_overlap=50
            )
            self.token_chunker = TokenChunker(
                chunk_size=512,
                chunk_overlap=50
            )
            self.sentence_chunker = SentenceChunker(
                chunk_size=5  # sentences per chunk
            )

            logger.info("Chunking service initialized with Chonkie")
            self.available = True
        except ImportError:
            logger.warning("Chonkie not installed. Chunking features disabled.")
            self.semantic_chunker = None
            self.token_chunker = None
            self.sentence_chunker = None
            self.available = False
        except Exception as e:
            logger.error(f"Failed to initialize chunking service: {e}")
            self.available = False

    def is_available(self) -> bool:
        """Check if chunking service is available"""
        return self.available

    def chunk_text(
        self,
        text: str,
        strategy: str = "semantic",
        chunk_size: int = 512,
        overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Chunk text using specified strategy

        Args:
            text: Input text to chunk
            strategy: Chunking strategy (semantic, token, sentence)
            chunk_size: Maximum chunk size
            overlap: Overlap between chunks

        Returns:
            List of chunks with metadata:
            [
                {
                    "text": "chunk text",
                    "start": 0,
                    "end": 512,
                    "index": 0,
                    "size": 512
                }
            ]
        """
        if not self.is_available():
            # Fallback: return whole text as single chunk
            return [{
                "text": text,
                "start": 0,
                "end": len(text),
                "index": 0,
                "size": len(text)
            }]

        try:
            if strategy == "semantic":
                chunks = self.semantic_chunker.chunk(text)
            elif strategy == "token":
                chunks = self.token_chunker.chunk(text)
            elif strategy == "sentence":
                chunks = self.sentence_chunker.chunk(text)
            else:
                raise ValueError(f"Unknown chunking strategy: {strategy}")

            # Format results
            results = []
            for idx, chunk in enumerate(chunks):
                results.append({
                    "text": chunk.text,
                    "start": chunk.start_index,
                    "end": chunk.end_index,
                    "index": idx,
                    "size": len(chunk.text)
                })

            logger.info(f"Created {len(results)} chunks using {strategy} strategy")
            return results

        except Exception as e:
            logger.error(f"Chunking failed: {e}")
            # Fallback: return whole text as single chunk
            return [{
                "text": text,
                "start": 0,
                "end": len(text),
                "index": 0,
                "size": len(text),
                "error": str(e)
            }]

    def should_chunk(self, file_size: int) -> bool:
        """Determine if file should be chunked based on size"""
        return self.is_available() and file_size > self.LARGE_FILE_THRESHOLD
