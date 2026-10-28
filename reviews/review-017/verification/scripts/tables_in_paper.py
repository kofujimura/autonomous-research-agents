"""Reviewer check: does each regenerated numeric table appear verbatim in paper.md (submitted tag)?
usage: tables_in_paper.py <tables_dir> <paper.md>"""
import sys, glob, os
paper = open(sys.argv[2]).read()
found = 0; rows = []
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.md'))):
    t = open(f).read().strip()
    # compare table body lines (skip header) to tolerate caption differences
    lines = [l for l in t.splitlines() if l.startswith('|')]
    ok_full = t in paper
    ok_lines = all(l in paper for l in lines)
    rows.append((os.path.basename(f), len(lines), ok_full, ok_lines)); found += ok_lines
for r in rows: print(*r)
print('tables', len(rows), 'all-lines-present', found)
