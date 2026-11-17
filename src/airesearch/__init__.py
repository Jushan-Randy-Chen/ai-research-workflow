"""airesearch: small, explicit building blocks for hypothesis-driven ML research.

Modules (each is independent; import only what you need):
  config      typed experiment config from YAML + dotted CLI overrides
  seeding     one call to seed python/numpy/torch
  runs        run directories: atomic writes, resumable status, done markers
  provenance  what produced a result: git commit + diff hash, lockfile hash, environment, command, config hash
  stats       seeds-aware statistics: bootstrap CIs, paired differences, IQM
  figures     save a figure as PDF + PNG and return its sha256
  loop        the research loop with verification gates and human review (CLI: `research-loop`)
"""

__version__ = "0.1.0"
