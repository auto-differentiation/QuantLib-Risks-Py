# QuantLib-Risks is now QuantLibAAD

This package has been renamed to [QuantLibAAD](https://pypi.org/project/QuantLibAAD).
`QuantLib-Risks` 1.44 only installs `QuantLibAAD` and keeps `import QuantLib_Risks`
working, with a `DeprecationWarning`. Please switch to:

```bash
pip install QuantLibAAD
```

```python
import QuantLibAAD as ql
```

Anyone pinned to `QuantLib-Risks==1.33.3` must also pin `xad<2`.
