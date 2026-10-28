"""Audit paired city strata directly against saved cases and the land mask."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import TOL
from record import ROOT, now


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    directory = Path(args.directory)
    cases = pd.read_csv(directory / 'paired-cases.csv', dtype={'date': str})
    summary = pd.read_csv(directory / 'paired-width-summary.csv')
    land = pd.read_csv(ROOT / 'data/cities/land-mask/land-fractions.csv')
    land_flags = land.groupby('portfolio_index')['land_fraction'].min().ge(.5)
    common = cases['informative_snapshot'].eq(1) & cases['informative_maximum'].eq(1)
    all_land = cases['portfolio_index'].map(land_flags)
    assert all_land.notna().all()
    assert np.array_equal(cases['all_land_common_informative'], common & all_land)
    checks = []
    for _, row in summary.iterrows():
        selected = cases['matched_date_snapshot'] & cases['portfolio_type_snapshot'].eq(row['portfolio_type'])
        if row['model'] != 'all':
            selected &= cases['model'].eq(row['model'])
        if str(row['horizon']) != 'all':
            selected &= cases['horizon'].eq(int(row['horizon']))
        if row['stratum'] != 'all':
            selected &= common
        before_land = int(selected.sum())
        if row['stratum'] == 'all_land_common_informative':
            selected &= all_land
        part = cases.loc[selected]
        assert len(part) == int(row['cases']), row.to_dict()
        assert part['date'].nunique() == int(row['dates']), row.to_dict()
        delta = part[row['mode'] + '_width_maximum'] - part[row['mode'] + '_width_snapshot']
        actual = float(delta.mean())
        expected = row['maximum_minus_snapshot_width']
        assert (pd.isna(actual) and pd.isna(expected)) or abs(actual - expected) <= TOL, row.to_dict()
        checks.append({'portfolio_type': row['portfolio_type'], 'model': row['model'],
                       'horizon': str(row['horizon']), 'stratum': row['stratum'], 'mode': row['mode'],
                       'cases': len(part), 'cases_before_land_condition': before_land,
                       'land_condition_removed': before_land - len(part)})
    report = {'status': 'passed', 'observed_at_utc': now(), 'paired_rows': len(cases),
              'summary_rows_checked': len(checks), 'checks': checks,
              'scope': 'Direct counts and mean differences from saved cases; land flags recomputed from the bundled mask table. No new scientific comparison.'}
    Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}))


if __name__ == '__main__':
    main()
