# ChangeLog

This log is to be read in conjunction with [ChangeLog.txt](./ChangeLog.txt). 
It lists the QuantLibAAD (formerly QuantLib-Risks) specific changes on top of what is already listed in 
the underlying QuantLib-SWIG changelog.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed

- The `QuantLib-Risks` alias package is no longer built: `QuantLib-Risks` 1.44.0 stays on PyPI as
  its last release; install `QuantLibAAD` instead

### Added

- Colab notebooks in `notebooks/`: option Greeks and curve risk in one adjoint sweep
- Example `scaling-adjoint.py`: cost of all sensitivities of an option book with AAD and with
  bumping as the volatility surface grows
- Example `trade-risk.py`: sensitivities of every swap in a book to every curve quote with AAD


## [1.44.0] - 2026-11-12

First release as QuantLibAAD.

- Renamed QuantLib-Risks -> QuantLibAAD: `pip install QuantLibAAD`, `import QuantLibAAD`
- `QuantLib-Risks` 1.44.0 is a deprecated shim (`shim/`) that requires `QuantLibAAD==1.44.*` and
  re-exports it as `QuantLib_Risks` with a `DeprecationWarning`
- Anyone pinned to `QuantLib-Risks==1.33.3` must also pin `xad<2`
- Matches QuantLib and QuantLib Python bindings version 1.44, with C++ QuantLibAAD (formerly
  QuantLib-Risks-Cpp)
- Removed from the Python API with QuantLib-SWIG 1.42 to 1.44, as in the C++ library:
  `SpreadOption` and `KirkSpreadOptionEngine`; `SubPeriodsCoupon`, `SubPeriodsLeg`,
  `SubPeriodsPricer`, `CompoundingRatePricer` and `AveragingRatePricer`; `DatedOISRateHelper`;
  the history functions of `IndexManager` (`setHistory`, `getHistory`, `hasHistory`,
  `clearHistory`, `hasHistoricalFixing`); `AnalyticHestonEngine_Integration` (now
  `FourierIntegration`); `InflationTermStructure.observationLag` and `hasExplicitBaseDate`; the
  YoY inflation index and curve constructors taking an `interpolated` flag;
  `DiscountingSwapEngine(curve, settlementDate, npvDate)` (pass `includeSettlementDateFlows`
  first, or use keywords). The constructor of `GlobalLinearSimpleZeroCurve` no longer takes
  keyword arguments.
- Builds QuantLib 1.44 with two temporary fixes, kept in `patches/quantlib/`, applied at build
  time to a copy of the QuantLib source and dropped with QuantLib 1.45:
  - QuantLib compiles with automatic-differentiation number types, a fix from QuantLib's main
    branch ([QuantLib #2934](https://github.com/lballabio/QuantLib/pull/2934))
  - an implied rate keeps its derivative when the compound factor is 1, so for example the
    dividend rho at a zero dividend yield is no longer lost, as proposed in
    [QuantLib #3057](https://github.com/lballabio/QuantLib/pull/3057); with a compound factor
    of 1 and a positive time, `SimpleThenCompounded` and `CompoundedThenSimple` now throw, as
    they do on QuantLib's main branch
- Builds against the shared libxad of the installed xad 2.2 package (`xad>=2.2,<2.3`), which is
  not bundled; tapes are shared with xad through libxad, thread-local per Python thread
- QuantLib and the module are built with no FMA contraction (`-ffp-contract=off` with GCC and
  Clang), so AD values match a plain-double build with the same setting
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


[Unreleased]: https://github.com/auto-differentiation/QuantLibAAD-Py/compare/v1.44.0...HEAD
[1.44.0]: https://github.com/auto-differentiation/QuantLibAAD-Py/compare/v1.33.3...v1.44.0

[1.33.3]: https://github.com/auto-differentiation/QuantLib-Risks-Py/compare/v1.33.2...v1.33.3

[1.33.2]: https://github.com/auto-differentiation/QuantLib-Risks-Py/compare/v1.33...v1.33.2

[1.33]: https://github.com/auto-differentiation/QuantLib-Risks-Py/releases/tag/v1.33
