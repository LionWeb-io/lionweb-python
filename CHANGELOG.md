# Changelog

All notable changes to this project will be documented in this file.

## 0.4.3

### Changed

- Added `__all__` to the `lionweb.language`, `lionweb.model`, `lionweb.model.impl`,
  `lionweb.self`, `lionweb.presentation`, `lionweb.utils`, `lionweb.serialization`
  and `lionweb.generation` packages to explicitly control their public API.
- Replaced generic `RuntimeError`/`ValueError` usages with more specific exception
  types where it improves clarity and lets callers handle failures precisely:
  - `lionweb.serialization.classifier_resolver.UnresolvedClassifierError` is now
    raised by `ClassifierResolver` when a classifier, concept, or annotation
    cannot be resolved from a `MetaPointer`.
  - `lionweb.utils.language_validator.InvalidLanguageError` is now raised by
    `LanguageValidator.ensure_is_valid` when a `Language` fails validation,
    carrying the offending language and its `ValidationResult`.
- Rewrote the `isinstance`-chain in `LanguageValidator.check_ancestors_helper`
  using `match`/`case` pattern matching for clarity.
- Added Google-style docstrings (with typed `Args`/`Returns`/`Raises` sections)
  to `ClassifierResolver` and `LanguageValidator`.
- Tightened type hints (e.g. `Sequence[object]`, forward-referenced `Concept`/
  `Annotation` dictionaries) in `ClassifierResolver` and `LanguageValidator`.

### Removed

- Removed `ROADMAP.md`; the items it tracked have been addressed.
