"""Extract and visualize the most common disfluency tokens per language."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import re
from collections import Counter
import os

# Configuration
TOP_N = 15
OUTPUT_DIR = 'outputs/figures'
CASE_SENSITIVE = False

def extract_underscored_tokens(text):
    """Extract tokens between underscores."""
    if pd.isna(text):
        return []

    tokens = re.findall(r'_([^_]+)_', str(text))

    if not CASE_SENSITIVE:
        tokens = [t.lower() for t in tokens]

    return tokens


def get_font_properties(lang):
    """Get font properties for special scripts."""
    font_paths = {
        'ZH': os.path.expanduser('~/.local/share/fonts/noto/NotoSansCJKsc-Regular.otf'),
        'HI': os.path.expanduser('~/.local/share/fonts/noto/NotoSansDevanagari-Regular.ttf'),
        'AR': os.path.expanduser('~/.local/share/fonts/noto/NotoSansArabic-Regular.ttf'),
    }

    if lang in font_paths and os.path.exists(font_paths[lang]):
        return fm.FontProperties(fname=font_paths[lang])
    else:
        return fm.FontProperties()


def configure_fonts_for_language(lang):
    """Configure fonts for special scripts."""
    font_config = {
        'ZH': ['Noto Sans CJK SC', 'Noto Sans CJK TC', 'SimHei', 'Microsoft YaHei'],
        'HI': ['Noto Sans Devanagari', 'Mangal', 'Noto Sans'],
        'AR': ['Noto Sans Arabic', 'Arial', 'DejaVu Sans'],
    }

    if lang in font_config:
        plt.rcParams['font.sans-serif'] = font_config[lang] + ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    else:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = True


def analyze_disfluencies_per_language(df):
    """Extract and count disfluency tokens per language."""
    disfluent_cols = [col for col in df.columns if col.endswith('_disfluent')]

    language_disfluencies = {}

    for col in disfluent_cols:
        lang = col.replace('_disfluent', '')

        all_tokens = []
        for text in df[col].dropna():
            tokens = extract_underscored_tokens(text)
            all_tokens.extend(tokens)

        token_counts = Counter(all_tokens)
        language_disfluencies[lang] = token_counts

        print(f"{lang}: {len(all_tokens)} total tokens, {len(token_counts)} unique")

    return language_disfluencies


def create_disfluency_chart(lang, token_counts, top_n=TOP_N):
    """Create bar chart of top disfluency tokens."""
    configure_fonts_for_language(lang)

    top_tokens = token_counts.most_common(top_n)

    if not top_tokens:
        print(f"No disfluencies found for {lang}")
        return

    tokens, counts = zip(*top_tokens)

    from matplotlib.colors import LinearSegmentedColormap
    colors_gradient = ['#ecf0f1', '#3498db', '#2980b9', '#1a5490']
    cmap = LinearSegmentedColormap.from_list('freq', colors_gradient, N=100)

    max_count = max(counts)
    norm_values = [c / max_count for c in counts]
    bar_colors = [cmap(val) for val in norm_values]

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(range(len(tokens)), counts, color=bar_colors, edgecolor='black', linewidth=1)

    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(bar.get_width() + max_count * 0.01, bar.get_y() + bar.get_height()/2,
                f'{count}', va='center', fontweight='bold', fontsize=10)

    font_prop = get_font_properties(lang)

    ax.set_yticks(range(len(tokens)))
    ax.set_yticklabels(tokens, fontsize=11, fontproperties=font_prop)
    ax.set_xlabel('Frequency', fontweight='bold', fontsize=12)
    ax.set_title(f'Top {top_n} Disfluency Tokens: {lang.upper()}',
                 fontweight='bold', fontsize=14, pad=15)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, f'disfluencies_{lang}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


def create_summary_comparison(language_disfluencies):
    """Create summary chart comparing disfluencies across languages."""
    langs = []
    unique_counts = []
    total_counts = []

    for lang, counter in sorted(language_disfluencies.items()):
        langs.append(lang)
        unique_counts.append(len(counter))
        total_counts.append(sum(counter.values()))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    from matplotlib.colors import LinearSegmentedColormap
    colors_gradient = ['#ecf0f1', '#e74c3c', '#c0392b', '#8b0000']
    cmap = LinearSegmentedColormap.from_list('total', colors_gradient, N=100)

    max_total = max(total_counts)
    norm_values = [c / max_total for c in total_counts]
    bar_colors = [cmap(val) for val in norm_values]

    bars1 = ax1.bar(langs, total_counts, color=bar_colors, edgecolor='black', linewidth=1)
    for bar, count in zip(bars1, total_counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_total * 0.01,
                 f'{count}', ha='center', va='bottom', fontweight='bold')

    ax1.set_xlabel('Language', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Total Tokens', fontweight='bold', fontsize=12)
    ax1.set_title('Total Disfluency Tokens per Language', fontweight='bold', fontsize=13)
    ax1.grid(axis='y', alpha=0.3)
    colors_gradient = ['#ecf0f1', '#9b59b6', '#8e44ad', '#6c3483']
    cmap = LinearSegmentedColormap.from_list('unique', colors_gradient, N=100)

    max_unique = max(unique_counts)
    norm_values = [c / max_unique for c in unique_counts]
    bar_colors = [cmap(val) for val in norm_values]

    bars2 = ax2.bar(langs, unique_counts, color=bar_colors, edgecolor='black', linewidth=1)
    for bar, count in zip(bars2, unique_counts):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_unique * 0.01,
                 f'{count}', ha='center', va='bottom', fontweight='bold')

    ax2.set_xlabel('Language', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Unique Types', fontweight='bold', fontsize=12)
    ax2.set_title('Unique Disfluency Types per Language', fontweight='bold', fontsize=13)
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'disfluencies_summary.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()


def save_token_frequencies(language_disfluencies):
    """Save token frequency tables to CSV."""
    for lang, counter in language_disfluencies.items():
        df = pd.DataFrame(counter.most_common(), columns=['Token', 'Frequency'])
        output_path = os.path.join('outputs/results', f'disfluency_tokens_{lang}.csv')
        df.to_csv(output_path, index=False)
        print(f"Saved: {output_path}")


def main():
    print("Loading dataset...")
    df = pd.read_csv('data/uh-mazing.csv')
    print(f"Loaded {len(df)} samples\n")

    print("Extracting disfluency tokens...")
    language_disfluencies = analyze_disfluencies_per_language(df)
    print()

    print(f"Creating charts (top {TOP_N} per language)...")
    for lang, token_counts in sorted(language_disfluencies.items()):
        create_disfluency_chart(lang, token_counts, top_n=TOP_N)
    print()

    print("Creating summary comparison...")
    create_summary_comparison(language_disfluencies)
    print()

    print("Saving token frequency tables...")
    save_token_frequencies(language_disfluencies)
    print()



if __name__ == '__main__':
    main()
