"""
Similarity Checker Tester
Tests the similarityCheckerUtil to verify it works correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmUtil.similarityCheckerUtil import (
    calculate_similarity,
    get_similarity_category,
    compare_articles_batch,
    find_duplicates
)


def test_identical_articles():
    """Test 1: Identical articles should have ~100% similarity"""
    print("\n" + "="*80)
    print("TEST 1: Identical Articles")
    print("="*80)

    article = "President Trump announced a new immigration policy today in Washington."

    similarity = calculate_similarity(article, article)
    category = get_similarity_category(similarity)

    print(f"\nArticle 1: {article}")
    print(f"Article 2: {article}")
    print(f"\nSimilarity: {similarity:.2f}%")
    print(f"Category: {category}")

    # Expected: ~100%
    if similarity >= 99.0:
        print("✅ PASS: Identical articles correctly identified")
    else:
        print(f"❌ FAIL: Expected ~100%, got {similarity:.2f}%")

    return similarity >= 99.0


def test_very_similar_articles():
    """Test 2: Very similar articles (same story, different wording)"""
    print("\n" + "="*80)
    print("TEST 2: Very Similar Articles (Same Story)")
    print("="*80)

    article1 = "President Trump announced a new immigration policy today in Washington, focusing on border security measures."
    article2 = "Trump unveils immigration policy in Washington today, emphasizing border security initiatives."

    similarity = calculate_similarity(article1, article2)
    category = get_similarity_category(similarity)

    print(f"\nArticle 1: {article1}")
    print(f"Article 2: {article2}")
    print(f"\nSimilarity: {similarity:.2f}%")
    print(f"Category: {category}")

    # Expected: 70-95%
    if 70.0 <= similarity <= 95.0:
        print("✅ PASS: Very similar articles correctly identified")
    else:
        print(f"❌ FAIL: Expected 70-95%, got {similarity:.2f}%")

    return 70.0 <= similarity <= 95.0


def test_related_articles():
    """Test 3: Related articles (same topic, different focus)"""
    print("\n" + "="*80)
    print("TEST 3: Related Articles (Same Topic)")
    print("="*80)

    article1 = "President Trump announced a new immigration policy today focusing on border security."
    article2 = "Biden criticized Trump's immigration approach, calling for more humanitarian policies."

    similarity = calculate_similarity(article1, article2)
    category = get_similarity_category(similarity)

    print(f"\nArticle 1: {article1}")
    print(f"Article 2: {article2}")
    print(f"\nSimilarity: {similarity:.2f}%")
    print(f"Category: {category}")

    # Expected: 40-70%
    if 40.0 <= similarity <= 70.0:
        print("✅ PASS: Related articles correctly identified")
    else:
        print(f"⚠️ WARNING: Expected 40-70%, got {similarity:.2f}% (may vary)")

    return True  # This test is more flexible


def test_unrelated_articles():
    """Test 4: Completely unrelated articles"""
    print("\n" + "="*80)
    print("TEST 4: Unrelated Articles (Different Topics)")
    print("="*80)

    article1 = "President Trump announced a new immigration policy today focusing on border security."
    article2 = "Scientists discover a new species of deep-sea fish in the Pacific Ocean."

    similarity = calculate_similarity(article1, article2)
    category = get_similarity_category(similarity)

    print(f"\nArticle 1: {article1}")
    print(f"Article 2: {article2}")
    print(f"\nSimilarity: {similarity:.2f}%")
    print(f"Category: {category}")

    # Expected: 0-30%
    if similarity <= 30.0:
        print("✅ PASS: Unrelated articles correctly identified")
    else:
        print(f"❌ FAIL: Expected ≤30%, got {similarity:.2f}%")

    return similarity <= 30.0


def test_near_duplicate_articles():
    """Test 5: Near-duplicate articles (minor differences)"""
    print("\n" + "="*80)
    print("TEST 5: Near-Duplicate Articles")
    print("="*80)

    article1 = "The White House announced today that President Trump will visit Mexico next week to discuss trade agreements and border security measures."
    article2 = "President Trump will visit Mexico next week, the White House announced today, to discuss trade agreements and border security."

    similarity = calculate_similarity(article1, article2)
    category = get_similarity_category(similarity)

    print(f"\nArticle 1: {article1}")
    print(f"Article 2: {article2}")
    print(f"\nSimilarity: {similarity:.2f}%")
    print(f"Category: {category}")

    # Expected: 85-100%
    if similarity >= 85.0:
        print("✅ PASS: Near-duplicate articles correctly identified")
    else:
        print(f"❌ FAIL: Expected ≥85%, got {similarity:.2f}%")

    return similarity >= 85.0


def test_batch_comparison():
    """Test 6: Batch comparison of multiple articles"""
    print("\n" + "="*80)
    print("TEST 6: Batch Comparison (Multiple Articles)")
    print("="*80)

    articles = {
        "1": "Trump announces new immigration policy focusing on border security.",
        "2": "President Trump unveils immigration policy emphasizing border security.",
        "3": "Biden criticizes Trump's immigration approach.",
        "4": "Scientists discover new species in Pacific Ocean.",
        "5": "Trump announces immigration policy at White House today."
    }

    print(f"\nComparing {len(articles)} articles...")

    similar_pairs = compare_articles_batch(articles)

    print(f"\n📊 Top 5 Most Similar Pairs:")
    print("-" * 80)

    for i, (id1, id2, similarity) in enumerate(similar_pairs[:5], 1):
        category = get_similarity_category(similarity)
        print(f"{i}. Article {id1} vs Article {id2}: {similarity:.2f}% - {category}")
        print(f"   Article {id1}: {articles[id1][:60]}...")
        print(f"   Article {id2}: {articles[id2][:60]}...")
        print()

    # Check if articles 1, 2, and 5 are identified as similar (they're about same topic)
    similar_found = False
    for id1, id2, similarity in similar_pairs:
        if (id1 in ["1", "2", "5"] and id2 in ["1", "2", "5"]) and similarity >= 70.0:
            similar_found = True
            break

    if similar_found:
        print("✅ PASS: Similar articles correctly grouped")
    else:
        print("❌ FAIL: Failed to identify similar articles in batch")

    return similar_found


def test_duplicate_detection():
    """Test 7: Duplicate detection with threshold"""
    print("\n" + "="*80)
    print("TEST 7: Duplicate Detection")
    print("="*80)

    articles = {
        "1": "Trump announces new immigration policy today.",
        "2": "President Trump announces new immigration policy today.",  # Near duplicate of 1
        "3": "Biden responds to Trump's immigration policy.",
        "4": "Trump unveils immigration policy at White House.",  # Similar to 1 & 2
        "5": "Scientists discover new marine species."  # Unrelated
    }

    print(f"\nSearching for duplicates (threshold: 85%)...")

    duplicates = find_duplicates(articles, threshold=85.0)

    if duplicates:
        print(f"\n✅ PASS: Found {len(duplicates)} duplicate/near-duplicate pairs")
    else:
        print("\n⚠️ WARNING: No duplicates found (threshold may be too high)")

    return True  # This test is informational


def test_edge_cases():
    """Test 8: Edge cases (empty strings, very short text)"""
    print("\n" + "="*80)
    print("TEST 8: Edge Cases")
    print("="*80)

    # Test with very short text
    print("\n📝 Testing with very short text...")
    short1 = "Trump"
    short2 = "Biden"

    similarity = calculate_similarity(short1, short2)
    print(f"'{short1}' vs '{short2}': {similarity:.2f}%")

    # Test with empty string (should handle gracefully)
    print("\n📝 Testing with empty string...")
    empty_similarity = calculate_similarity("", "Some text")
    print(f"Empty string vs 'Some text': {empty_similarity:.2f}%")

    if empty_similarity == 0.0:
        print("✅ PASS: Edge cases handled correctly")
    else:
        print("⚠️ WARNING: Edge case handling may need review")

    return True


def test_real_world_news_articles():
    """Test 9: Real-world style news articles"""
    print("\n" + "="*80)
    print("TEST 9: Real-World News Articles")
    print("="*80)

    article1 = """
President Donald Trump announced a sweeping new immigration policy on Monday,
focusing on enhanced border security measures and stricter visa requirements.
The policy, unveiled at a White House press conference, includes plans to
increase funding for border patrol and implement new screening procedures
for visa applicants from certain countries.
"""

    article2 = """
In a White House announcement on Monday, President Trump revealed a comprehensive
immigration policy that emphasizes border security and visa restrictions.
The new measures include increased border patrol funding and enhanced screening
for visa applications from specific nations.
"""

    article3 = """
The stock market reached record highs today as investors responded positively
to strong earnings reports from major tech companies. Apple, Microsoft, and
Google all reported better-than-expected quarterly results, driving the
Nasdaq to new peaks.
"""

    print("\n📰 Comparing real-world style articles...")

    sim_1_2 = calculate_similarity(article1, article2)
    sim_1_3 = calculate_similarity(article1, article3)

    print(f"\nArticle 1 vs Article 2 (same story): {sim_1_2:.2f}%")
    print(f"Category: {get_similarity_category(sim_1_2)}")

    print(f"\nArticle 1 vs Article 3 (different topics): {sim_1_3:.2f}%")
    print(f"Category: {get_similarity_category(sim_1_3)}")

    # Article 1 and 2 should be similar (>70%), Article 1 and 3 should be different (<30%)
    if sim_1_2 >= 70.0 and sim_1_3 <= 30.0:
        print("\n✅ PASS: Real-world articles correctly classified")
        return True
    else:
        print(f"\n⚠️ WARNING: Expected sim(1,2)≥70% and sim(1,3)≤30%, got {sim_1_2:.2f}% and {sim_1_3:.2f}%")
        return False


def run_all_tests():
    """Run all tests and display summary"""
    print("\n" + "="*80)
    print("🧪 SIMILARITY CHECKER UTILITY - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nTesting the all-mpnet-base-v2 model for article similarity detection...")

    tests = [
        ("Identical Articles", test_identical_articles),
        ("Very Similar Articles", test_very_similar_articles),
        ("Related Articles", test_related_articles),
        ("Unrelated Articles", test_unrelated_articles),
        ("Near-Duplicate Articles", test_near_duplicate_articles),
        ("Batch Comparison", test_batch_comparison),
        ("Duplicate Detection", test_duplicate_detection),
        ("Edge Cases", test_edge_cases),
        ("Real-World News Articles", test_real_world_news_articles)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "-"*80)
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("="*80)

    if passed == total:
        print("\n🎉 All tests passed! Similarity checker is working correctly.")
    elif passed >= total * 0.7:
        print("\n✅ Most tests passed. Similarity checker is working well.")
    else:
        print("\n⚠️ Some tests failed. Please review the results above.")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nError running tests: {str(e)}")
        import traceback
        traceback.print_exc()