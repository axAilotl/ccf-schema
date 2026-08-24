# Example CCF Capsule

This fixture is a partial, lossless Exchange Capsule for a small project
knowledge transfer. It contains:

- a `semantic.entity` root Record for the Cissa hardware project;
- an `experience.observation` design note;
- the exporting runtime Record;
- `ccf.part_of` membership Links;
- one external, one withheld, and one erased dependency;
- an L1-to-L3 uplift receipt that preserves every supplied ID and does not
  manufacture producer authentication;
- an illustrative L3-to-L1 lossy downgrade receipt that enumerates its omitted
  journal proof.

The `org.example.future_context` extension on the root is deliberately unknown
to CCF. Exchange implementations preserve it without activating it.

The object hashes in `uplift-receipt.json` demonstrate the receipt shape. The
fixture does not include the destination's canonical compartments, so those
hashes are not canonical test vectors. Canonical identity is tested separately
against the inherited 0.1.2 vectors by `check-canonical`.

