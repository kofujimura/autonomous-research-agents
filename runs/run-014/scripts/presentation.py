"""Display-only tables from prespecified analysis outputs; no new estimators."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from figures import markdown_table,LABELS,MODEL_LABELS

def display_tables(main,secondary,extension,native,output,overwrite=False):
    output.mkdir(parents=True,exist_ok=overwrite)
    m=pd.read_csv(main/'main-table.csv')
    p=pd.read_csv(main/'paired-comparisons.csv')
    primary=p[(p.availability_mode=='paired')&(p.support=='centre')&
              (p.seed==14014)&(p.reference_mode=='global')&
              p.method.isin(['concurrent','control_adjusted'])].copy()
    primary['interval']=[f'{a:.3f} to {b:.3f}' for a,b in zip(primary.delta_J_lo,primary.delta_J_hi)]
    primary['decisions']=[f'{int(c)}/{int(n)}' for c,n in zip(primary.changed_flags,primary.total_pairs)]
    primary['model']=primary.model.map(MODEL_LABELS);primary['method']=primary.method.map(LABELS)
    fmt={k:lambda v:'NA' if pd.isna(v) else f'{v:.3f}' for k in ['delta_J','delta_sensitivity','delta_false_positive_rate','sensitivity','false_positive_rate','J']}
    (output/'primary-contrasts.md').write_text(markdown_table(primary,{
        'model':'Representation','task':'Task','method':'Readout versus start-fixed',
        'delta_sensitivity':'Sensitivity difference','delta_false_positive_rate':'False-positive-rate difference',
        'delta_J':'J difference','interval':'Conditional 95% interval','decisions':'Changed flags / cases'},fmt))
    for name,methods in [('primary-operating-points',['start_fixed','concurrent','control_adjusted']),
                         ('learned-operating-points',['subsequent_reference_similarity','cosine_change','state_random_forest',
                           'subsequent_state_random_forest','subsequent_state_logistic','direct_gradient_boosting'])]:
        q=m[m.method.isin(methods)].copy()
        q['tp']=[f'{int(a)}/{int(b)}' for a,b in zip(q.true_positive,q.n_positive)]
        q['fp']=[f'{int(a)}/{int(b)}' for a,b in zip(q.false_positive,q.n_negative)]
        q['model']=q.model.map(MODEL_LABELS);q['method']=q.method.map(LABELS)
        (output/f'{name}.md').write_text(markdown_table(q,{'model':'Representation','task':'Task','method':'Readout',
            'tp':'True positives / positives','fp':'False positives / negatives','sensitivity':'Sensitivity',
            'false_positive_rate':'False-positive rate','J':'J'},fmt))
    s=pd.read_csv(main/'strata.csv')
    q=s[(s.availability_mode=='paired')&(s.support=='centre')&(s.seed==14014)&
        (s.reference_mode=='global')&s.method.isin(['start_fixed','concurrent','control_adjusted','subsequent_state_random_forest'])&
        s.stratum.isin(['2019','2020'])].copy()
    q['model']=q.model.map(MODEL_LABELS);q['method']=q.method.map(LABELS)
    (output/'calendar-strata.md').write_text(markdown_table(q,{'model':'Representation','task':'Task','method':'Readout',
        'stratum':'Before year','n_positive':'Positives','n_negative':'Negatives',
        'sensitivity':'Sensitivity','false_positive_rate':'False-positive rate'},fmt))
    e=pd.read_csv(extension/'metrics.csv')
    q=e[(e.support=='centre')&e.availability_mode.str.endswith('_primary')&
        e.method.isin(['start_fixed','concurrent','control_adjusted','subsequent_state_random_forest','subsequent_state_logistic'])].copy()
    q['horizon']=q.availability_mode.map({'nlcd_overlapping_2019_2021_primary':'2019–2021','nlcd_beyond_2021_primary':'2022–2023'})
    q['model']=q.model.map(MODEL_LABELS);q['method']=q.method.map(LABELS)
    (output/'nlcd-operating-points.md').write_text(markdown_table(q,{'model':'Representation','horizon':'Pair end years',
        'task':'Task','method':'Readout','n_positive':'Positives','n_negative':'Negatives',
        'sensitivity':'Sensitivity','false_positive_rate':'False-positive rate','J':'J'},fmt))
    n=pd.read_csv(native/'summary.csv');q=n[n.group=='overall'].copy()
    nf={k:lambda v:'NA' if pd.isna(v) else f'{v:.6f}' for k in ['minimum','q05','median','maximum']}
    (output/'native-summary.md').write_text(markdown_table(q,{'metric':'Co-location metric','n':'Valid pairs',
        'minimum':'Minimum','q05':'Fifth percentile','median':'Median','maximum':'Maximum'},nf))
    # Full machine-readable tables remain the authoritative values before display rounding.
    primary.to_csv(output/'primary-contrasts-display.csv',index=False)
    index=dict(inputs=[str(x) for x in [main,secondary,extension,native]],
               rounding='Once on display; three decimals for rates/differences, six for native diagnostics.',
               methods_selected='Explicit protocol-primary contrasts and fixed conditional-state comparators; full tables retain all methods.')
    (output/'index.json').write_text(json.dumps(index,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['main','secondary','extension','native','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();display_tables(a.main,a.secondary,a.extension,a.native,a.output)
