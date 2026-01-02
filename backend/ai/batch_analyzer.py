"""Batch document analysis for analyzing multiple files at once."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BatchAnalyzer:
    """Analyzer for processing multiple documents in batch."""

    @staticmethod
    def prepare_batch_summary(analyses: List[Dict], analysis_type: str) -> str:
        """
        Create a summary across all analyzed documents.

        Args:
            analyses: List of analysis results with file metadata
            analysis_type: Type of analysis that was performed

        Returns:
            Consolidated summary across all files
        """
        if not analyses:
            return "No files analyzed"

        file_count = len(analyses)
        filenames = [a.get("filename", "Unknown") for a in analyses]

        # Build cross-document insights based on analysis type
        if analysis_type == "summary":
            return BatchAnalyzer._summarize_documents(analyses, file_count, filenames)
        elif analysis_type == "key_points":
            return BatchAnalyzer._consolidate_key_points(analyses, file_count, filenames)
        elif analysis_type == "anomalies":
            return BatchAnalyzer._consolidate_anomalies(analyses, file_count, filenames)
        elif analysis_type == "insights":
            return BatchAnalyzer._consolidate_insights(analyses, file_count, filenames)
        elif analysis_type == "trends":
            return BatchAnalyzer._consolidate_trends(analyses, file_count, filenames)
        elif analysis_type == "comparative":
            return BatchAnalyzer._comparative_analysis(analyses, file_count, filenames)
        else:
            return f"Analysis completed for {file_count} files"

    @staticmethod
    def _summarize_documents(analyses: List[Dict], file_count: int, filenames: List[str]) -> str:
        """Generate summary of summaries."""
        summary = f"## Summary of {file_count} Documents\n\n"
        summary += f"**Files analyzed:** {', '.join(filenames)}\n\n"

        for i, analysis in enumerate(analyses, 1):
            summary += f"### {i}. {analysis.get('filename', 'Unknown')}\n"
            summary += f"{analysis.get('analysis', 'No summary available')}\n\n"

        return summary

    @staticmethod
    def _consolidate_key_points(analyses: List[Dict], file_count: int, filenames: List[str]) -> str:
        """Consolidate key points across documents."""
        consolidated = f"## Key Points from {file_count} Documents\n\n"

        for i, analysis in enumerate(analyses, 1):
            consolidated += f"### {analysis.get('filename', 'Unknown')}\n"
            consolidated += f"{analysis.get('analysis', 'No key points identified')}\n\n"

        return consolidated

    @staticmethod
    def _consolidate_anomalies(analyses: List[Dict], file_count: int, filenames: List[str]) -> str:
        """Consolidate anomalies found across documents."""
        consolidated = f"## Anomalies in {file_count} Documents\n\n"

        anomaly_count = 0
        for analysis in analyses:
            if "anomaly" in analysis.get('analysis', '').lower() or "unusual" in analysis.get('analysis', '').lower():
                anomaly_count += 1
                consolidated += f"### {analysis.get('filename', 'Unknown')}\n"
                consolidated += f"{analysis.get('analysis', 'No anomalies detected')}\n\n"

        if anomaly_count == 0:
            consolidated += "No significant anomalies detected across analyzed documents.\n"

        return consolidated

    @staticmethod
    def _consolidate_insights(analyses: List[Dict], file_count: int, filenames: List[str]) -> str:
        """Consolidate business insights from documents."""
        consolidated = f"## Business Insights from {file_count} Documents\n\n"

        for i, analysis in enumerate(analyses, 1):
            consolidated += f"### {analysis.get('filename', 'Unknown')}\n"
            consolidated += f"{analysis.get('analysis', 'No insights identified')}\n\n"

        return consolidated

    @staticmethod
    def _consolidate_trends(analyses: List[Dict], file_count: int, filenames: List[str]) -> str:
        """Consolidate trends across documents."""
        consolidated = f"## Trends Identified in {file_count} Documents\n\n"

        for i, analysis in enumerate(analyses, 1):
            consolidated += f"### {analysis.get('filename', 'Unknown')}\n"
            consolidated += f"{analysis.get('analysis', 'No trends identified')}\n\n"

        return consolidated

    @staticmethod
    def _comparative_analysis(analyses: List[Dict], file_count: int, filenames: List[str]) -> str:
        """Perform comparative analysis across documents."""
        comparative = f"## Comparative Analysis of {file_count} Documents\n\n"
        comparative += f"**Files compared:** {', '.join(filenames)}\n\n"

        comparative += "### Individual Analyses\n"
        for analysis in analyses:
            comparative += f"#### {analysis.get('filename', 'Unknown')}\n"
            comparative += f"{analysis.get('analysis', 'No analysis available')}\n\n"

        comparative += "### Common Themes\n"
        comparative += "Cross-document analysis complete. Review individual sections above for themes and patterns.\n"

        return comparative

    @staticmethod
    def format_batch_result(analyses: List[Dict], summary: str) -> Dict:
        """
        Format batch analysis results for display.

        Args:
            analyses: List of individual file analyses
            summary: Consolidated summary

        Returns:
            Formatted result with all analyses and summary
        """
        return {
            "file_count": len(analyses),
            "files_analyzed": [a.get("filename") for a in analyses],
            "individual_analyses": analyses,
            "summary": summary,
            "status": "completed"
        }
