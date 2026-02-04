"""Bar chart of annotation errors by language (sorted)."""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import re

# Load data
errors_df = pd.read_csv('outputs/results/annotation_errors.csv')
df = pd.read_csv('data/uh-mazing.csv')

total_tokens = {}
for col in df.columns:
    if col.endswith('_disfluent'):
        lang = col.replace('_disfluent', '')
        tokens = []
        for text in df[col].dropna():
            tokens.extend(re.findall(r'_([^_]+)_', str(text)))
        total_tokens[lang] = len(tokens)

error_counts = errors_df['Language'].value_counts().to_dict()
error_counts['EN'] = 0

data = []
for lang in total_tokens.keys():
    errors = error_counts.get(lang, 0)
    data.append({'Language': lang, 'Errors': errors})

data = sorted(data, key=lambda x: x['Errors'])
languages = [d['Language'] for d in data]
errors = [d['Errors'] for d in data]

cmap = LinearSegmentedColormap.from_list('error_gradient',
                                          ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c'], N=100)
norm_values = [err / max(errors) if max(errors) > 0 else 0 for err in errors]
colors = [cmap(val) for val in norm_values]

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(languages, errors, color=colors, edgecolor='black', linewidth=1)

for bar, count in zip(bars, errors):
    ax.text(bar.get_width() + max(errors) * 0.01, bar.get_y() + bar.get_height()/2,
            f'{count}', va='center', fontweight='bold', fontsize=10)

ax.set_xlabel('Errors', fontweight='bold', fontsize=12)
ax.set_ylabel('Language', fontweight='bold', fontsize=12)
ax.set_title('Annotation Errors (Best → Worst)', fontweight='bold', fontsize=14, pad=15)
ax.grid(axis='x', alpha=0.3)
ax.invert_yaxis()

plt.tight_layout()
plt.savefig('outputs/figures/error_count_simple.png', dpi=300, bbox_inches='tight')
print('✓ Saved: outputs/figures/error_count_simple.png')

print('\n=== Errors (Best to Worst) ===\n')
for lang, count in zip(languages, errors):
    print(f'{lang}: {count:3d} errors')
