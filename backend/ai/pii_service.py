"""PII masking service using Microsoft Presidio - GDPR compliant"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PIIService:
    """GDPR-compliant PII detection and masking using Microsoft Presidio"""

    # Default PII entities to detect (GDPR-relevant)
    DEFAULT_ENTITIES = [
        "PERSON",           # Names
        "EMAIL_ADDRESS",    # Email addresses
        "PHONE_NUMBER",     # Phone numbers
        "CREDIT_CARD",      # Credit card numbers
        "IBAN_CODE",        # Bank account numbers
        "IP_ADDRESS",       # IP addresses
        "LOCATION",         # Physical addresses
        "DATE_TIME",        # Dates (can be PII in context)
        "NRP",              # National registration numbers
        "US_SSN",           # Social Security Numbers
        "UK_NHS",           # NHS numbers
    ]

    def __init__(self):
        """Initialize Presidio analyzer and anonymizer"""
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine

            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            logger.info("PII Service initialized successfully with Presidio")
        except ImportError as e:
            logger.warning(f"Presidio not installed: {e}. PII features disabled.")
            self.analyzer = None
            self.anonymizer = None

    def is_available(self) -> bool:
        """Check if PII service is available"""
        return self.analyzer is not None and self.anonymizer is not None

    def detect_pii(
        self,
        text: str,
        entities: Optional[List[str]] = None,
        language: str = "en",
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Detect PII entities in text

        Args:
            text: Input text to analyze
            entities: List of entity types to detect (None = all)
            language: Language code (default: en)
            score_threshold: Minimum confidence score (0.0-1.0)

        Returns:
            List of detected PII entities with metadata
        """
        if not self.is_available():
            return []

        try:
            entities_to_detect = entities or self.DEFAULT_ENTITIES

            # Analyze text
            results = self.analyzer.analyze(
                text=text,
                entities=entities_to_detect,
                language=language,
                score_threshold=score_threshold
            )

            # Convert to dict format
            detections = []
            for result in results:
                detections.append({
                    "entity_type": result.entity_type,
                    "start": result.start,
                    "end": result.end,
                    "score": result.score,
                    "text": text[result.start:result.end]
                })

            logger.info(f"Detected {len(detections)} PII entities")
            return detections

        except Exception as e:
            logger.error(f"PII detection failed: {e}")
            return []

    def mask_pii(
        self,
        text: str,
        entities: Optional[List[str]] = None,
        mask_char: str = "*",
        operation: str = "replace"
    ) -> Dict[str, Any]:
        """
        Mask PII in text with various anonymization strategies

        Args:
            text: Input text with PII
            entities: Entity types to mask (None = all)
            mask_char: Character for masking (default: *)
            operation: Anonymization operation:
                - "replace": Replace with mask_char (default)
                - "redact": Remove completely
                - "hash": Replace with hash
                - "mask": Partial masking

        Returns:
            {
                "masked_text": str,
                "entities_found": int,
                "entities": List[dict],
                "original_length": int,
                "masked_length": int
            }
        """
        if not self.is_available():
            return {
                "masked_text": text,
                "entities_found": 0,
                "entities": [],
                "error": "PII service not available"
            }

        try:
            # Detect PII first
            analyzer_results = self.analyzer.analyze(
                text=text,
                entities=entities or self.DEFAULT_ENTITIES,
                language="en"
            )

            if not analyzer_results:
                return {
                    "masked_text": text,
                    "entities_found": 0,
                    "entities": [],
                    "original_length": len(text),
                    "masked_length": len(text),
                    "operation": operation
                }

            # Configure anonymization operator
            from presidio_anonymizer.entities import OperatorConfig

            operators = {}
            for result in analyzer_results:
                if operation == "replace":
                    operators[result.entity_type] = OperatorConfig(
                        "replace",
                        {"new_value": mask_char * (result.end - result.start)}
                    )
                elif operation == "redact":
                    operators[result.entity_type] = OperatorConfig("redact", {})
                elif operation == "hash":
                    operators[result.entity_type] = OperatorConfig("hash", {})
                elif operation == "mask":
                    operators[result.entity_type] = OperatorConfig(
                        "mask",
                        {
                            "masking_char": mask_char,
                            "chars_to_mask": result.end - result.start,
                            "from_end": False
                        }
                    )

            # Anonymize
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators=operators
            )

            # Extract entity details
            entities_list = [
                {
                    "entity_type": r.entity_type,
                    "start": r.start,
                    "end": r.end,
                    "score": r.score
                }
                for r in analyzer_results
            ]

            logger.info(f"Masked {len(analyzer_results)} PII entities using '{operation}' operation")

            return {
                "masked_text": anonymized_result.text,
                "entities_found": len(analyzer_results),
                "entities": entities_list,
                "original_length": len(text),
                "masked_length": len(anonymized_result.text),
                "operation": operation
            }

        except Exception as e:
            logger.error(f"PII masking failed: {e}")
            return {
                "masked_text": text,
                "entities_found": 0,
                "entities": [],
                "error": str(e)
            }
