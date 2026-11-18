"""Fail closed if the repository is missing mandatory published release assets.

Do not use --candidate-only when declaring a student release ready.
"""
import argparse,json,sys
from pathlib import Path
from data_io import ROOT,records,digest
from validate_assets import check

REQUIRED=[
 'data/public_locked/c4_calibration_locked.jsonl.gz',
 'data/public_locked/c4_development_locked.jsonl.gz',
 'data/public_locked/c4_validation_windows_locked.jsonl.gz',
 'data/public_locked/wikitext2_test_windows_locked.jsonl.gz',
 'data/public_locked/hellaswag_val_locked.jsonl.gz',
 'data/public_locked/gsm8k_train_locked.jsonl.gz',
 'data/public_locked/gsm8k_test_locked.jsonl.gz',
 'data/prefix_banks/prefix_banks_locked.jsonl.gz',
 'data/release_provenance.json',
 'data/release_certification.json',
]

def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate-only',action='store_true');a=p.parse_args()
 check()
 if a.candidate_only:
  print('CANDIDATE ASSETS VALID: this is NOT a complete student release');return
 missing=[p for p in REQUIRED if not (ROOT/p).is_file()]
 if missing:
  print('\nNOT RELEASE READY. Missing required files:')
  for p in missing:print(' -',p)
  sys.exit(2)
 provenance=json.load(open(ROOT/'data/release_provenance.json'))
 for k in ['c4','wikitext','hellaswag','gsm8k','model_base','model_target','model_draft']:
  value=provenance.get('revisions',{}).get(k,'')
  if len(value)<40:raise SystemExit(f'Missing immutable revision for {k}')
 certificate=json.load(open(ROOT/'data/release_certification.json'))
 for key in ['mqar_dense_gate_passed','kv_full_cache_gate_passed','token_lengths_audited','prefix_distribution_checked']:
  if certificate.get(key) is not True:raise SystemExit(f'Missing staff signoff: {key}')
 for p in REQUIRED[:8]:
  n=sum(1 for _ in records(ROOT/p))
  if n==0:raise SystemExit(f'Empty release asset: {p}')
 print('RELEASE CANDIDATE COMPLETE: staff signoffs present; verify published checksums before shipping')
if __name__=='__main__':main()
