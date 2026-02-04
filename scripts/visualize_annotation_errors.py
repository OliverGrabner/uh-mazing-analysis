"""Visualize annotation errors across languages."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
import re
import os

OUTPUT_DIR = 'outputs/figures'

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

    if 'EN' not in error_counts:
        error_counts['EN'] = 0

    languages = sorted(error_counts.keys())
    errors = [error_counts.get(lang, 0) for lang in languages]
    totals = [total_tokens.get(lang, 1) for lang in languages]
    error_rates = [(e / t * 100) if t > 0 else 0 for e, t in zip(errors, totals)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    colors_gradient = ['#ecf0f1', '#e74c3c', '#c0392b', '#8b0000']
    cmap = LinearSegmentedColormap.from_list('errors', colors_gradient, N=100)

    max_errors = max(errors)
    norm_values = [e / max_errors for e in errors]
    bar_colors = [cmap(val) for val in norm_values]

    bars1 = ax1.bar(languages, errors, color=bar_colors, edgecolor='black', linewidth=1)

    for bar, count in zip(bars1, errors):
        y_offset = max(bar.get_height() + max_errors * 0.01, max_errors * 0.02)
        ax1.text(bar.get_x() + bar.get_width()/2, y_offset,
                 f'{count}', ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax1.set_xlabel('Language', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Errors', fontweight='bold', fontsize=12)
    ax1.set_title('Annotation Errors by Language', fontweight='bold', fontsize=14, pad=15)
    ax1.grid(axis='y', alpha=0.3)

    en_idx = languages.index('EN')
    ax1.annotate('Gold Standard',
                 xy=(en_idx, 0), xytext=(en_idx, max_errors * 0.15),
                 ha='center', fontsize=9, style='italic', color='green',
                 arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
    colors_gradient = ['#ecf0f1', '#f39c12', '#e67e22', '#d35400']
    cmap = LinearSegmentedColormap.from_list('rate', colors_gradient, N=100)

    max_rate = max(error_rates)
    norm_values = [r / max_rate for r in error_rates]
    bar_colors = [cmap(val) for val in norm_values]

    bars2 = ax2.bar(languages, error_rates, color=bar_colors, edgecolor='black', linewidth=1)

    for bar, rate in zip(bars2, error_rates):
        y_offset = max(bar.get_height() + max_rate * 0.01, max_rate * 0.02)
        ax2.text(bar.get_x() + bar.get_width()/2, y_offset,
                 f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax2.set_xlabel('Language', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Error Rate (%)', fontweight='bold', fontsize=12)
    ax2.set_title('Error Rate by Language', fontweight='bold', fontsize=14, pad=15)
    ax2.grid(axis='y', alpha=0.3)

    en_idx = languages.index('EN')
    ax2.annotate('Gold Standard',
                 xy=(en_idx, 0), xytext=(en_idx, max_rate * 0.15),
                 ha='center', fontsize=9, style='italic', color='green',
                 arrowprops=dict(arrowstyle='->', color='green', lw=1.5))

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'annotation_errors_by_language.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

    fig, ax = plt.subplots(figsize=(14, 7))

    top_langs = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    colors = ['#e74c3c', '#3498db', '#2ecc71']

    for idx, (lang, _) in enumerate(top_langs):
        lang_errors = errors_df[errors_df['Language'] == lang]
        lengths = lang_errors['Token_Length'].values

        ax.hist(lengths, bins=20, alpha=0.6, label=f'{lang} (n={len(lengths)})',
                color=colors[idx], edgecolor='black', linewidth=0.5)

    ax.axvline(x=50, color='red', linestyle='--', linewidth=2, label='Threshold (50 chars)')

    ax.set_xlabel('Token Length', fontweight='bold', fontsize=12)
    ax.set_ylabel('Number of Errors', fontweight='bold', fontsize=12)
    ax.set_title('Error Token Lengths (Top 3 Languages)',
                 fontweight='bold', fontsize=14, pad=15)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'error_length_distribution.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

    print("\n=== SUMMARY ===\n")

    summary_data = []
    for lang in languages:
        summary_data.append({
            'Language': lang,
            'Errors': error_counts.get(lang, 0),
            'Total_Tokens': total_tokens.get(lang, 0),
            'Error_Rate_%': f"{(error_counts.get(lang, 0) / total_tokens.get(lang, 1) * 100):.2f}"
        })

    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('Errors', ascending=False)

    print(summary_df.to_string(index=False))
    print(f"\n✓ Total errors across all languages: {sum(errors)}")
    print(f"✓ Average error rate: {sum(error_rates)/len(error_rates):.2f}%")


if __name__ == '__main__':
    main()
