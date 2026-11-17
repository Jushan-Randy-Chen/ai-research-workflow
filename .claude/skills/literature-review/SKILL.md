---
name: literature-review
description: Find, verify and organise the literature and reference code for the project - related work, baselines, benchmark numbers, citations. Use when adding a citation or baseline, writing related work, checking novelty of a claim, or when the user asks "what has been done on X".
---

# Literature review

1. **Search** with several queries at once (WebSearch): the method's mechanism, the task/benchmark, the baselines'
   names, "<benchmark> leaderboard / results". Prefer venues: NeurIPS, ICML, ICLR, CVPR/ICCV/ECCV, ACL/EMNLP, CoRL,
   RSS, TMLR, JMLR; arXiv for very recent work (flag as preprint).
2. **Verify every source** by opening its page (OpenReview, PMLR, NeurIPS proceedings, CVF, ACL Anthology, arXiv):
   exact title, authors, venue, year, and that it says what we will cite it for. Never cite from memory; an entry you
   could not open is marked unverified and not used in the paper.
3. **Record**: a bib entry in references/refs.bib (published version preferred), a row in references/INDEX.md (what we
   take from it, code URL @ commit if any, verification date).
4. **Map the field** for related work: group papers by the question they answer, and state precisely how our claim
   differs from the closest two or three (setting, assumption, mechanism, result). Flag any paper that already makes
   our claim; tell the user immediately.
5. Pull reported numbers for `cross-validate-results` with table/figure references.
