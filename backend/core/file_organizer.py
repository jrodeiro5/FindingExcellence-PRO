"""
File Organization Module using Content-Based Clustering

Organizes files in a folder into thematic groups using TF-IDF + KMeans clustering.
Supports PDF, Excel, Word, text, CSV, and Markdown files.

Can be used standalone via CLI or integrated into desktop UI.
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

# Setup logging
logger = logging.getLogger(__name__)

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.pdf': 'pdf_processor',
    '.xlsx': 'excel_handler',
    '.xls': 'excel_handler',
    '.xlsm': 'excel_handler',
    '.docx': 'word_handler',
    '.txt': 'text',
    '.csv': 'text',
    '.md': 'text',
}

# Extensions without extractable text
UNSUPPORTED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg',
    '.mp3', '.mp4', '.wav', '.mov', '.avi', '.mkv',
    '.zip', '.rar', '.7z', '.tar', '.gz',
    '.exe', '.dll', '.bin', '.iso',
    '.pptx', '.ppt',  # PowerPoint not fully supported yet
}

# Language-specific stopwords (for TF-IDF)
STOPWORDS = {
    'spanish': [
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no',
        'haber', 'por', 'con', 'su', 'para', 'es', 'al', 'lo', 'como', 'más',
        'o', 'pero', 'sus', 'le', 'ya', 'o', 'fue', 'este', 'ha', 'sí',
        'porque', 'esta', 'son', 'entre', 'está', 'cuando', 'muy', 'sin',
        'sobre', 'ser', 'tiene', 'también', 'me', 'hasta', 'hay', 'donde',
        'han', 'quien', 'están', 'estado', 'desde', 'todo', 'durante', 'estados',
        'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'fueron', 'ese', 'eso',
        'había', 'ante', 'ellos', 'tengo', 'esos', 'mí', 'antes', 'algunos',
        'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa',
        'estos', 'mucho', 'quienes', 'sólo', 'solamente', 'ello', 'éstos',
    ],
    'english': [
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'that', 'this', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
        'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
        'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
        'own', 'same', 'so', 'than', 'too', 'very', 'as', 'just', 'if',
    ]
}


class FileTextExtractor:
    """Extract text from various file formats"""

    @staticmethod
    def extract_text(file_path: str) -> Tuple[str, Optional[str]]:
        """
        Extract text from a file.

        Returns:
            (text, error) - text is str (empty if error), error is None on success
        """
        file_ext = Path(file_path).suffix.lower()

        try:
            # PDF files
            if file_ext == '.pdf':
                from backend.core.pdf_processor import PDFProcessor
                text, error = PDFProcessor.extract_text(file_path)
                return (text or "", error)

            # Excel files
            elif file_ext in {'.xlsx', '.xls', '.xlsm'}:
                from backend.core.excel_handler import ExcelHandler
                text, error = ExcelHandler.read_excel(file_path)
                return (text or "", error)

            # Word files
            elif file_ext == '.docx':
                from backend.core.word_handler import WordHandler
                text, error = WordHandler.read_word(file_path)
                return (text or "", error)

            # Plain text files (txt, csv, md)
            elif file_ext in {'.txt', '.csv', '.md'}:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    return (text, None)
                except UnicodeDecodeError:
                    # Try with different encoding
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            text = f.read()
                        return (text, None)
                    except Exception as e:
                        return ("", f"Encoding error: {str(e)}")
                except Exception as e:
                    return ("", str(e))

            else:
                return ("", f"Unsupported file type: {file_ext}")

        except Exception as e:
            logger.warning(f"Error extracting text from {file_path}: {e}")
            return ("", str(e))


class FileOrganizer:
    """Main file organization engine using clustering"""

    def __init__(self, folder: str, num_clusters: int, language: str = 'spanish'):
        """
        Initialize organizer.

        Args:
            folder: Root folder to organize
            num_clusters: Number of thematic clusters
            language: Language for stopwords (spanish/english)
        """
        self.folder = Path(folder).resolve()
        self.num_clusters = max(2, min(num_clusters, 20))  # Clamp between 2 and 20
        self.language = language
        self.extractor = FileTextExtractor()

        # Results storage
        self.files: List[Path] = []
        self.texts: Dict[str, str] = {}
        self.cluster_labels: Optional[np.ndarray] = None
        self.cluster_names: Dict[int, str] = {}
        self.errors: Dict[str, str] = {}

    def discover_files(self) -> int:
        """
        Discover supported files in folder (non-recursive, first level only).

        Returns:
            Number of files found
        """
        if not self.folder.exists():
            raise ValueError(f"Folder does not exist: {self.folder}")

        self.files = []

        for item in self.folder.iterdir():
            if item.is_file():
                ext = item.suffix.lower()

                # Skip if it's unsupported
                if ext in UNSUPPORTED_EXTENSIONS:
                    continue

                # Include only supported extensions
                if ext in SUPPORTED_EXTENSIONS:
                    self.files.append(item)

        logger.info(f"Found {len(self.files)} supported files in {self.folder}")
        return len(self.files)

    def extract_all_texts(self) -> int:
        """
        Extract text from all discovered files.

        Returns:
            Number of files with successfully extracted text
        """
        self.texts = {}
        self.errors = {}
        successful = 0

        for file_path in self.files:
            logger.info(f"Extracting: {file_path.name}")
            text, error = self.extractor.extract_text(str(file_path))

            if error:
                self.errors[file_path.name] = error
                logger.warning(f"  Error: {error}")
            else:
                # Only keep files with meaningful text (>50 chars)
                if text and len(text.strip()) > 50:
                    self.texts[file_path.name] = text
                    successful += 1
                else:
                    self.errors[file_path.name] = "No extractable text"

        logger.info(f"Successfully extracted text from {successful}/{len(self.files)} files")
        return successful

    def cluster_files(self) -> bool:
        """
        Perform TF-IDF vectorization and KMeans clustering.

        Returns:
            True if clustering succeeded
        """
        if len(self.texts) < self.num_clusters:
            logger.warning(
                f"Only {len(self.texts)} files with text, but {self.num_clusters} clusters requested. "
                f"Reducing clusters to {len(self.texts)}"
            )
            actual_clusters = max(1, len(self.texts))
        else:
            actual_clusters = self.num_clusters

        try:
            # Get stopwords for language
            stop_words = STOPWORDS.get(self.language.lower(), None)

            # Adaptive min_df: only filter out unique terms if enough documents
            min_df_threshold = 2 if len(self.texts) > 15 else 1

            # TF-IDF vectorization
            logger.info("Vectorizing text with TF-IDF...")
            vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words=stop_words,
                lowercase=True,
                min_df=min_df_threshold,
                max_df=0.8
            )
            tfidf_matrix = vectorizer.fit_transform(self.texts.values())

            # Dimensionality reduction for stability
            logger.info("Reducing dimensionality with TruncatedSVD...")
            svd = TruncatedSVD(n_components=min(50, tfidf_matrix.shape[1] - 1))
            reduced_matrix = svd.fit_transform(tfidf_matrix)

            # KMeans clustering
            logger.info(f"Clustering into {actual_clusters} groups...")
            kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
            self.cluster_labels = kmeans.fit_predict(reduced_matrix)

            # Generate cluster names from top terms (using direct TF-IDF method)
            self._generate_cluster_names_direct(vectorizer, tfidf_matrix)

            logger.info("Clustering complete")
            return True

        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            return False

    def _generate_cluster_names_direct(self, vectorizer, tfidf_matrix) -> None:
        """
        Generate human-readable names from average TF-IDF scores per cluster.

        CRITICAL FIX: Previous method mapped SVD component indices (0-49) to TF-IDF
        vocabulary (0-499), resulting in random cluster names. This method computes
        actual term importance in original TF-IDF space.
        """
        self.cluster_names = {}
        feature_names = vectorizer.get_feature_names_out()
        stop_words_set = set(STOPWORDS.get(self.language.lower(), []))

        for cluster_id in range(max(self.cluster_labels) + 1):
            # Get indices of files in this cluster
            cluster_mask = self.cluster_labels == cluster_id

            # Average TF-IDF scores across all documents in this cluster
            cluster_docs = tfidf_matrix[cluster_mask]
            avg_tfidf = np.asarray(cluster_docs.mean(axis=0)).flatten()

            # Get top 5 terms by average TF-IDF importance
            top_indices = avg_tfidf.argsort()[-5:][::-1]
            top_terms = [feature_names[i] for i in top_indices]

            # Filter: remove stopwords, numeric-only terms, and short terms
            top_terms = [
                t for t in top_terms
                if len(t) > 2 and t not in stop_words_set and not t.isdigit()
            ][:3]
            cluster_name = "_".join(top_terms) if top_terms else f"cluster_{cluster_id}"

            self.cluster_names[cluster_id] = cluster_name

    def get_results(self) -> List[Dict]:
        """
        Get clustering results as list of dicts.

        Returns:
            List of {filename, cluster_id, cluster_name, top_terms}
        """
        results = []

        # Files with errors
        for filename, error in self.errors.items():
            results.append({
                'filename': filename,
                'original_path': str(self.folder / filename),
                'cluster_id': -1,
                'cluster_name': '_sin_clasificar',
                'top_terms': error,
            })

        # Files that were clustered
        for i, filename in enumerate(self.texts.keys()):
            cluster_id = int(self.cluster_labels[i]) if self.cluster_labels is not None else -1
            cluster_name = self.cluster_names.get(cluster_id, 'unknown')

            results.append({
                'filename': filename,
                'original_path': str(self.folder / filename),
                'cluster_id': cluster_id,
                'cluster_name': cluster_name,
                'top_terms': cluster_name,
            })

        return results

    def print_table(self, results: List[Dict]) -> None:
        """Print results as formatted table."""
        print("\n" + "=" * 120)
        print(f"{'ARCHIVO':<40} | {'CLUSTER':<3} | {'CARPETA DESTINO':<40} | {'TÉRMINOS':<20}")
        print("=" * 120)

        for result in results:
            cluster_id = result['cluster_id']
            folder_name = f"{cluster_id + 1:02d}_{result['cluster_name']}"

            print(
                f"{result['filename']:<40} | {cluster_id:<3} | {folder_name:<40} | "
                f"{result['top_terms'][:20]:<20}"
            )

        print("=" * 120 + "\n")

    def export_csv(self, results: List[Dict]) -> str:
        """
        Export results to CSV file.

        Returns:
            Path to CSV file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.folder / f"organizer_output_{timestamp}.csv"

        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['filename', 'original_path', 'cluster_id', 'cluster_name', 'top_terms']
                )
                writer.writeheader()
                writer.writerows(results)

            logger.info(f"Results exported to {csv_path}")
            return str(csv_path)

        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            raise

    def print_summary(self, results: List[Dict]) -> None:
        """Print summary statistics."""
        clusters = {}

        for result in results:
            cluster_id = result['cluster_id']
            cluster_name = result['cluster_name']

            if cluster_id not in clusters:
                clusters[cluster_id] = {'name': cluster_name, 'count': 0}

            clusters[cluster_id]['count'] += 1

        print("\nRESUMEN POR CLUSTER:")
        print("=" * 50)

        total_files = 0
        for cluster_id in sorted(clusters.keys()):
            info = clusters[cluster_id]
            count = info['count']
            name = info['name']
            total_files += count

            if cluster_id == -1:
                print(f"_sin_clasificar:           {count:>3} archivos")
            else:
                folder_name = f"{cluster_id + 1:02d}_{name}"
                print(f"{folder_name:<40} {count:>3} archivos")

        print("=" * 50)
        print(f"TOTAL:                     {total_files:>3} archivos\n")

    def execute_organization(self, results: List[Dict]) -> None:
        """
        Actually move/copy files to their cluster folders.

        Args:
            results: Results from clustering
        """
        import shutil

        organized_folder = self.folder / "_organizado"

        # Create root organized folder
        organized_folder.mkdir(exist_ok=True)
        logger.info(f"Created organization folder: {organized_folder}")

        copy_errors = []

        for result in results:
            filename = result['filename']
            cluster_id = result['cluster_id']
            cluster_name = result['cluster_name']

            # Determine destination folder
            if cluster_id == -1:
                dest_folder = organized_folder / "_sin_clasificar"
            else:
                folder_name = f"{cluster_id + 1:02d}_{cluster_name}"
                dest_folder = organized_folder / folder_name

            # Create destination folder
            dest_folder.mkdir(parents=True, exist_ok=True)

            # Copy file
            src_path = self.folder / filename
            dest_path = dest_folder / filename

            try:
                shutil.copy2(src_path, dest_path)
                logger.info(f"Copied: {filename} → {dest_folder.name}/")
            except Exception as e:
                error_msg = f"Failed to copy {filename}: {e}"
                logger.error(error_msg)
                copy_errors.append(error_msg)

        if copy_errors:
            print("\nERRORES AL COPIAR:")
            print("=" * 70)
            for error in copy_errors:
                print(f"  [FAIL] {error}")
            print("=" * 70 + "\n")
