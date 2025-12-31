"""
Performance benchmark for optimized file search.

Tests old vs new search performance on real folders.
"""

import datetime
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.file_search_optimized import FileSearch, OptimizedFileSearch


class PerformanceBenchmark:
    """Run performance benchmarks on file search."""

    def __init__(self):
        self.results = []
        self.real_folders = [
            "C:\\Users\\jrodeiro\\Desktop",
            "C:\\Users\\jrodeiro\\Downloads",
        ]

    def count_files(self, folder: str) -> int:
        """Count files in a folder tree."""
        count = 0
        try:
            for _, _, files in os.walk(folder):
                count += len(files)
        except Exception as e:
            print(f"Error counting files in {folder}: {e}")
        return count

    def benchmark_search(self, folder: str, keywords: List[str], use_cache: bool = False,
                        name: str = "") -> Dict:
        """
        Benchmark a single search operation.

        Returns dict with timing and result count.
        """
        searcher = OptimizedFileSearch(use_cache=use_cache)

        # Warm up
        if use_cache:
            # First pass warms up cache
            searcher.search_by_filename([folder], keywords)

        # Actual benchmark
        start_time = time.time()
        results = searcher.search_by_filename([folder], keywords)
        elapsed = time.time() - start_time

        return {
            "name": name,
            "folder": folder,
            "keywords": keywords,
            "use_cache": use_cache,
            "elapsed_seconds": elapsed,
            "results_found": len(results),
            "files_per_second": len(results) / elapsed if elapsed > 0 else 0,
        }

    def benchmark_real_folders(self):
        """Benchmark search on real Desktop/Downloads folders."""
        print("\n" + "=" * 70)
        print("REAL FOLDER PERFORMANCE BENCHMARK")
        print("=" * 70)

        keywords_list = [
            (["pdf"], "PDF files"),
            (["docx", "doc"], "Office documents"),
            (["python", "py"], "Python files"),
            (["2025"], "2025 files"),
            (["test"], "Test files"),
        ]

        for folder in self.real_folders:
            if not os.path.isdir(folder):
                print(f"\nSkipping {folder} (does not exist)")
                continue

            file_count = self.count_files(folder)
            print(f"\nFolder: {folder}")
            print(f"Total files: {file_count:,}")
            print("-" * 70)

            for keywords, description in keywords_list:
                # Test without cache
                result_no_cache = self.benchmark_search(
                    folder, keywords,
                    use_cache=False,
                    name=f"No cache - {description}"
                )

                # Test with cache (second pass)
                result_cache = self.benchmark_search(
                    folder, keywords,
                    use_cache=True,
                    name=f"Cached - {description}"
                )

                self.results.append(result_no_cache)
                self.results.append(result_cache)

                speedup = result_no_cache["elapsed_seconds"] / result_cache["elapsed_seconds"]

                print(f"\n  {description}:")
                print(f"    No cache:  {result_no_cache['elapsed_seconds']:.2f}s ({result_no_cache['results_found']} files)")
                print(f"    Cached:    {result_cache['elapsed_seconds']:.4f}s ({result_cache['results_found']} files)")
                print(f"    Speedup:   {speedup:.1f}x faster")

    def benchmark_test_folders(self):
        """Benchmark with different folder sizes."""
        print("\n" + "=" * 70)
        print("TEST FOLDER SIZE SCALING BENCHMARK")
        print("=" * 70)

        sizes = [
            (10, "Small (10 files)"),
            (100, "Medium (100 files)"),
            (1000, "Large (1,000 files)"),
        ]

        keywords = ["test"]

        with tempfile.TemporaryDirectory() as tmpdir:
            for target_size, description in sizes:
                # Create test files
                test_folder = os.path.join(tmpdir, f"test_{target_size}")
                os.makedirs(test_folder, exist_ok=True)

                # Create subdirectories and files
                subdir_count = max(1, target_size // 100)
                files_per_subdir = target_size // subdir_count

                for i in range(subdir_count):
                    subdir = os.path.join(test_folder, f"subdir_{i}")
                    os.makedirs(subdir, exist_ok=True)

                    for j in range(files_per_subdir):
                        filename = os.path.join(subdir, f"test_file_{j}.txt")
                        Path(filename).touch()

                file_count = self.count_files(test_folder)

                print(f"\n{description}")
                print("-" * 70)

                # Benchmark
                result = self.benchmark_search(
                    test_folder, keywords,
                    use_cache=False,
                    name=description
                )

                self.results.append(result)

                print(f"  Actual files: {file_count:,}")
                print(f"  Found: {result['results_found']}")
                print(f"  Time: {result['elapsed_seconds']:.4f}s")
                print(f"  Speed: {result['files_per_second']:.0f} files/sec")

    def print_summary(self):
        """Print benchmark summary."""
        if not self.results:
            return

        print("\n" + "=" * 70)
        print("BENCHMARK SUMMARY")
        print("=" * 70)

        # Summary statistics
        uncached = [r for r in self.results if not r.get("use_cache", False)]
        cached = [r for r in self.results if r.get("use_cache", False)]

        if uncached:
            avg_uncached = sum(r["elapsed_seconds"] for r in uncached) / len(uncached)
            print(f"\nAverage search time (no cache): {avg_uncached:.2f}s")

        if cached:
            avg_cached = sum(r["elapsed_seconds"] for r in cached) / len(cached)
            print(f"Average search time (cached):   {avg_cached:.4f}s")

            if uncached:
                speedup = sum(r["elapsed_seconds"] for r in uncached) / sum(
                    r["elapsed_seconds"] for r in cached
                )
                print(f"Average cache speedup:         {speedup:.1f}x faster")

        # Performance per file
        all_results = [r for r in self.results if not r.get("use_cache", False)]
        if all_results:
            avg_files_per_sec = sum(r["files_per_second"] for r in all_results) / len(all_results)
            print(f"\nAverage scan speed:            {avg_files_per_sec:.0f} files/second")

    def run_all_benchmarks(self):
        """Run all benchmarks."""
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  FILE SEARCH PERFORMANCE BENCHMARK".center(68) + "║")
        print("║" + "  Testing optimized os.scandir + SQLite caching".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "=" * 68 + "╝")

        # Run benchmarks
        self.benchmark_test_folders()
        self.benchmark_real_folders()
        self.print_summary()

        print("\n")


def main():
    """Run performance benchmarks."""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()


if __name__ == "__main__":
    main()
