# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Heston model sensitivities through a calibration
#
# Copyright (&copy;) 2023 Xcelerit Computing Limited.
#
# This file is part of QuantLibAAD, a Python wrapper for QuantLib enabled
# for risk computation using automatic differentiation. It uses XAD,
# a fast and comprehensive C++ library for automatic differentiation.
#
# QuantLibAAD and XAD are free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QuantLibAAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# QuantLib is free software: you can redistribute it and/or modify it under the
# terms of the QuantLib license.  You should have received a copy of the
# license along with this program; if not, please email
# <quantlib-dev@lists.sf.net>. The license is also available online at
# <https://www.quantlib.org/license.shtml>.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the license for more details.

# %% [markdown]
# This is a port of the `AdjointHestonModel` C++ example.  A Heston model is
# calibrated to 104 DAX option prices (the data of QuantLib's Heston model
# test, but fitted on prices rather than implied volatilities, so there is no
# implied-volatility solver to differentiate) and used to price a
# forward-start call.  The sensitivities of that price to all 114 market
# inputs (the spot, the nine zero rates, and the 104 volatilities) must
# account for the recalibration that a market move would trigger.
#
# Recording the whole calibration would take several gigabytes of tape, and
# bumping every input with a recalibration takes 114 calibrations.  Instead,
# the example uses the implicit function theorem: at the calibrated
# parameters $p$ the gradient of the calibration objective is zero, so
#
# $$ \frac{dV}{dm} = \left.\frac{dV}{dm}\right|_p - (H_{pp}^{-1} \frac{dV}{dp})^T H_{pm} $$
#
# where the Hessian blocks $H_{pp}$ and $H_{pm}$ of the objective come from
# central differences of its XAD gradient in $p$: 11 recordings give all 114
# sensitivities.  The largest ones are cross-checked at the end by bumping
# and recalibrating.

# %%
import QuantLibAAD as ql
from xad.adj_1st import Tape
from xad import value
import numpy as np
import pandas as pd
import time

# %% [markdown]
# ### Global parameters

# %%
todaysDate = ql.Date(5, ql.July, 2002)
ql.Settings.instance().evaluationDate = todaysDate
dayCounter = ql.Actual365Fixed()

# tight, so that bumping and recalibrating moves the parameters reliably;
# the implicit function theorem doesn't need it
tolerance = 1e-12

# QuantLib's order for the Heston parameters
parameterNames = ["theta", "kappa", "sigma", "rho", "v0"]

# setup and activate the tape
tape = Tape()
tape.activate()

# %%
interactive = "get_ipython" in globals()

# %% [markdown]
# ### Market data
#
# DAX data from A. Sepp, as in QuantLib's Heston model tests.  Every number
# here gets a sensitivity: the spot, one zero rate per curve date, and one
# volatility per (strike, expiry) pair, ordered by strike, then expiry.

# %%
curveDays = [13, 41, 75, 165, 256, 345, 524, 703]
curveRates = [0.0357, 0.0349, 0.0341, 0.0355, 0.0359, 0.0368, 0.0386, 0.0401]
curveDates = [todaysDate] + [todaysDate + n for n in curveDays]
zeroRates_in = [ql.Real(0.0357)] + [ql.Real(r) for r in curveRates]
expiries = [ql.Period(int((n + 3) / 7.0), ql.Weeks) for n in curveDays]
strikes = [3400, 3600, 3800, 4000, 4200, 4400, 4500,
           4600, 4800, 5000, 5200, 5400, 5600]
spot_in = ql.Real(4468.17)
vols_in = [ql.Real(v) for v in [
    0.6625, 0.4875, 0.4204, 0.3667, 0.3431, 0.3267, 0.3121, 0.3121, 0.6007, 0.4543,
    0.3967, 0.3511, 0.3279, 0.3154, 0.2984, 0.2921, 0.5084, 0.4221, 0.3718, 0.3327,
    0.3155, 0.3027, 0.2919, 0.2889, 0.4541, 0.3869, 0.3492, 0.3149, 0.2963, 0.2926,
    0.2819, 0.2800, 0.4060, 0.3607, 0.3330, 0.2999, 0.2887, 0.2811, 0.2751, 0.2775,
    0.3726, 0.3396, 0.3108, 0.2781, 0.2788, 0.2722, 0.2661, 0.2686, 0.3550, 0.3277,
    0.3012, 0.2781, 0.2781, 0.2661, 0.2661, 0.2681, 0.3428, 0.3209, 0.2958, 0.2740,
    0.2688, 0.2627, 0.2580, 0.2620, 0.3302, 0.3062, 0.2799, 0.2631, 0.2573, 0.2533,
    0.2504, 0.2544, 0.3343, 0.2959, 0.2705, 0.2540, 0.2504, 0.2464, 0.2448, 0.2462,
    0.3460, 0.2845, 0.2624, 0.2463, 0.2425, 0.2385, 0.2373, 0.2422, 0.3857, 0.2860,
    0.2578, 0.2399, 0.2357, 0.2327, 0.2312, 0.2351, 0.3976, 0.2860, 0.2607, 0.2356,
    0.2297, 0.2268, 0.2241, 0.2320,
]]

inputNames = (
    ["spot"]
    + [f"zero rate {(d - todaysDate)}d" for d in curveDates]
    + [f"vol {strike} {expiry}" for strike in strikes for expiry in expiries]
)


# %% [markdown]
# ### Building the calibration
#
# Everything that stays fixed while the market moves is shared; the curves
# and the calibration instruments are rebuilt from the market data each time.


# %%
def buildMarket(spot, zeroRates, vols):
    spotHandle = ql.QuoteHandle(ql.SimpleQuote(spot))
    rateTS = ql.YieldTermStructureHandle(ql.ZeroCurve(curveDates, zeroRates, dayCounter))
    dividendTS = ql.YieldTermStructureHandle(ql.FlatForward(todaysDate, 0.0, dayCounter))
    helpers = []
    for i, strike in enumerate(strikes):
        for j, expiry in enumerate(expiries):
            helpers.append(
                ql.HestonModelHelper(
                    expiry,
                    ql.TARGET(),
                    spot,
                    float(strike),
                    ql.QuoteHandle(ql.SimpleQuote(vols[i * len(expiries) + j])),
                    rateTS,
                    dividendTS,
                    ql.BlackCalibrationHelper.PriceError,
                )
            )
    return spotHandle, rateTS, dividendTS, helpers


# %%
def makeModel(parameters, spotHandle, rateTS, dividendTS, helpers):
    # QuantLib's parameter order is theta, kappa, sigma, rho, v0
    process = ql.HestonProcess(
        rateTS, dividendTS, spotHandle,
        parameters[4], parameters[1], parameters[0], parameters[2], parameters[3],
    )
    model = ql.HestonModel(process)
    engine = ql.COSHestonEngine(model, 12, 75)
    for helper in helpers:
        helper.setPricingEngine(engine)
    return model


# %%
def calibrate(spot, zeroRates, vols, start):
    spotHandle, rateTS, dividendTS, helpers = buildMarket(spot, zeroRates, vols)
    model = makeModel(start, spotHandle, rateTS, dividendTS, helpers)
    optimizer = ql.LevenbergMarquardt(tolerance, tolerance, tolerance)
    model.calibrate(
        helpers, optimizer, ql.EndCriteria(1000, 100, tolerance, tolerance, tolerance)
    )
    # the implicit function theorem and the bumped sensitivities both need
    # the optimum
    if model.endCriteria() == ql.EndCriteria.MaxIterations:
        raise RuntimeError("calibration did not converge")
    return [value(p) for p in model.params()]


# %% [markdown]
# ### The forward-start option
#
# The strike is set at the money in 6 months and the option expires in 18
# months; the payoff's strike is a placeholder, the engine uses the
# moneyness.


# %%
def priceForwardStart(parameters, spotHandle, rateTS, dividendTS):
    process = ql.HestonProcess(
        rateTS, dividendTS, spotHandle,
        parameters[4], parameters[1], parameters[0], parameters[2], parameters[3],
    )
    option = ql.ForwardVanillaOption(
        1.0,
        todaysDate + ql.Period(6, ql.Months),
        ql.PlainVanillaPayoff(ql.Option.Call, 0.0),
        ql.EuropeanExercise(todaysDate + ql.Period(18, ql.Months)),
    )
    option.setPricingEngine(ql.AnalyticHestonForwardEuropeanEngine(process))
    return option.NPV()


# %% [markdown]
# ### Calibration and pricing (without sensitivities)

# %%
startTime = time.time()
parameters = calibrate(
    value(spot_in),
    [value(r) for r in zeroRates_in],
    [value(v) for v in vols_in],
    [ql.Real(x) for x in [0.1, 1.0, 0.5, -0.5, 0.1]],
)
calibrationSeconds = time.time() - startTime

# %%
spotHandle, rateTS, dividendTS, helpers = buildMarket(spot_in, zeroRates_in, vols_in)
forwardValue = priceForwardStart(
    [ql.Real(p) for p in parameters], spotHandle, rateTS, dividendTS
)

# %%
print(
    f"Heston model calibrated to {len(vols_in)} DAX option prices "
    f"in {calibrationSeconds:.2f} s:"
)
print("  " + "  ".join(f"{name} {p:.4f}" for name, p in zip(parameterNames, parameters)))
print(
    "Forward-start call, strike set in 6 months, expiry in 18 months: "
    f"{value(forwardValue):.2f}"
)

# %% [markdown]
# ### Gradients
#
# One function gives the gradient of a pricing or objective function with
# respect to both the parameters and the market inputs, from a single
# recording.  The market is rebuilt inside the recording from fresh inputs
# each time, and the tape is cleared between recordings.


# %%
def gradient(f, parameters, spot, zeroRates, vols):
    tape.clearAll()
    p_in = [ql.Real(p) for p in parameters]
    spot_in_ = ql.Real(spot)
    rates_in_ = [ql.Real(r) for r in zeroRates]
    vols_in_ = [ql.Real(v) for v in vols]
    for p in p_in:
        tape.registerInput(p)
    tape.registerInput(spot_in_)
    tape.registerInputs(rates_in_)
    tape.registerInputs(vols_in_)
    tape.newRecording()

    y = f(p_in, spot_in_, rates_in_, vols_in_)

    tape.registerOutput(y)
    y.derivative = 1.0
    tape.computeAdjoints()

    dp = [p.derivative for p in p_in]
    dm = [spot_in_.derivative] + [r.derivative for r in rates_in_] + [v.derivative for v in vols_in_]
    return dp, dm


# %%
def objective(parameters, spot, zeroRates, vols):
    # the sum of squared calibration errors, which calibrate() minimizes
    spotHandle, rateTS, dividendTS, helpers = buildMarket(spot, zeroRates, vols)
    makeModel(parameters, spotHandle, rateTS, dividendTS, helpers)
    f = ql.Real(0.0)
    for helper in helpers:
        error = helper.calibrationError()
        f = f + error * error
    return f


# %%
def target(parameters, spot, zeroRates, vols):
    spotHandle, rateTS, dividendTS, helpers = buildMarket(spot, zeroRates, vols)
    return priceForwardStart(parameters, spotHandle, rateTS, dividendTS)


# %% [markdown]
# ### Sensitivities with the implicit function theorem
#
# The Hessian blocks of the objective come from central differences of its
# gradient in the parameters; then one more recording gives $dV/dp$ and the
# direct $dV/dm$ with the parameters held fixed.

# %%
marketValues = (
    value(spot_in),
    [value(r) for r in zeroRates_in],
    [value(v) for v in vols_in],
)

# %%
startTime = time.time()
nParams = len(parameters)
nInputs = len(inputNames)
Hpp = np.zeros((nParams, nParams))
Hmp = np.zeros((nInputs, nParams))
for k in range(nParams):
    h = 1e-4 * max(abs(parameters[k]), 0.01)
    up = list(parameters)
    up[k] += h
    down = list(parameters)
    down[k] -= h
    dpUp, dmUp = gradient(objective, up, *marketValues)
    dpDown, dmDown = gradient(objective, down, *marketValues)
    Hpp[:, k] = [(a - b) / (2.0 * h) for a, b in zip(dpUp, dpDown)]
    Hmp[:, k] = [(a - b) / (2.0 * h) for a, b in zip(dmUp, dmDown)]

# %%
dVdp, dVdm = gradient(target, parameters, *marketValues)
lam = np.linalg.solve(Hpp, np.array(dVdp))
sensitivities = np.array(dVdm) - Hmp @ lam
iftSeconds = time.time() - startTime

# %%
print(
    f"Sensitivities to all {nInputs} market inputs with the implicit "
    f"function theorem: {iftSeconds:.2f} s"
)

# %%
order = np.argsort(-np.abs(sensitivities))
top = pd.DataFrame(
    [(inputNames[i], sensitivities[i]) for i in order[:10]],
    columns=["Input", "Sensitivity"],
)
top.style.hide(axis="index")

# %%
if not interactive:
    print(top.to_string(index=False))

# %% [markdown]
# ### Cross-check by bumping and recalibrating
#
# The largest sensitivities are checked by bumping the input, recalibrating
# from the calibrated parameters, and repricing.

# %%
def bumpAndRecalibrate(indices):
    base = value(forwardValue)
    results = []
    for i in indices:
        spot = value(spot_in)
        zeroRates = [value(r) for r in zeroRates_in]
        vols = [value(v) for v in vols_in]
        if i == 0:
            spot += 1.0
            h = 1.0
        elif i <= len(zeroRates_in):
            zeroRates[i - 1] += 1e-4
            h = 1e-4
        else:
            vols[i - 1 - len(zeroRates_in)] += 1e-4
            h = 1e-4
        bumpedParameters = calibrate(spot, zeroRates, vols, [ql.Real(p) for p in parameters])
        spotHandle, rateTS, dividendTS, helpers = buildMarket(
            ql.Real(spot), [ql.Real(r) for r in zeroRates], [ql.Real(v) for v in vols]
        )
        bumped = priceForwardStart(
            [ql.Real(p) for p in bumpedParameters], spotHandle, rateTS, dividendTS
        )
        results.append((value(bumped) - base) / h)
    return results


# %%
checkIndices = [int(i) for i in order[:8]]
bumped = bumpAndRecalibrate(checkIndices)
checks = pd.DataFrame(
    [
        (inputNames[i], sensitivities[i], fd)
        for i, fd in zip(checkIndices, bumped)
    ],
    columns=["Input", "Implicit function theorem", "Bump and recalibrate"],
)
checks.style.hide(axis="index")

# %%
if not interactive:
    print(checks.to_string(index=False))

# %%
tape.deactivate()
