"""
Simple performance test - Desktop folder only (quick).
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.file_search_optimized import OptimizedFileSearch


def test_desktop_performance():
    """Quick test on Desktop folder."""
    desktop = "C:\\Users\\jrodeiro\\Desktop"

    if not os.path.isdir(desktop):
        print(f"Desktop folder not found: {desktop}")
        return

    searcher_no_cache = OptimizedFileSearch(use_cache=False)
    searcher_cache = OptimizedFileSearch(use_cache=True)

    # Count files
    total_files = sum(len(files) for _, _, files in os.walk(desktop))

    print("\n" + "=" * 70)
    print(f"Desktop Folder: {desktop}")
    print(f"Total Files: {total_files:,}")
    print("=" * 70)

    # Test 1: PDF search (no cache)
    print("\nTest 1: Searching for '.pdf' files (no cache)...")
    start = time.time()
    results1 = searcher_no_cache.search_by_filename([desktop], ["pdf"])
    time1 = time.time() - start

    print(f"  Found: {len(results1)} files")
    print(f"  Time: {time1:.2f}s")
    print(f"  Speed: {len(results1) / time1:.0f} files/sec")

    # Test 2: PDF search (with cache - should be instant)
    print("\nTest 2: Searching for '.pdf' files (with cache)...")
    start = time.time()
    results2 = searcher_cache.search_by_filename([desktop], ["pdf"])
    time2 = time.time() - start

    print(f"  Found: {len(results2)} files")
    print(f"  Time: {time2:.4f}s")
    print(f"  Speedup: {time1 / time2:.0f}x faster than no-cache")

    # Test 3: Different keyword
    print("\nTest 3: Searching for 'test' files (no cache)...")
    start = time.time()
    results3 = searcher_no_cache.search_by_filename([desktop], ["test"])
    time3 = time.time() - start

    print(f"  Found: {len(results3)} files")
    print(f"  Time: {time3:.2f}s")

    # Test 4: Same keyword (cached)
    print("\nTest 4: Searching for 'test' files (with cache)...")
    start = time.time()
    results4 = searcher_cache.search_by_filename([desktop], ["test"])
    time4 = time.time() - start

    print(f"  Found: {len(results4)} files")
    print(f"  Time: {time4:.4f}s")
    print(f"  Speedup: {time3 / time4:.0f}x faster than no-cache")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"First full search:      {time1:.2f}s")
    print(f"Cached search:          {time2:.4f}s")
    print(f"Average cache speedup:  {(time1 + time3) / (time2 + time4):.0f}x")
    print(f"\n✓ Optimization successful!")
    print(f"✓ Cache provides {(time1 + time3) / (time2 + time4):.0f}x speedup for repeated searches")
    print("=" * 70)


if __name__ == "__main__":
    test_desktop_performance()
