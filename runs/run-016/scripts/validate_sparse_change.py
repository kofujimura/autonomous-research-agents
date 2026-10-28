"""Exact rational enumeration validates the one-sided hypergeometric bound."""
import json,math
from fractions import Fraction
from pathlib import Path
from sparse_change_core import changed_count_upper,entropy_envelope
from records import ROOT,now

out=ROOT/'results/validation-sparse-change'
if out.exists():raise FileExistsError('Preserve original validation')
out.mkdir(parents=True);cases=0;maximum=Fraction(0)
for N in range(2,25):
    for n in range(1,N+1):
        upper=[changed_count_upper(N,n,x) for x in range(n+1)]
        for M in range(N+1):
            failure=Fraction(0)
            for x in range(max(0,n-(N-M)),min(n,M)+1):
                if M>upper[x]:failure+=Fraction(math.comb(M,x)*math.comb(N-M,n-x),math.comb(N,n))
            assert failure<=Fraction(1,20),(N,n,M,failure)
            maximum=max(maximum,failure);cases+=1
assert entropy_envelope(0.,17)==0
assert abs(float(entropy_envelope(1.,17))-math.log(17))<1e-12
result=dict(completed_at_utc=now(),population_sample_count_cases=cases,largest_exact_failure_probability=str(maximum),
            largest_failure_probability=float(maximum),required_upper_bound=.05,status='passed',
            scope='Small finite populations N=2..24, every sample size and true changed count; rational combinatorial probabilities, not independent reproduction')
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
