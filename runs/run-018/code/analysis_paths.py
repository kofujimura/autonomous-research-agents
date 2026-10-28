"""Explicit canonical analyses; legacy outputs remain available as controls."""
import json
from pathlib import Path

DEFAULTS=dict(primary_features='analysis/features',primary_predictions='analysis/main',
 primary_summary='analysis/primary-summary',recent_features='analysis/recent-features',
 recent_predictions='analysis/recent',recent_summary='analysis/recent-summary',
 hgb_predictions='analysis/controls/hgb',hgb_summary='analysis/controls/hgb-summary',
 polygon_features='analysis/polygon-features')

def paths(root):
 root=Path(root);manifest=root/'manifest.json'
 return DEFAULTS | (json.loads(manifest.read_text()).get('analysis_paths',{}) if manifest.exists() else {})
