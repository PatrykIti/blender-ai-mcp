# 169. Reference-guided correction focus

Date: 2026-03-30

## Summary

Specialized the reference-guided checkpoint output so iterative modeling work
gets a tighter correction-oriented payload instead of only loose mismatch
lists.

## What Changed

- added `correction_focus` to the bounded vision result contract
- tightened prompt semantics for checkpoint-vs-reference compare modes so the
  backend ranks the most important mismatch targets first
- parser now backfills `correction_focus` from
  `shape_mismatches` / `proportion_mismatches` / `next_corrections` when the
  request is a reference-guided checkpoint comparison
- parser now prunes obviously unhelpful unchanged-fact items from
  correction-oriented lists and bounds those lists to a small usable set

## Why

The earlier contract could describe mismatches, but it still left too much
guesswork around priority. For iterative creature/reference work, the next
model step needs a short ranked focus set rather than only a longer unordered
summary.
