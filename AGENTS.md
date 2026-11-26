# Repository instructions

- Use [BOOTSTRAP](BOOTSTRAP.md) and [OPTIMIZE](OPTIMIZE.md) for user-level maintenance. Test deployment in an isolated home first.
- Run the three [verification commands](README.md#verification). After changing the bundled Skills or registry, regenerate the lock and reference with `python tools/setup.py sync-reference`.
- Preserve the existing EWK CLI contract. Exercise failed writes, drift, and rollback when touching deployment.
- Keep private inventory and machine-local configuration outside Git. Follow [CONTRIBUTING](CONTRIBUTING.md) for public changes.
