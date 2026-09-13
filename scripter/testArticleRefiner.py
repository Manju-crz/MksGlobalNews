import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmUtil.articleRefinerUtil import ArticleRefiner, refine_single_article
from filesystemUtil.jsonutil import JsonUtil


def test_with_sample_text():
    """Test 1: Refine a sample article with noise"""
    print("="*100)
    print("TEST 1: Refining Sample Article with Noise")
    print("="*100)

    sample_article = """
WASHINGTON (AP) — Public health experts have been quick to condemn an executive order from President Donald Trump aimed at upending childhood vaccinations in the U.S.

Get more with a free CBC account! Subscribe now to our newsletter!!!

The announcement calls for separating combination shots — including the measles, mumps and rubella, or MMR, vaccine — into separate injections.

—

AP videojournalist Mary Conlon in New York contributed to this report.

—

Follow the AP's coverage of immunizations at https://apnews.com/hub/immunizations.

Follow us on Twitter @APnews for more updates!
"""

    headline = "Trump's vaccine plan would require millions of individual shots"

    print(f"\nHeadline: {headline}")
    print("\n--- ORIGINAL ARTICLE ---")
    print(sample_article)

    print("\n🔄 Refining article...")
    refined = refine_single_article(sample_article, headline)

    print("\n--- REFINED ARTICLE ---")
    print(refined)

    print("\n✅ Test 1 Complete")
    print("="*100)


def test_with_json_articles():
    """Test 2: Refine first 2 articles from JSON file"""
    print("\n" + "="*100)
    print("TEST 2: Refining Articles from JSON File")
    print("="*100)

    json_file = "dumps/2026_08_14_00_56_transformed.json"

    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return

    print(f"\n📖 Reading articles from: {json_file}")
    data = JsonUtil.read_json_content(json_file)

    # Test with first 2 articles
    test_count = 2
    print(f"\n🔄 Testing with first {test_count} articles...\n")

    refiner = ArticleRefiner()

    for idx, (record_id, article) in enumerate(list(data.items())[:test_count], 1):
        print(f"\n{'='*100}")
        print(f"Article {idx}/{test_count} - Record ID: {record_id}")
        print(f"Headline: {article.get('headline', 'No headline')}")
        print(f"Source: {article.get('source', 'Unknown')}")
        print(f"{'='*100}")

        original_content = article.get('article_content', '')
        headline = article.get('headline', '')

        print(f"\n📊 Original length: {len(original_content)} characters")

        print("\n--- ORIGINAL (first 300 chars) ---")
        print(original_content[:300] + "...")

        print("\n🔄 Refining...")
        refined_content = refiner.refine_article(original_content, headline)

        print(f"\n📊 Refined length: {len(refined_content)} characters")

        print("\n--- REFINED (first 300 chars) ---")
        print(refined_content[:300] + "...")

        print(f"\n✅ Article {idx} refined successfully")

    print("\n" + "="*100)
    print("✅ Test 2 Complete")
    print("="*100)


def test_batch_refinement():
    """Test 3: Batch refine multiple articles"""
    print("\n" + "="*100)
    print("TEST 3: Batch Refinement")
    print("="*100)

    json_file = "dumps/2026_08_14_00_56_transformed.json"

    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return

    print(f"\n📖 Reading articles from: {json_file}")
    data = JsonUtil.read_json_content(json_file)

    # Prepare batch of 3 articles
    batch_size = 3
    articles_batch = []

    for record_id in list(data.keys())[:batch_size]:
        article = data[record_id]
        articles_batch.append({
            'record_id': record_id,
            'headline': article.get('headline', ''),
            'article_content': article.get('article_content', ''),
            'source': article.get('source', '')
        })

    print(f"\n🔄 Batch refining {len(articles_batch)} articles...\n")

    refiner = ArticleRefiner()
    refined_batch = refiner.refine_article_batch(articles_batch)

    print("\n" + "="*100)
    print("BATCH REFINEMENT RESULTS")
    print("="*100)

    for idx, refined in enumerate(refined_batch, 1):
        original_len = len(articles_batch[idx-1]['article_content'])
        refined_len = len(refined['article_content'])

        print(f"\nArticle {idx} - Record {refined['record_id']}")
        print(f"  Headline: {refined['headline'][:60]}...")
        print(f"  Original: {original_len} chars -> Refined: {refined_len} chars")

    print("\n✅ Test 3 Complete")
    print("="*100)


def refine_all_and_save():
    """Test 4: Refine ALL articles and save to new file (WARNING: Takes time!)"""
    print("\n" + "="*100)
    print("TEST 4: Refine ALL Articles and Save")
    print("="*100)

    json_file = "dumps/2026_08_14_00_56_transformed.json"
    output_file = "dumps/2026_08_14_00_56_refined.json"

    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return

    print(f"\n📖 Reading articles from: {json_file}")
    data = JsonUtil.read_json_content(json_file)

    print(f"📊 Total articles to refine: {len(data)}")
    print(f"⚠️ This will take approximately {len(data) * 10} seconds (~{len(data) * 10 / 60:.1f} minutes)")

    confirm = input("\n⚠️ Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Cancelled by user")
        return

    print("\n🔄 Starting refinement process...\n")

    refiner = ArticleRefiner()
    refined_data = {}

    for idx, (record_id, article) in enumerate(data.items(), 1):
        print(f"\n[{idx}/{len(data)}] Record {record_id}: {article.get('headline', 'No headline')[:60]}...")

        try:
            refined_content = refiner.refine_article(
                article.get('article_content', ''),
                article.get('headline', '')
            )

            refined_data[record_id] = article.copy()
            refined_data[record_id]['article_content'] = refined_content

            original_len = len(article.get('article_content', ''))
            refined_len = len(refined_content)

            print(f"    ✅ {original_len} chars -> {refined_len} chars")

        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            refined_data[record_id] = article

    print(f"\n💾 Saving refined articles to: {output_file}")
    JsonUtil.replace_json_content(output_file, refined_data)

    print("\n" + "="*100)
    print("✅ ALL ARTICLES REFINED AND SAVED!")
    print("="*100)
    print(f"Total articles: {len(data)}")
    print(f"Output file: {output_file}")
    print("="*100)


if __name__ == "__main__":
    print("\n" + "="*100)
    print("ARTICLE REFINER UTILITY - TEST SUITE")
    print("="*100)

    # Run tests (uncomment the ones you want to run)

    # Test 1: Simple sample text
    test_with_sample_text()

    # Test 2: First 2 articles from JSON
    test_with_json_articles()

    # Test 3: Batch refinement of 3 articles
    # test_batch_refinement()

    # Test 4: Refine ALL articles and save (WARNING: Takes time and uses API credits!)
    # refine_all_and_save()

    print("\n" + "="*100)
    print("ALL TESTS COMPLETE")
    print("="*100)