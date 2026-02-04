"""Bar chart of annotation errors by language."""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import re

def extract_underscored_tokens(text):
    """Extract all tokens between underscores."""
    if pd.isna(text):
        return []
    return re.findall(r'_([^_]+)_', str(text))


def main():
    errors_df = pd.read_csv('outputs/results/annotation_errors.csv')
    df = pd.read_csv('data/uh-mazing.csv')

    disfluent_cols = [col for col in df.columns if col.endswith('_disfluent')]
    total_tokens = {}
    for col in disfluent_cols:
        lang = col.replace('_disfluent', '')
        all_tokens = []
        for text in df[col].dropna():
            tokens = extract_underscored_tokens(text)
            all_tokens.extend(tokens)
        total_tokens[lang] = len(all_tokens)

    error_counts = errors_df['Language'].value_counts().to_dict()
    error_counts['EN'] = 0

    languages = sorted(error_counts.keys())
    errors = [error_counts.get(lang, 0) for lang in languages]

    colors_gradient = ['#2ecc71', '#ecf0f1', '#f39c12', '#e74c3c', '#c0392b']
    cmap = LinearSegmentedColormap.from_list('errors', colors_gradient, N=100)

    max_errors = max(errors) if max(errors) > 0 else 1
    norm_values = [e / max_errors for e in errors]
    bar_colors = [cmap(val) for val in norm_values]

    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.bar(languages, errors, color=bar_colors, edgecolor='black', linewidth=1.5)

    for bar, count, lang in zip(bars, errors, languages):
        y_offset = max(bar.get_height() + max_errors * 0.02, max_errors * 0.03)
        label_text = f'{count}'

        if lang == 'EN':
            ax.text(bar.get_x() + bar.get_width()/2, y_offset,
                   label_text, ha='center', va='bottom',
                   fontweight='bold', fontsize=12, color='green')
        else:
            ax.text(bar.get_x() + bar.get_width()/2, y_offset,
                   label_text, ha='center', va='bottom',
                   fontweight='bold', fontsize=12)

    en_idx = languages.index('EN')
    ax.annotate('Gold Standard',
                xy=(en_idx, 0), xytext=(en_idx, max_errors * 0.25),
                ha='center', fontsize=11, style='italic', color='darkgreen',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7),
                arrowprops=dict(arrowstyle='->', color='green', lw=2))

    ax.set_xlabel('Language', fontweight='bold', fontsize=14)
    ax.set_ylabel('Errors', fontweight='bold', fontsize=14)
    ax.set_title('Annotation Errors per Language',
                fontweight='bold', fontsize=16, pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_ylim(0, max_errors * 1.15)

    total_errors = sum(errors)
    summary_text = f'Total errors: {total_errors}\nMost errors: CS ({error_counts.get("CS", 0)})'
    ax.text(0.98, 0.97, summary_text, transform=ax.transAxes,
           fontsize=11, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig('outputs/figures/annotation_errors_simple.png', dpi=300, bbox_inches='tight')
    print('✓ Saved: outputs/figures/annotation_errors_simple.png')

    print('\n=== Summary ===\n')
    for lang in languages:
        err_count = error_counts.get(lang, 0)
        tot = total_tokens.get(lang, 0)
        rate = (err_count / tot * 100) if tot > 0 else 0
        marker = '✓' if err_count == 0 else '✗'
        print(f'{marker} {lang}: {err_count:3d} errors ({rate:5.2f}%)')


if __name__ == '__main__':
    main()
