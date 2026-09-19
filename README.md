# MksGlobalNews

MksGlobalNews is a Python-based news aggregation and processing pipeline that scrapes major news sources, stores raw article data, transforms it into a flat format, compares articles for similarity, and groups related stories for downstream consolidation or refinement.

The current execution flow is driven by `Driver.py`, which acts as the main orchestration script for the full pipeline.

## Project overview

This project combines several responsibilities:

- Collecting news from multiple publishers
- Saving raw scraped data to timestamped JSON files in the `dumps/` folder
- Normalizing the scraped data into a flat article structure
- Detecting similar articles across sources using similarity scoring
- Grouping and consolidating related stories
- Supporting optional LLM-based summarization and media generation utilities

## Main execution flow

The real workflow is defined in `Driver.py`:

1. Run the scraper
   - Calls `run_news_scraper(...)` from `scrapers/utils/NewsScraper.py`
   - Scrapes BBC, The Guardian, DW, CBC, and AP News
   - Saves a timestamped JSON dump into `dumps/`

2. Transform raw source-grouped data
   - Calls `process_and_transform_json(...)` from `scripter/summarizer.py`
   - Converts the source-based structure into a flat numbered JSON dataset
   - Example structure becomes:

```python
{
  "1": {
    "headline": "...",
    "article_content": "...",
    "source": "bbc"
  }
}
```

3. Group and consolidate related articles
   - Calls `group_paired_articles(...)` and `consolidate_grouped_articles(...)` from `scripter/conciser.py`
   - Groups similar articles together and writes a refined JSON output file

## How the application runs

`Driver.py` contains the main entry point:

```python
if __name__ == "__main__":
    main()
```

The `main()` function does the following:

```python
news_data, json_filename = run_news_scraper(
    headless=False,
    save_file=True,
    show_sample=True
)
```

This starts the scraping stage and returns:

- `news_data`: the scraped article dictionary
- `json_filename`: the path to the saved raw JSON file

Then it creates an output file path in `dumps/` and runs:

```python
process_and_transform_json(
    input_json_file=json_filename,
    output_json_file=output_file
)
```

After transformation and summarization, it groups and consolidates the data:

```python
groups = group_paired_articles(
    json_file=output_file,
    similarity_threshold=90.0
)

refined_output = os.path.join(dumps_folder, base_filename.replace('.json', '_refined.json'))
refined_articles = consolidate_grouped_articles(
    groups=groups,
    input_file=output_file,
    output_file=refined_output
)
```

## Data flow summary

```text
Scrape sources
   -> raw JSON in dumps/
   -> flatten and normalize
   -> group related articles
   -> write refined JSON
```

## Repository structure

```text
MksGlobalNews/
├── Driver.py                     # Main orchestration entry point
├── README.md                    # Project documentation
├── requirements.txt             # Python package dependencies
├── all_news_data.json           # Generic combined dataset file
├── dumps/                       # Scraped and processed JSON outputs
├── util/                        # Shared utility packages
│   ├── dateTimeUtil/            # Timestamp utilities
│   ├── filesystemUtil/          # JSON and file helpers
│   ├── llmUtil/                 # AI/LLM utilities
│   └── youtubeUtil/             # YouTube integration
├── dumps/                       # Scraped data and generated media outputs
│   ├── generated_audios/
│   ├── generated_images/
│   └── generated_videos/
├── mediaGen/                    # Media generation support modules
├── Reference Documents/         # Reference docs and internal notes
├── scripter/                    # Transformation, comparison, grouping, and processing scripts
├── scrapers/                    # Scraping logic and source-specific tools
└── requirements.txt
```

## Source scraping modules

The scraper system gathers data from multiple publishers, mainly through the modules under `scrapers/finders/`:

- `BBC.py`
- `TheGuardian.py`
- `DW.py`
- `CBC.py`
- `APNews.py`

These are invoked by `NewsScraper.scrape_all()` in `scrapers/utils/NewsScraper.py`.

## Processing modules

### `scripter/summarizer.py`

This module:

- transforms grouped source data into a flat dictionary by article number
- extracts only `headline`, `article_content`, and `source`
- summarizes articles with the configured Groq model
- writes results to a transformed JSON output

### `scripter/conciser.py`

This module:

- groups articles that exceed similarity thresholds
- prepares a consolidated or refined dataset
- writes the grouped output to a refined file

## Dependencies

The project depends on:

- `playwright` for browser automation
- `requests` for HTTP requests
- `groq` for LLM access
- `python-dotenv` for environment handling
- `google-generativeai` for Google AI integration
- `sentence-transformers` for text similarity and embedding work
- `gTTS` for text-to-speech
- `moviepy` for video-related automation
- `Pillow` for image handling
- `huggingface_hub` for model ecosystem access

Install them with:

```bash
pip install -r requirements.txt
```

## Environment setup

For features involving LLM APIs or secrets, create a `.env` file in the project root with the required keys, depending on the services used by the utilities in `llmUtil/`.

Example:

```env
GROQ_API_KEY=your_key_here
```

## How to run the project

From the project root:

```bash
python Driver.py
```

This runs the complete pipeline:

- scraping all sources
- generating a raw JSON dump
- transforming the scraped data
- comparing article similarity
- grouping related stories
- generating refined output files in `dumps/`

## Important runtime behavior

In `Driver.py`, these parameters control behavior:

```python
run_news_scraper(
    headless=False,
    save_file=True,
    show_sample=True
)
```

- `headless=False`: shows the browser while scraping
- `headless=True`: runs in background mode
- `save_file=True`: writes raw data to JSON
- `show_sample=True`: prints sample output to the console

The transform step also contains:

```python
process_and_transform_json(..., summarize=False)
```

This keeps summarization off by default, but it can be enabled by switching that flag to `True`.

## Output files

The pipeline typically creates files in the `dumps/` folder with names like:

```text
dumps/
├── 2026_09_13_00_25.json
├── 2026_09_13_00_25_transformed.json
├── 2026_09_13_00_25_refined.json
```

These outputs represent:

- raw scraped data
- flattened transformed article data
- refined grouped article set

## Notes

This project is structured as a data-processing pipeline rather than a simple scraper. The key idea is to ingest news from multiple sources, transform it into analyzable form, detect duplicate or highly similar stories, and prepare the data for later summarization, media generation, or editorial review.

## Suggested next steps

- Add safer error handling for scraper failures per source
- Add retry logic for flaky network or browser actions
- Move constants such as thresholds and output paths into a config module
- Add a CLI wrapper so the workflow can be run with arguments instead of editing `Driver.py`
- Add tests for transformation and similarity grouping

## License

This project does not currently declare a license in the repository root. If you plan to distribute or publish it, add a proper license file before broad use.
