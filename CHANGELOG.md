# ChangeLog

This log is to be read in conjunction with [ChangeLog.txt](./ChangeLog.txt). 
It lists the QuantLibAAD (formerly QuantLib-Risks) specific changes on top of what is already listed in 
the underlying QuantLib-SWIG changelog.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.44.0] - Unreleased

- Matches QuantLib and QuantLib Python bindings version 1.44; features removed from QuantLib in
  1.42 to 1.44 are removed here too, and the constructor of `GlobalLinearSimpleZeroCurve` no
  longer takes keyword arguments (see the QuantLib-SWIG 1.42, 1.43 and 1.44 release notes)
- Builds QuantLib 1.44 with two temporary fixes from QuantLib's main branch, kept in
  `patches/quantlib/`, applied at build time and dropped with QuantLib 1.45:
  - QuantLib compiles with automatic-differentiation number types again
    ([QuantLib #2934](https://github.com/lballabio/QuantLib/pull/2934))
  - an implied rate keeps its derivative when the compound factor is 1, so for example the
    dividend rho at a zero dividend yield is no longer lost
    ([QuantLib #3057](https://github.com/lballabio/QuantLib/pull/3057))
- Builds against the shared libxad of the installed xad 2.2 package (`xad>=2.2,<2.3`)

## [1.41.0] - Unreleased

- Renamed QuantLib-Risks -> QuantLibAAD: `pip install QuantLibAAD`, `import QuantLibAAD`
- `QuantLib-Risks` 1.41.0 is a deprecated shim (`shim/`) that requires `QuantLibAAD==1.41.*` and
  re-exports it as `QuantLib_Risks` with a `DeprecationWarning`
- Anyone pinned to `QuantLib-Risks==1.33.3` must also pin `xad<2`
- Matches QuantLib and QuantLib Python bindings version 1.41
- Builds against QuantLibAAD 1.41 (formerly QuantLib-Risks-Cpp) and the shared libxad of the installed xad 2.2 package (`xad>=2.2,<2.3`), which is not bundled
- Tapes are shared with xad through libxad, thread-local per Python thread
- Builds the unmodified QuantLib 1.41 release, no QuantLib patches
- One-step build with scikit-build-core; wheels for Python 3.10-3.14 on Linux, macOS and Windows
- `tools/sync-swig.sh` syncs `SWIG/` with a QuantLib-SWIG release, re-applying the XAD changes in `SWIG/patches/`

## [1.33.3] - 2024-04-04

- Builds against renamed xad-autodiff -> xad Python package
- Cleanup of repository

## [1.33.2] - 2024-03-29

- Renaming quantlib-risks -> QuantLib-Risks for consistency
- Fixing markdown annotations in examples
- otherwise technically identical

## [1.33] - 2024-03-25

Initial release, matching QuantLib Python bindings version 1.33


[1.44.0]: https://github.com/auto-differentiation/QuantLibAAD-Py/compare/v1.41.0...v1.44.0

[1.41.0]: https://github.com/auto-differentiation/QuantLibAAD-Py/compare/v1.33.3...v1.41.0

[1.33.3]: https://github.com/auto-differentiation/QuantLib-Risks-Py/compare/v1.33.2...v1.33.3

[1.33.2]: https://github.com/auto-differentiation/QuantLib-Risks-Py/compare/v1.33...v1.33.2

[1.33]: https://github.com/auto-differentiation/QuantLib-Risks-Py/releases/tag/v1.33
