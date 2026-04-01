# 178. Current-view checkpoint compare unique filenames

Date: 2026-04-01

## Summary

Made `reference_compare_current_view(...)` write per-call unique checkpoint
filenames so concurrent or rapid back-to-back compares cannot collide on the
same staged image path.

## What Changed

- current-view checkpoint capture now appends a UUID fragment to
  `checkpoint_compare_<timestamp>...jpg`
- the stable `checkpoint_compare_latest.jpg` alias is still written for
  convenience
- added unit coverage proving the generated checkpoint path includes the unique
  suffix

## Why

Second-level timestamps were not enough to isolate concurrent compare requests.
Two calls started in the same second could overwrite the same checkpoint image
before vision consumed it, producing mismatched compare results.
