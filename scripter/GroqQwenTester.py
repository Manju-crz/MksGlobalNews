import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import reusable methods from llmUtil
from llmUtil.summarizerUtil import (
    summarize_article_with_groq,
    summarize_with_custom_instructions,
    batch_summarize_articles
)

# Example usage and testing
if __name__ == "__main__":
    print("=== Groq Qwen Article Summarizer ===\n")

    # Sample article for testing
    sample_article = """
Romania has shut down its only nuclear power station because of extremely low water levels
in the Danube river caused by prolonged hot weather affecting much of Europe.

The Cernavodă plant, where two reactors produce about 20% of Romania's electricity, is not
expected to be restarted within the next 10 days.

Earlier this week, authorities tried to increase the water flow to the plant - which uses
the Danube for cooling - by sinking barges loaded with rocks in the river.

Neighbouring Hungary has so far avoided a shutdown of its only nuclear plant in Paks, which
also uses the Danube. The waters in Europe's second-longest river have fallen to the lowest
levels for 30 years in several countries.

The second of the two 706-megawatt reactors at Cernavodă was disconnected from the Romanian
electricity grid just before midday on Thursday.

"We do not foresee a restart within the next 10 days," plant director Romeo Urjan told the
AFP news agency.

The first reactor had already been shut down in July.

Until now, Cernavodă had only been shut down once before in 2003.

The shortfall in power is usually covered by solar and wind during the hot, windy daytimes -
but traditional coal- and gas-powered generation will have to be supplemented by imports
during the evenings.

Romania also has huge hydropower capacity, although that has been heavily cut by the same
low river levels that caused the nuclear shutdown.
"""

    print("Sample Article:")
    print("-" * 80)
    print(sample_article.strip())
    print("-" * 80)

    # Test 1: Basic summarization
    print("\n--- Test 1: Basic Summarization ---")
    summary = summarize_article_with_groq(sample_article)

    if summary:
        print("\nGenerated Summary:")
        print("-" * 80)
        print(summary)
        print("-" * 80)

    # Test 2: Custom instructions
    print("\n--- Test 2: Custom Instructions (3 bullet points) ---")
    custom_summary = summarize_with_custom_instructions(
        sample_article,
        "Summarize the following article in exactly 3 bullet points. Be concise and focus on the most important facts."
    )

    if custom_summary:
        print("\nGenerated Summary:")
        print("-" * 80)
        print(custom_summary)
        print("-" * 80)

    # Test 3: One-sentence summary
    print("\n--- Test 3: One-Sentence Summary ---")
    one_sentence = summarize_with_custom_instructions(
        sample_article,
        "Summarize the following article in ONE sentence only."
    )

    if one_sentence:
        print("\nGenerated Summary:")
        print("-" * 80)
        print(one_sentence)
        print("-" * 80)