"""Render completed main/secondary and exploratory comparisons together."""
from record import ROOT
from figures import generate
from diagnostic_figures import generate_diagnostics
from presentation import display_tables
from input_figures import generate_inputs

if __name__=='__main__':
    generate(ROOT/'analysis/main-v1',ROOT/'analysis/secondary-v2',ROOT/'figures',overwrite=True)
    generate_diagnostics(ROOT/'analysis/robustness-paired-v12',ROOT/'analysis/secondary-v2',ROOT/'figures/diagnostics')
    display_tables(ROOT/'analysis/main-v1',ROOT/'analysis/secondary-v2',ROOT/'analysis/nlcd-v4',ROOT/'analysis/native-v5',ROOT/'tables',overwrite=True)
    generate_inputs(ROOT/'analysis/direct-inputs-v23',ROOT/'analysis/nlcd-direct-inputs-v23',ROOT/'figures')
