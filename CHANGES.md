## Changelog

### Release 0.1a2 (unreleased)

#### Bugs Fixed

- Ignore Ansible filters and tests with unqualified names.

- Use `isinstance(obj, collections.abc.Buffer)` rather than
  `isinstance(obj, collections.abc.ByteString)` when detecting
  non-flattenable iterables.

### Release 0.1a1 (2023-08-23)

First release.
