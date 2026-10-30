# Preprint source

LaTeX source of *Letting AI Formulate the Research Question: Autonomous Research Agents*. This is the source of [arXiv:2610.39620v1](https://arxiv.org/abs/2610.39620v1); `main.pdf` is built from it, and its text is the same as the arXiv PDF apart from arXiv's margin stamp.

- `make_tables.py` generates `tables/*.tex` and `facts.json` from the run records (read only) and from the management records listed in its docstring. It was run against the original workspace; `facts.json` holds the values it used.
- Build: `pdflatex main && bibtex main && pdflatex main && pdflatex main`.
