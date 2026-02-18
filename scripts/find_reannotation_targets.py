"""Find all (ID, Language) pairs that need reannotation."""

import pandas as pd
import re
from collections import defaultdict

OUTPUT_FILE = 'outputs/results/reannotation_targets.csv'

def check_sample(row):
    """Check a row for annotation issues across all target languages."""
    results = []
    sample_id = row['ID']

    lang_cols = [col for col in row.index if col.endswith('_disfluent') and col != 'EN_disfluent']

    for col in lang_cols:
        if pd.isna(row[col]):
            continue

        text = str(row[col])
        lang = col.replace('_disfluent', '')
        reasons = []

        # Condition 1: any disfluency span has 10+ words
        tokens = re.findall(r'_([^_]+)_', text)
        for token in tokens:
            if len(token.split()) >= 10:
                reasons.append('long_disfluency')
                break

        # Condition 2: no underscore markers at all
        if '_' not in text:
            reasons.append('missing_underscores')

        if reasons:
            # Strip all underscores so reannotators start fresh
            clean_text = text.replace('_', '')
            results.append({
                'ID': sample_id,
                'Language': lang,
                'Reason': ';'.join(reasons),
                'EN_disfluent': row['EN_disfluent'],
                'Text': clean_text
            })

    return results


def main():
    print("Loading dataset...")
    df = pd.read_csv('data/uh-mazing.csv')
    print(f"Loaded {len(df)} samples\n")

    all_flags = []
    for _, row in df.iterrows():
        all_flags.extend(check_sample(row))

    # Deduplicate by (ID, Language) — shouldn't happen given logic, but just in case
    seen = set()
    deduped = []
    for flag in all_flags:
        key = (flag['ID'], flag['Language'])
        if key not in seen:
            seen.add(key)
            deduped.append(flag)

    print(f"Found {len(deduped)} (ID, Language) pairs needing reannotation\n")

    # Breakdown by language
    lang_counts = defaultdict(int)
    reason_counts = defaultdict(int)
    for flag in deduped:
        lang_counts[flag['Language']] += 1
        for r in flag['Reason'].split(';'):
            reason_counts[r] += 1

    print("By language:")
    for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {lang}: {count}")

    print("\nBy reason:")
    for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {reason}: {count}")

    # Save
    out_df = pd.DataFrame(deduped)
    out_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✓ Saved to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
