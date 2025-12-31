"""Named Entity Recognition using GliNER - flexible, lightweight NER"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NERService:
    """Lightweight NER service using GliNER for custom entity extraction"""

    # Default model (small, fast, CPU-friendly)
    DEFAULT_MODEL = "urchade/gliner_small-v2.1"

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize GliNER model

        Args:
            model_name: HuggingFace model name (default: gliner_small-v2.1)
        """
        try:
            from gliner import GLiNER

            self.model_name = model_name or self.DEFAULT_MODEL
            logger.info(f"Loading GliNER model: {self.model_name}")

            self.model = GLiNER.from_pretrained(self.model_name)

            logger.info(f"GliNER model loaded successfully: {self.model_name}")
        except ImportError:
            logger.warning("GliNER not installed. NER features disabled.")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load GliNER model: {e}")
            self.model = None

    def is_available(self) -> bool:
        """Check if NER service is available"""
        return self.model is not None

    def extract_entities(
        self,
        text: str,
        entity_types: List[str],
        threshold: float = 0.5,
        flat_ner: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract custom entities from text

        Args:
            text: Input text
            entity_types: List of entity types to extract (e.g., ["person", "organization", "product"])
            threshold: Confidence threshold (0.0-1.0)
            flat_ner: If True, remove nested entities

        Returns:
            List of entities with metadata:
            [
                {
                    "text": "entity text",
                    "label": "entity_type",
                    "score": 0.95,
                    "start": 10,
                    "end": 20
                }
            ]
        """
        if not self.is_available():
            return []

        try:
            # Predict entities
            entities = self.model.predict_entities(
                text,
                entity_types,
                threshold=threshold,
                flat_ner=flat_ner
            )

            # Format results
            results = []
            for entity in entities:
                results.append({
                    "text": entity["text"],
                    "label": entity["label"],
                    "score": float(entity["score"]),
                    "start": entity["start"],
                    "end": entity["end"]
                })

            logger.info(f"Extracted {len(results)} entities of types: {entity_types}")
            return results

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

    def extract_domain_entities(
        self,
        text: str,
        domain: str = "business",
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Extract entities for common domains with predefined entity types

        Args:
            text: Input text
            domain: Domain type (business, financial, medical, legal)
            threshold: Confidence threshold

        Returns:
            List of extracted entities
        """
        if not self.is_available():
            return []

        # Predefined entity types for common domains
        domain_entities = {
            "business": [
                "company", "organization", "product", "service",
                "person", "location", "revenue", "metric", "date"
            ],
            "financial": [
                "company", "stock_symbol", "currency", "amount",
                "financial_metric", "date", "percentage", "person"
            ],
            "medical": [
                "disease", "symptom", "medication", "treatment",
                "patient", "doctor", "hospital", "date"
            ],
            "legal": [
                "person", "organization", "law", "regulation",
                "case_number", "court", "date", "location"
            ],
            "general": [
                "person", "organization", "location", "date",
                "product", "event", "money"
            ]
        }

        entity_types = domain_entities.get(domain, domain_entities["general"])

        return self.extract_entities(text, entity_types, threshold)
