# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static website serving as a local archive for CSWEP (Committee on the Status of Women in the Economics Profession) newsletters from the American Economic Association. The site displays newsletter PDFs from 1972-2025 with individual articles nested under each issue.

**Original source**: https://www.aeaweb.org/about-aea/committees/cswep/news-and-events/newsletters/archives

## Architecture

- **index.html**: Single-page archive with newsletters organized by year; articles appear nested under each newsletter issue
- **styles.css**: AEA-branded styling with responsive design
- **articles.json**: Article index data (477 articles, 1996-2025) with title, author, issue, year, topics array, and URL
- **build_index.py**: Python script to regenerate articles.json from Excel + manually curated data; includes `ISSUE_TOPICS` dictionary mapping issues to their focus topics
- **cswep_articles_index.xlsx**: Source Excel file from AEA (articles 1996-2018)

## Development

No build process required. Open `index.html` directly in a browser or serve with:
```bash
python -m http.server 8000
```

### Regenerating the Article Index

To update articles.json after modifying build_index.py:
```bash
python build_index.py
```

The script merges:
1. Excel data (339 articles, 1996-2018)
2. Manually curated scraped_articles list (146 articles, 2018-2025)

Article URLs use Google Docs viewer to display AEA PDFs in-browser:
`https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=XXXXX`

## Content Structure

Newsletter entries follow this HTML pattern:
```html
<div class="newsletter-item">
    <a href="https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=XXXXX" class="newsletter-link">Issue N YYYY</a>
    <span class="newsletter-focus">- Focus Topic</span>
    <span class="newsletter-editor">Co-Editor: Name</span>
</div>
```

Articles are injected dynamically from articles.json based on matching issue names.

## Adding New Articles

1. If adding a new issue, first add its focus topic to the `ISSUE_TOPICS` dictionary:
```python
"Issue I 2026": "Focus Topic Name",
```

2. Add articles to the `scraped_articles` list (topic field is for article-specific topics; issue topic is added automatically):
```python
{"title": "Article Title", "author": "Author Name", "issue": "Issue I 2026", "year": 2026, "topic": "Additional Topic", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=XXXXX"},
```

3. Run `python build_index.py` to regenerate articles.json.

Articles automatically inherit their issue's focus topic. The `topic` field is for additional article-specific topics (e.g., an article in a "Job Market" issue that also covers "Mentoring").

## Features

- **Search**: Filters newsletters and articles by text
- **Topic filter**: Dropdown with 47 individual topic categories; articles with multiple topics appear under each matching filter
- **Year filter**: Dropdown for years 1972-2025
- **Article badges**: Shows article count per newsletter issue; individual topic badges on each article
- **Citations**: `[Cite]` button on each issue and article; click to reveal formatted citation with copy button

### Citation Formats

Issue citation:
```
CSWEP News, Issue IV 2025: Focus on Fertility. American Economic Association. [URL]
```

Article citation:
```
Author Name. "Article Title." CSWEP News, Issue IV 2025. American Economic Association. [URL]
```

## Topic System

Articles have a `topics` array containing individual tags. Each article inherits its issue's focus topic plus any article-specific topics. For example, an article in Issue IV 2025 (Focus on Fertility) might have:
```json
"topics": ["Fertility", "Work-Life Balance"]
```

This article will appear when filtering by either "Fertility" or "Work-Life Balance".
