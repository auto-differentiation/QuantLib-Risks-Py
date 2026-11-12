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
# # Trade-level risk of a swap book
#
# Copyright (&copy;) 2026 Xcelerit Computing Limited.
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
# We compute the sensitivities of every swap in a book of 200 to every one of
# the 45 quotes of the curve they are priced on, with adjoint algorithmic
# differentiation (AAD).
#
# The curve is recorded once: its node zero rates and their Jacobian to the 45
# quotes come from one recording of the bootstrap and one adjoint sweep per
# node. Each swap is then priced off a zero curve through those nodes, which
# reproduces the bootstrapped curve, with a small recording of its own; the
# chain rule maps its node sensitivities to the quotes.
#
# The results are checked against a recording of the whole book together with
# the bootstrap, and against central differences, and the run time is compared
# with bumping each quote.

# %%
import math
import time
from collections import namedtuple

import QuantLibAAD as ql
from xad.adj_1st import Tape

# %% [markdown]
# ### Market data
#
# Deposits (ON, TN, SN, 1W, 1M to 6M), FRAs (1x7 to 5x11) and swaps (1Y to 30Y).

# %%
DEPOSITS, FRAS, SWAPS = 10, 5, 30
today = ql.Date(2, ql.January, 2015)
calendar = ql.TARGET()


def market_quotes():
    return ([0.0010 + i * 0.0002 for i in range(DEPOSITS)]
            + [0.0030 + i * 0.0005 for i in range(FRAS)]
            + [0.0060 + i * 0.0001 for i in range(SWAPS)])


def quote_names():
    names = ["deposit ON", "deposit TN", "deposit SN", "deposit 1W"]
    names += [f"deposit {i}M" for i in range(1, DEPOSITS - 3)]
    names += [f"FRA {i}x{i + 6}" for i in range(1, FRAS + 1)]
    names += [f"swap {i}Y" for i in range(1, SWAPS + 1)]
    return names


# %% [markdown]
# ### The curve
#
# A `PiecewiseLinearZero` curve bootstrapped on the quotes. AAD differentiates
# the bootstrap's solver iterations, so its sensitivities are only as accurate
# as the solver: we tighten the accuracy well below the default.

# %%
def bootstrap(quotes):
    helpers = []
    for i in range(DEPOSITS):
        tenor = ql.Period(1, ql.Days) if i < 3 else (
            ql.Period(1, ql.Weeks) if i == 3 else ql.Period(i - 3, ql.Months))
        fixing_days = i if i < 2 else 2
        helpers.append(ql.DepositRateHelper(
            ql.QuoteHandle(quotes[i]), tenor, fixing_days, calendar,
            ql.ModifiedFollowing, False, ql.Actual360()))
    for i in range(FRAS):
        helpers.append(ql.FraRateHelper(
            ql.QuoteHandle(quotes[DEPOSITS + i]), i + 1, i + 7, 2, calendar,
            ql.ModifiedFollowing, False, ql.Actual360()))
    euribor6m = ql.Euribor6M()
    for i in range(SWAPS):
        helpers.append(ql.SwapRateHelper(
            ql.QuoteHandle(quotes[DEPOSITS + FRAS + i]), ql.Period(i + 1, ql.Years),
            calendar, ql.Annual, ql.ModifiedFollowing,
            ql.Thirty360(ql.Thirty360.European), euribor6m))
    curve = ql.PiecewiseLinearZero(today, helpers, ql.Actual365Fixed(),
                                   ql.IterativeBootstrap(1e-15))
    curve.enableExtrapolation()
    return curve


# %% [markdown]
# ### The book
#
# 200 spot-starting swaps with random side, nominal, fixed rate and maturity.
# The draws come from a Mersenne Twister with seed 42, four per trade.

# %%
Trade = namedtuple("Trade", "type nominal fixed_rate years")


def make_book(size):
    rng = ql.UniformRandomSequenceGenerator(4 * size, ql.UniformRandomGenerator(42))
    draws = iter([float(x) for x in rng.nextSequence().value()])
    book = []
    for _ in range(size):
        swap_type = ql.Swap.Payer if next(draws) < 0.5 else ql.Swap.Receiver
        nominal = 1e6 * (1 + int(10 * next(draws)))
        fixed_rate = 0.002 + 0.008 * next(draws)
        years = 1 + int(29.999 * next(draws))
        book.append(Trade(swap_type, nominal, fixed_rate, years))
    return book


def make_swap(trade, start, curve):
    index = ql.Euribor6M(curve)
    end = calendar.advance(start, trade.years, ql.Years)
    fixed = ql.Schedule(start, end, ql.Period(1, ql.Years), calendar, ql.ModifiedFollowing,
                        ql.ModifiedFollowing, ql.DateGeneration.Backward, False)
    floating = ql.Schedule(start, end, ql.Period(6, ql.Months), calendar, ql.ModifiedFollowing,
                           ql.ModifiedFollowing, ql.DateGeneration.Backward, False)
    swap = ql.VanillaSwap(trade.type, trade.nominal, fixed, trade.fixed_rate,
                          ql.Thirty360(ql.Thirty360.European), floating, index, 0.0,
                          ql.Actual360())
    swap.setPricingEngine(ql.DiscountingSwapEngine(curve))
    return swap


# %% [markdown]
# ### Sensitivities with AAD
#
# First the curve: the quotes are registered as inputs, the bootstrap is
# recorded, and one adjoint sweep per node zero rate gives one row of the
# Jacobian of the nodes to the quotes.

# %%
def curve_risk(tape, quotes):
    tape.clearAll()
    q = [ql.Real(x) for x in quotes]
    tape.registerInputs(q)
    tape.newRecording()

    curve = bootstrap([ql.SimpleQuote(x) for x in q])
    zeros = list(curve.data())
    for z in zeros:
        tape.registerOutput(z)

    jacobian = []
    for z in zeros:
        tape.clearDerivatives()
        z.derivative = 1.0
        tape.computeAdjoints()
        jacobian.append([x.derivative for x in q])
    return list(curve.dates()), [float(z) for z in zeros], jacobian


# %% [markdown]
# Then each swap, priced off a `ZeroCurve` through the same nodes, with the node
# zero rates as inputs of a small recording. The node sensitivities, times the
# Jacobian, are the sensitivities to the quotes.

# %%
def trade_risk(tape, start, book, dates, zeros, jacobian):
    npvs, risk = [], []
    for trade in book:
        tape.clearAll()
        z = [ql.Real(x) for x in zeros]
        tape.registerInputs(z)
        tape.newRecording()

        curve = ql.ZeroCurve(dates, z, ql.Actual365Fixed())
        curve.enableExtrapolation()
        npv = make_swap(trade, start, ql.YieldTermStructureHandle(curve)).NPV()

        tape.registerOutput(npv)
        npv.derivative = 1.0
        tape.computeAdjoints()
        sensitivities = [0.0] * len(jacobian[0])
        for zj, row in zip(z, jacobian):
            dz = zj.derivative
            if dz != 0.0:
                sensitivities = [s + dz * r for s, r in zip(sensitivities, row)]
        npvs.append(float(npv))
        risk.append(sensitivities)
    return npvs, risk


# %% [markdown]
# Put together, with the quote names attached:

# %%
def aad_sensitivities(book_size=200):
    ql.Settings.instance().evaluationDate = today
    start = calendar.advance(today, 2, ql.Days)
    book = make_book(book_size)
    with Tape() as tape:
        npvs, risk = trade_risk(tape, start, book, *curve_risk(tape, market_quotes()))
    names = quote_names()
    return npvs, [dict(zip(names, r)) for r in risk]


# %%
ql.Settings.instance().evaluationDate = today
start = calendar.advance(today, 2, ql.Days)
quotes, names, book = market_quotes(), quote_names(), make_book(200)
print(f"Sensitivities of each of the {len(book)} swaps in a book "
      f"to each of the {len(quotes)} curve quotes\n")

t0 = time.perf_counter()
npvs, risk = aad_sensitivities(len(book))
aad_seconds = time.perf_counter() - t0
risk = [[r[name] for name in names] for r in risk]
print(f"AAD: {aad_seconds * 1000:.1f} ms, "
      "from one recording of the curve and one small recording per swap")


# %% [markdown]
# ### Checks
#
# Every swap against a full recording of the bootstrap and the whole book, with
# one sweep per swap: this checks the chain rule through the curve nodes.

# %%
def through_bootstrap(quotes, book):
    with Tape() as tape:
        q = [ql.Real(x) for x in quotes]
        tape.registerInputs(q)
        tape.newRecording()
        curve = ql.YieldTermStructureHandle(bootstrap([ql.SimpleQuote(x) for x in q]))
        npvs = [make_swap(trade, start, curve).NPV() for trade in book]
        for npv in npvs:
            tape.registerOutput(npv)
        risk = []
        for npv in npvs:
            tape.clearDerivatives()
            npv.derivative = 1.0
            tape.computeAdjoints()
            risk.append([x.derivative for x in q])
    return risk


direct = through_bootstrap(quotes, book)
# max() would skip a NaN, so check first that every sensitivity is finite
if not all(math.isfinite(r) for rs in (risk, direct) for trade in rs for r in trade):
    raise ValueError("a sensitivity is not finite")
largest = max(abs(r) for trade in risk for r in trade)
difference = max(abs(a - b) for ta, tb in zip(risk, direct) for a, b in zip(ta, tb))
print(f"  all swaps against a full recording of curve and swaps "
      f"(largest sensitivity {largest:.1e}): largest difference {difference:.1e}")


# %% [markdown]
# The first swap and the longest one against central differences on plain
# pricing, which also checks the recording of the bootstrap itself. The same
# function with forward differences is the bumping alternative to AAD: one
# revaluation of the curve and of the book per quote.

# %%
def finite_differences(quotes, book, h, central):
    simple = [ql.SimpleQuote(x) for x in quotes]
    curve = ql.YieldTermStructureHandle(bootstrap(simple))
    swaps = [make_swap(trade, start, curve) for trade in book]
    base = [float(s.NPV()) for s in swaps]
    risk = [[0.0] * len(quotes) for _ in book]
    for i, x in enumerate(quotes):
        simple[i].setValue(x + h)
        up = [float(s.NPV()) for s in swaps]
        if central:
            simple[i].setValue(x - h)
            base = [float(s.NPV()) for s in swaps]
        simple[i].setValue(x)
        for k in range(len(book)):
            risk[k][i] = (up[k] - base[k]) / ((2 if central else 1) * h)
    return risk


longest = max(range(len(book)), key=lambda k: book[k].years)
checked = [0, longest]
differences = finite_differences(quotes, [book[k] for k in checked], 1e-5, central=True)
# relative to each sensitivity, or absolute below the floor, where rounding in
# the central differences dominates
floor = 100.0
for k, d in zip(checked, differences):
    relative = max(abs(a - b) / max(abs(b), floor) for a, b in zip(risk[k], d))
    print(f"  swap {k + 1} ({book[k].years}y) by central differences: "
          f"largest relative difference {relative:.1e}")

# bumping the whole book with forward differences, timed only
t0 = time.perf_counter()
finite_differences(quotes, book, 1e-6, central=False)
bumping_seconds = time.perf_counter() - t0
print(f"\nBumping: {bumping_seconds * 1000:.1f} ms, "
      f"{len(quotes) + 1} curve and book revaluations, AAD speedup "
      f"{bumping_seconds / aad_seconds:.1f}x")

# %% [markdown]
# ### Results
#
# The largest sensitivities of the first swap, to a unit change of each quote.

# %%
first = risk[0]
order = sorted(range(len(first)), key=lambda i: -abs(first[i]))
side = "payer" if book[0].type == ql.Swap.Payer else "receiver"
print(f"\nSwap 1 ({side}, {book[0].years}y), largest sensitivities:")
for i in order[:5]:
    print(f"{names[i]:>14} | {first[i]:14.0f}")
