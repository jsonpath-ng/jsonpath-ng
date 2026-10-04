All notable changes to this project will be documented in this file.
Past changes are listed in [History.md](History.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Support Python 3.15.
- Add a `py.typed` marker.

### Fixed
- Ignore non-mapping values when updating named fields instead of raising `TypeError` (#104).
- `update()` with an in-place callback returning `None` no longer overwrites the field with `None` (#163)
- `Index.find` no longer raises `KeyError` when applied to a dict (e.g. `$.*[0]`
  where `*` matched a dict value); it now matches nothing, as the docstring
  promises ([#93](https://github.com/jsonpath-ng/jsonpath-ng/issues/93))
- Fix extended parser handling of field names that start with `true` or `false`.
- Stop serializing `Child` paths with surrounding parentheses. (#215)
- Avoid mutating dictionaries while evaluating extended filter expressions.
- Fix broken `Slice` serialization behavior.

  Previously, a slice like `[0:]` would serialize to `[]`,
  and a slice like `[::2]` would serialize to `[:2]`.

### Removed
- Drop support for Python 3.10.

## [1.8.0] - 2026-02-24

### Added
- Support Python 3.13 and 3.14
- Typing for IDE autocomplete
- Support for EMOJI and CJK Unicode
- Support for `DatumInContext` in-place updating
- Support equality checking of `Operation` instances
- Support string serialization of `Union` and `Intersect` instances
- Support comma-separated indices
- Add typings for IDE autocomplete

### Changed
- Rename `ExtentedJsonPathParser`
- Remove ply dependency

### Fixed
- Fix `False` and `None` values
- Fix single constant case
- Update field filter to resolve wildcard path issue
- Vendor copy of ply and remove pickle support from the vendored copy to resolve [CVE-2025-56005](https://nvd.nist.gov/vuln/detail/CVE-2025-56005)
- Fix string serialization throughout the library to enforce roundtrip parsing consistency.
  - Fields are more conservatively enclosed in quotion marks
    This fixes serialization and re-parsing of `"00"`, `'%'`, `'0@'` and `"&'"`.
  - `Operation` instances can now be serialized.
    This fixes serialization of `0-@` and `A -A`.
  - `SortedThis` instances can now be serialized and re-parsed.
    This fixes serialization of `0[/0]`.
  - `Child` precedence is now preserved using parentheses during serialization.
    This ensures that serialized strings like `a..b[c]` serialize and re-parse identically.
- Fix parsing and string serialization of numeric-only identifiers.
  This fixes parsing of `10`, which was parsed as two separate fields.
- Fix equality checks for `SortedThis` instances.
- Fix bool filter type to handle None values

### Removed
- Python 3.8 and 3.9 no longer supported

[Unreleased]: https://github.com/jsonpath-ng/jsonpath-ng/compare/v1.8.0...HEAD
[1.8.0]: https://github.com/jsonpath-ng/jsonpath-ng/compare/v1.7.0...v1.8.0
