"""Detect annotation errors in disfluency marking."""

import pandas as pd
import re
from collections import defaultdict

# Configuration
LONG_TOKEN_THRESHOLD = 50
OUTPUT_FILE = 'outputs/results/annotation_errors.csv'

def extract_underscored_tokens(text):
    """Extract all tokens between underscores."""
    if pd.isna(text):
        return []
    return re.findall(r'_([^_]+)_', str(text))


def is_likely_error(token):
    """Check if token is likely an annotation error."""
    if len(token) > LONG_TOKEN_THRESHOLD:
        return True

    if any(punct in token[:-5] for punct in ['. ', '! ', '? ']):
        return True

    word_count = len(token.split())
    if word_count > 10:
        return True

    return False


def analyze_sample(row):
    """Analyze a sample for annotation errors."""
    errors = []
    sample_id = row['ID']

    en_tokens = extract_underscored_tokens(row['EN_disfluent'])
    en_token_lengths = [len(t) for t in en_tokens]

    lang_cols = [col for col in row.index if col.endswith('_disfluent') and col != 'EN_disfluent']

    for col in lang_cols:
        if pd.isna(row[col]):
            continue

        lang = col.replace('_disfluent', '')
        tokens = extract_underscored_tokens(row[col])

        for token in tokens:
            if is_likely_error(token):
                errors.append({
                    'Sample_ID': sample_id,
                    'Language': lang,
                    'Error_Type': 'Long_Token',
                    'Token_Length': len(token),
                    'Token_Preview': token[:100] + '...' if len(token) > 100 else token,
                    'Full_Token': token,
                    'Context': row[col][:200] + '...' if len(row[col]) > 200 else row[col]
                })

    return errors


def main():
    print("Loading dataset...")
    df = pd.read_csv('data/uh-mazing.csv')
    print(f"Loaded {len(df)} samples\n")

    print("Detecting annotation errors...")
    all_errors = []

    for idx, row in df.iterrows():
        errors = analyze_sample(row)
        all_errors.extend(errors)

    print(f"\nFound {len(all_errors)} potential annotation errors\n")

    errors_by_lang = defaultdict(int)
    for error in all_errors:
        errors_by_lang[error['Language']] += 1

    print("Errors by language:")
    for lang, count in sorted(errors_by_lang.items(), key=lambda x: x[1], reverse=True):
        print(f"  {lang}: {count} errors")

    if all_errors:
        errors_df = pd.DataFrame(all_errors)
        errors_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n✓ Saved detailed report to: {OUTPUT_FILE}")

        summary_df = errors_df.drop(columns=['Full_Token', 'Context'])
        summary_df.to_csv('outputs/results/annotation_errors_summary.csv', index=False)
        print(f"✓ Saved summary to: outputs/results/annotation_errors_summary.csv")

        print("\n=== EXAMPLES ===\n")
        for lang in ['CS', 'AR', 'ES'][:3]:
            lang_errors = errors_df[errors_df['Language'] == lang]
            if len(lang_errors) > 0:
                print(f"{lang} example:")
                example = lang_errors.iloc[0]
                print(f"  Sample: {example['Sample_ID']}")
                print(f"  Token length: {example['Token_Length']} chars")
                print(f"  Preview: {example['Token_Preview']}")
                print()
    else:
        print("No errors detected!")


if __name__ == '__main__':
    main()