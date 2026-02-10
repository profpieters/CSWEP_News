"""
Build the CSWEP News Archives site from the master spreadsheet.

Reads cswep_news_master.xlsx and generates:
  - index.html (from template.html + Issues sheet)
  - articles.json (from Articles sheet)

Usage:
    python build_site.py
"""

import pandas as pd
import json
import re
from html import escape

XLSX_PATH = 'cswep_news_master.xlsx'
TEMPLATE_PATH = 'template.html'
OUTPUT_HTML = 'index.html'
OUTPUT_JSON = 'articles.json'
LOAD_MORE_CUTOFF = 2021  # Years >= this shown initially


def read_issues(xlsx_path):
    """Read Issues sheet, return list of dicts."""
    df = pd.read_excel(xlsx_path, sheet_name='Issues')
    issues = []
    for _, row in df.iterrows():
        issues.append({
            'issue': str(row['issue']).strip(),
            'year': int(row['year']),
            'focus_topic': str(row['focus_topic']).strip() if pd.notna(row['focus_topic']) else '',
            'editor': str(row['editor']).strip() if pd.notna(row['editor']) else '',
            'url': str(row['url']).strip() if pd.notna(row['url']) else '',
        })
    return issues


def read_articles(xlsx_path):
    """Read Articles sheet, parse topics, deduplicate."""
    df = pd.read_excel(xlsx_path, sheet_name='Articles')
    articles = []
    for _, row in df.iterrows():
        title = str(row['title']).strip() if pd.notna(row['title']) else ''
        if not title:
            continue

        # Parse topics column (comma-separated string)
        topics_str = str(row['topics']).strip() if pd.notna(row.get('topics')) else ''
        topics_list = [t.strip() for t in topics_str.split(',') if t.strip()]

        articles.append({
            'title': title,
            'author': str(row['author']).strip() if pd.notna(row['author']) else '',
            'issue': str(row['issue']).strip() if pd.notna(row['issue']) else '',
            'year': int(row['year']) if pd.notna(row['year']) else 0,
            'url': str(row['url']).strip() if pd.notna(row['url']) and str(row['url']).startswith('http') else '',
            'topics': topics_list,
        })

    # Deduplicate by normalized title
    seen = set()
    unique = []
    for a in articles:
        norm = re.sub(r'[^a-z0-9]', '', a['title'].lower())
        if norm not in seen and len(norm) > 5:
            seen.add(norm)
            unique.append(a)

    # Sort by year descending, then title ascending
    unique.sort(key=lambda x: (-x['year'], x['title']))
    return unique


def generate_newsletter_html(issues, load_more_cutoff):
    """Generate the newsletter list HTML from issues data."""
    # Group issues by year, preserving order within each year
    years_dict = {}
    for issue in issues:
        y = issue['year']
        if y not in years_dict:
            years_dict[y] = []
        years_dict[y].append(issue)

    # Sort years descending
    sorted_years = sorted(years_dict.keys(), reverse=True)

    min_year = min(sorted_years)
    max_year = max(sorted_years)

    lines = []
    load_more_inserted = False

    for year in sorted_years:
        is_hidden = year < load_more_cutoff

        # Insert Load More button at the boundary
        if is_hidden and not load_more_inserted:
            hidden_count = sum(1 for y in sorted_years if y < load_more_cutoff)
            lines.append('')
            lines.append('                <!-- Load More Button -->')
            lines.append('                <div class="load-more-container" id="load-more-container">')
            lines.append(f'                    <button class="load-more-btn" id="load-more-btn">Load Earlier Years ({min_year}-{load_more_cutoff - 1})</button>')
            lines.append(f'                    <div class="load-more-info">{hidden_count} more years of archives</div>')
            lines.append('                </div>')
            lines.append('')
            load_more_inserted = True

        hidden_class = ' hidden-year' if is_hidden else ''
        lines.append(f'                <section class="year-section{hidden_class}">')
        lines.append(f'                    <h2 class="year-heading">{year}</h2>')

        for issue in years_dict[year]:
            focus = escape(issue['focus_topic']) if issue['focus_topic'] else ''
            editor = escape(issue['editor']) if issue['editor'] else ''
            url = escape(issue['url'])
            name = escape(issue['issue'])

            line = f'                    <div class="newsletter-item">'
            line += f'<a href="{url}" class="newsletter-link">{name}</a>'
            if focus:
                line += f'<span class="newsletter-focus">- {focus}</span>'
            if editor:
                line += f'<span class="newsletter-editor">{editor}</span>'
            line += '</div>'
            lines.append(line)

        lines.append('                </section>')
        lines.append('')

    return '\n'.join(lines), min_year, max_year


def generate_articles_json(articles):
    """Build the articles.json structure."""
    # Collect unique topics from the topics arrays
    all_topics = set()
    for a in articles:
        all_topics.update(a['topics'])

    topics = sorted(all_topics)

    return {
        'articles': articles,
        'filters': {
            'topics': topics,
        },
        'stats': {
            'total': len(articles),
            'topic_count': len(topics),
        },
    }


def build_index_html(template_path, newsletter_html, min_year, max_year, output_path):
    """Read template, replace placeholders, write index.html."""
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    html = template.replace('<!-- NEWSLETTER_CONTENT -->', newsletter_html)
    html = html.replace('{{MIN_YEAR}}', str(min_year))
    html = html.replace('{{MAX_YEAR}}', str(max_year))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    print(f"Reading {XLSX_PATH}...")

    # Read data
    issues = read_issues(XLSX_PATH)
    print(f"  Issues: {len(issues)}")

    articles = read_articles(XLSX_PATH)
    print(f"  Articles: {len(articles)} (after dedup)")

    # Generate newsletter HTML
    newsletter_html, min_year, max_year = generate_newsletter_html(issues, LOAD_MORE_CUTOFF)
    print(f"  Year range: {min_year}-{max_year}")

    # Generate and write articles.json
    articles_data = generate_articles_json(articles)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {OUTPUT_JSON} ({articles_data['stats']['total']} articles, {articles_data['stats']['topic_count']} topics)")

    # Build and write index.html
    build_index_html(TEMPLATE_PATH, newsletter_html, min_year, max_year, OUTPUT_HTML)
    print(f"  Wrote {OUTPUT_HTML}")

    print("Done.")


if __name__ == '__main__':
    main()
