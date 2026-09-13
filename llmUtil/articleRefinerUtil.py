import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class ArticleRefiner:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def refine_article(self, article_content, headline=""):
        """
        Refines article content by removing noise and making it professionally readable.

        Args:
            article_content (str): The raw article content to refine
            headline (str): Optional headline for context

        Returns:
            str: Refined article content
        """
        try:
            prompt = self._build_refinement_prompt(article_content, headline)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional news editor. Your job is to refine news articles "
                                   "while preserving all factual information, quotes, and key details."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=8000
            )

            refined_content = response.choices[0].message.content.strip()
            return refined_content

        except Exception as e:
            print(f"Error refining article: {str(e)}")
            return article_content

    def _build_refinement_prompt(self, article_content, headline):
        """Builds the prompt for article refinement."""
        prompt = f"""Refine the following news article to make it professionally readable """
        prompt += f"""while following these rules:

RULES:
1. Remove noise, redundant phrases, and unnecessary filler text
2. Fix grammar, spelling, and punctuation errors
3. Improve sentence structure and flow for better readability
4. Remove promotional content (e.g., "Subscribe now", "Follow us", "Get more with...")
5. Remove metadata and attribution lines (e.g., "AP Photo", "___", reporter credits at the end)
6. Keep ALL factual information, quotes, names, dates, and statistics
7. Maintain the original tone and perspective
8. Keep the article in third-person journalistic style
9. Preserve all direct quotes exactly as they appear
10. Do NOT add new information or opinions
11. Do NOT change the meaning or facts
12. Return ONLY the refined article content, no explanations or comments

"""

        if headline:
            prompt += f"HEADLINE: {headline}\n\n"

        prompt += f"ARTICLE CONTENT:\n{article_content}\n\nREFINED ARTICLE:"

        return prompt

    def refine_article_batch(self, articles_list):
        """
        Refines multiple articles in batch.

        Args:
            articles_list (list): List of dicts with 'headline' and 'article_content' keys

        Returns:
            list: List of refined articles with same structure
        """
        refined_articles = []

        for idx, article in enumerate(articles_list, 1):
            print(f"Refining article {idx}/{len(articles_list)}: "
                  f"{article.get('headline', 'No headline')[:50]}...")

            refined_content = self.refine_article(
                article.get('article_content', ''),
                article.get('headline', '')
            )

            refined_article = article.copy()
            refined_article['article_content'] = refined_content
            refined_articles.append(refined_article)

            print(f"    ✅ Refined successfully")

        return refined_articles


def refine_single_article(article_content, headline=""):
    """
    Convenience function to refine a single article.

    Args:
        article_content (str): The article content to refine
        headline (str): Optional headline

    Returns:
        str: Refined article content
    """
    refiner = ArticleRefiner()
    return refiner.refine_article(article_content, headline)