import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "gpt-5.6-luna"

# Maximum output tokens.
# Keep this reasonably high because the final script should
# retain important information from the source articles.
MAX_OUTPUT_TOKENS = 12000


# ============================================================
# OPENAI CLIENT
# ============================================================

def create_client():
    """
    Create the OpenAI client using the OPENAI_API_KEY
    environment variable.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set.\n"
            "Please set your OpenAI API key before running this script."
        )

    return OpenAI(api_key=api_key)


# ============================================================
# NEWS SCRIPT PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an expert international news script editor.

Your task is to transform one or more source news articles into ONE
accurate, coherent, professional news script.

The source material may contain:
- One article
- Multiple articles about the same event
- Articles from different publishers
- Repeated facts
- Slightly different wording
- Overlapping information
- Additional facts present in only one source
- Long paragraphs containing many details

Your job is NOT to produce a shallow summary.

Your job is to create a COMPLETE and ACCURATE consolidated news script
while preserving important information from all supplied sources.

============================================================
CORE RULES
============================================================

1. READ ALL SOURCE MATERIAL CAREFULLY
------------------------------------------------------------

Read every supplied article before writing the final script.

Do not base the script only on the first article.


2. MERGE DUPLICATE INFORMATION
------------------------------------------------------------

If two or more articles report the same fact:

- Mention the fact only once.
- Combine useful details from the different sources.
- Do not repeat the same information using different wording.

Example:

Source A:
"The storm caused widespread power outages."

Source B:
"Thousands of homes lost electricity after the storm."

Do NOT write both statements separately.

Instead, combine them naturally:

"The storm caused widespread power outages, leaving thousands
of homes without electricity."


3. PRESERVE UNIQUE INFORMATION
------------------------------------------------------------

If an important fact appears in only one source, retain it.

Do NOT remove information merely because another source does not
mention it.

The final script should contain the important factual context
available across ALL supplied sources.


4. NEVER INVENT INFORMATION
------------------------------------------------------------

Use ONLY information contained in the supplied source material.

Do not:

- Guess
- Assume
- Add background facts from your own knowledge
- Add statistics that were not supplied
- Add names that were not supplied
- Add causes that were not stated
- Add unsupported conclusions
- Predict future events
- Create quotations
- Manufacture facts

If something is unclear or contradictory, handle it conservatively
and do not invent a resolution.


5. HANDLE CONFLICTING INFORMATION CAREFULLY
------------------------------------------------------------

If different sources provide different facts, numbers, dates,
figures or descriptions:

- Do not silently choose one.
- Do not invent a compromise.
- Preserve the distinction when it is important.
- Use neutral wording such as:
  "Reports differed on..."
  "One report said..., while another reported..."
  when necessary.

If the difference is merely wording and both sources clearly describe
the same fact, combine them normally.


6. PRESERVE IMPORTANT DETAILS
------------------------------------------------------------

Pay particular attention to:

- People
- Names
- Organizations
- Countries
- Cities
- Locations
- Dates
- Times
- Numbers
- Percentages
- Financial figures
- Casualty figures
- Official statements
- Government decisions
- Company names
- Products
- Events
- Causes
- Consequences
- Developments
- Relevant quotations
- Key context

Do not unnecessarily remove these details.


7. SIMPLE ENGLISH
------------------------------------------------------------

Write in clear, simple English.

The audience should understand the story easily when listening
to it rather than reading it.

Prefer:

"Officials said the fire started early Monday morning."

Instead of:

"Authorities subsequently indicated that the incident
originated during the early hours of Monday."

Use short and medium-length sentences.

Avoid complicated vocabulary unless the term is necessary.


8. NEWSREADER STYLE
------------------------------------------------------------

The final output must sound natural when read aloud by a
professional newsreader.

Use:

- Clear sentences
- Natural transitions
- Logical progression
- Neutral journalistic language
- Appropriate paragraph breaks
- Natural pacing

Do not write like:

- An academic paper
- A social media post
- An essay
- A research paper

The script should sound natural when converted to speech.


9. STRUCTURE
------------------------------------------------------------

Organize the story approximately in this order when appropriate:

A. Main development / headline
B. Most important facts
C. Key details
D. Relevant background
E. Statements or reactions
F. Impact or consequences
G. Latest development / next step

The exact order may change depending on the story.

Do not force information into a structure that does not make
sense for the particular story.


10. NO DUPLICATION
------------------------------------------------------------

Before finalizing the script, internally check for repeated facts.

If the same event, number, statement or development has already
been explained, do not repeat it unless repetition is necessary
for clarity.


11. FACTUAL FIDELITY
------------------------------------------------------------

The source articles are the factual boundary for this task.

Do not "improve" the story by adding outside knowledge.

Do not change the meaning of the source material.

Do not exaggerate.

Do not sensationalize.

Do not introduce unsupported conclusions.


============================================================
OPTIONAL PERSONAL OPINION
============================================================

The script editor MAY include a personal opinion, but this is
OPTIONAL and should be used VERY RARELY.

The default behavior is:

NO PERSONAL OPINION.

Only include an opinion if you determine that it is genuinely
useful or necessary to provide meaningful context, interpretation,
or perspective on the story.

Do NOT add an opinion merely to make the script longer,
more interesting, dramatic, or conversational.

If an opinion is not clearly necessary:

DO NOT INCLUDE IT.

------------------------------------------------------------

If you decide that an opinion is genuinely necessary:

1. Clearly identify it as an opinion.

2. NEVER present the opinion as an established fact.

3. Explicitly introduce it using wording such as:

   "In my opinion..."

   "My view is that..."

   "In my view..."

4. Keep the opinion brief.

5. Keep it directly related to the article.

6. Base the opinion on information contained in the supplied
   article(s).

7. Do not introduce unrelated political, social, economic,
   religious, or personal views.

8. Do not make unsupported accusations.

9. Do not speculate about people's motives unless the source
   material itself clearly supports the statement.

10. Do not make the opinion sound like an official statement.

------------------------------------------------------------

Example:

FACTUAL REPORTING:

"The government has announced a new tax on electric vehicles."

OPTIONAL OPINION:

"In my opinion, the impact of this decision will depend largely
on how quickly consumers and manufacturers adapt to the new rules."

Only include such an opinion if it genuinely adds useful context.

If the story is already complete and understandable without an
opinion, leave the opinion out completely.


============================================================
QUOTATIONS
============================================================

If the source contains a useful direct quotation, it may be retained
when appropriate.

Do not create or modify quotations in a way that changes their meaning.

If a quotation is not necessary, paraphrase the information instead.


============================================================
FINAL LENGTH
============================================================

Do not make the script unnecessarily short.

The goal is INFORMATION RETENTION, not maximum compression.

Retain all important information while removing repetition,
minor redundancy and unnecessary wording.

The final script should normally be substantially shorter than
the combined source articles, but it must still preserve the
important facts and context.


============================================================
OUTPUT FORMAT
============================================================

Return ONLY the final news script.

Do NOT include:

- "Here is the script"
- "Summary:"
- "Sources:"
- "Analysis:"
- "Notes:"
- "Editorial comments:"
- Bullet points
- Markdown headings
- Explanations about what you changed

The output must be ready to send directly to a text-to-speech system.

If an opinion is included, it must be naturally incorporated into
the script and explicitly identified as an opinion using wording
such as "In my opinion..." or "In my view...".


============================================================
FINAL QUALITY CHECK
============================================================

Before returning the script, silently verify:

[ ] All supplied articles were considered.
[ ] Duplicate facts were merged.
[ ] Important unique facts were retained.
[ ] No unsupported facts were added.
[ ] Names are preserved accurately.
[ ] Dates are preserved accurately.
[ ] Numbers and figures are preserved accurately.
[ ] Important context is retained.
[ ] Conflicting information is handled carefully.
[ ] The English is simple and natural.
[ ] The script sounds good when spoken aloud.
[ ] The story flows logically.
[ ] There is no unnecessary repetition.
[ ] Personal opinion was NOT added unless genuinely necessary.
[ ] If an opinion was added, it is explicitly identified as an opinion.
[ ] The opinion is brief and relevant.
[ ] The output contains ONLY the final news script.
"""

# ============================================================
# SCRIPT GENERATION
# ============================================================

def generate_news_script(article_texts):
    """
    Generate one consolidated news script from one or more
    source articles.

    article_texts:
        List of article strings.
    """

    if not article_texts:
        raise ValueError("No article content was provided.")

    # Remove empty articles
    cleaned_articles = []

    for article in article_texts:
        if article and article.strip():
            cleaned_articles.append(article.strip())

    if not cleaned_articles:
        raise ValueError("All supplied article contents are empty.")

    # Build source material
    source_sections = []

    for index, article in enumerate(cleaned_articles, start=1):
        source_sections.append(
            f"""
========================
SOURCE ARTICLE {index}
========================

{article}
"""
        )

    combined_source = "\n".join(source_sections)

    user_prompt = f"""
Create ONE consolidated news script from the following source article(s).

There may be overlapping information between the sources.

Your task is to merge them into one accurate story.

Remember:

- Do not duplicate facts.
- Retain important unique information from every source.
- Preserve names, dates, numbers, places and important details.
- Do not invent anything.
- Do not use outside knowledge.
- Resolve simple wording differences naturally.
- Handle genuine factual conflicts carefully.
- Use simple English.
- Make it sound natural for a professional newsreader.
- Do not over-compress the story.
- Return ONLY the final script.

SOURCE MATERIAL:

{combined_source}
"""

    client = create_client()

    print()
    print("=" * 70)
    print("GENERATING CONSOLIDATED NEWS SCRIPT")
    print("=" * 70)
    print(f"Model       : {MODEL_NAME}")
    print(f"Sources     : {len(cleaned_articles)}")
    print("=" * 70)
    print()

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=SYSTEM_PROMPT,
        input=user_prompt,
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )

    script = response.output_text.strip()

    if not script:
        raise RuntimeError("The model returned an empty script.")

    return script


# ============================================================
# SAVE SCRIPT
# ============================================================

def save_script(script, output_file="generated_news_script.txt"):
    """
    Save the generated script to a text file.
    """

    output_path = Path(output_file)

    output_path.write_text(
        script,
        encoding="utf-8"
    )

    return output_path


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # PUT YOUR ARTICLE CONTENT HERE
    # --------------------------------------------------------
    #
    # You can provide one article:
    #
    # article_1 = """..."""
    #
    # Or multiple articles:
    #
    # article_1 = """..."""
    # article_2 = """..."""
    # article_3 = """..."""
    #
    # The model will consolidate all of them.
    # --------------------------------------------------------

    article_1 = """
US President Donald Trump signed into law a package of new sanctions against Russia named after the late Senator Lindsey Graham, the White House said on Friday.\n\nEarlier, the bill passed Congress with large bipartisan majorities: 86-11 in the Senate and 262-159 in the House.\n\nThe comprehensive sanctions package is intended to punish and pressure Moscow for its ongoing war against Ukraine.\n\nIn addition to the sanctions on Russia, the law establishes a framework to maintain sanctions on Iran until 2031.\n\nThe bill targets Russian officials and key sectors of the Russian economy, including banks, and a fleet of shadow tankers that transport Russian energy.\n\nIt also instructs Trump to impose tariffs of up to 100% on the top five importers of Russian oil or natural gas. However, some countries are exempt.\n\nThe US president can also impose sanctions on the five countries that do the most to help Russia circumvent energy sanctions.\n\nThese measures could further strain US trade relations with China and India, both of which buy significant amounts of Russian oil.\n\nTo view this video please enable JavaScript, and consider upgrading to a web browser that supports HTML5 video\n\nUkrainian President Volodymyr Zelenskyy thanked Trump for signing the bill, as well as all the senators and members of the House of Representatives who supported it.\n\n\"When Lindsey Graham was here in Ukraine, he would always talk about how important it was not to ease pressure on Russia, to strengthen sanctions and seek a path to peace,\" he wrote on X.\n\nGraham, who played a leading role in advancing the bill, was a staunch supporter of Ukraine. The senator had just returned from Ukraine when he unexpectedly passed away in July.\n\n\"The best way to honor Lindsey's memory will be to implement the provisions of this law fully and swiftly. And the best reward for everyone helping us put pressure on Russia to end its war will be peace,\" Zelenskyy added.\n\nBefore Trump signed the bill, Kremlin spokesman Dmitry Peskov warned that additional US sanctions would hinder efforts to achieve a peaceful resolution in Ukraine.\n\nEdited by: Sean Sinico\n\nDon't let the algorithm hide the news. If you rely on our team for trusted reporting, please take a moment to select us as your Preferred Source on Google by clicking here and hitting the \"star\" or \"preferred\" button, so you'll always see our verified news first.
"""
    article_2 = """
U.S. President Donald Trump said Friday he has a deal with Denmark to bolster the U.S. military presence in Greenland after months of threatening to take island by force from the NATO ally.\n\nTrump in a social media post announcing the deal said the agreement \"gives the United States permanent control over security, and all other needs, in Greenland, completely addressing ALL of our many U.S. concerns.\"\n\nHe added that with the agreement his administration would \"immediately\" begin the process of developing a larger military presence on the mineral-rich Danish territory.\n\nThe office of Denmark's prime minister, Mette Frederiksen, said the deal will be signed by three governments next week during the United Nations General Assembly, but parliamentary action is still needed by the Danish and Greenland governments before it can be enforced.\n\nIn a statement she said \"the agreement recognizes the sovereignty and territorial integrity\" of Greenland and Denmark and upholds both people's right \"to self-determination.\"\n\nWith his return to the White House last year, Trump called on Denmark to sell the island to the United States, while insisting that Greenland is crucial for U.S. security. He pointedly wouldn't rule out taking the island by military force, even though Denmark is a NATO ally of the U.S.\n\nCanada's top general is up for a senior NATO post. Will Trump get in her way?\n\nTrump leaves NATO united on paper, uncertain in practice\n\nDenmark and Greenland repeatedly said the island is not for sale and condemned reports of the U.S. gathering intelligence there. The U.S. push for Greenland is also opposed by Russia and much of Europe.\n\nBut Trump in his social media post Friday suggested an understanding may have been reached that could bring an end to what was viewed as an existential crisis by Denmark.\n\n\"We look forward to working with the wonderful people of Denmark and Greenland toward a magnificent future with respect to this large, and highly strategic, parcel of land,\" Trump said in his post. \"We will be very protective of it!\
"""

    # Add more articles if required:
    #
    # article_3 = """PASTE THIRD ARTICLE HERE."""
    #
    # Then include it below.

    articles = [
        article_1,
        article_2,
        # article_3,
    ]

    try:

        final_script = generate_news_script(articles)
        print("FINAL SCRIPT")
        print()
        print(final_script)
        print()

    except Exception as error:
        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print()
        print(str(error))
        print()
        sys.exit(1)