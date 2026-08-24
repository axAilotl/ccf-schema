# CCF 0.2.0 Working Draft bundles

These generated manifests define the artifact boundary for four cumulative
level distributions and three independent semantic-pack distributions.

Level bundles are incremental:

```text
ccf-exchange-bundle-v1
  -> ccf-canonical-store-bundle-v1
  -> ccf-verified-archive-bundle-v1
  -> ccf-governed-archive-bundle-v1
```

The continuity, work, and agent bundles depend only on the Exchange bundle.
Their payload schemas are excluded from the Exchange, Canonical Store, and
Verified Archive manifests. Governed Archive remains the complete successor to
the 0.1.2 distribution.

Each artifact entry names its source package and raw SHA-256 digest. Run
`make rebuild` after changing schemas, registries, or draft documentation.

