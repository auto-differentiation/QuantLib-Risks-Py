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
# # Adjoint sensitivities as the number of inputs grows
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
# A fixed book of 250 European options is priced off spot, a dividend yield, a
# 7-point zero curve and a Black volatility surface that grows from 4 expiries
# by 5 strikes up to 20 by 25, so from 29 to 509 market inputs.
#
# All sensitivities are computed in two ways:
#
# * **AAD**: the pricing is recorded once on an XAD tape and one adjoint sweep
#   gives the derivative of the book value to every input;
# * **bumping**: forward differences, one extra pricing of the book per input.
#
# The cost of AAD grows only slightly as the surface grows, while the cost of
# bumping grows with the number of inputs.

# %%
import math
import time
from dataclasses import dataclass

import QuantLibAAD as ql
from xad.adj_1st import Tape

# %% [markdown]
# ### Setup
#
# Everything that stays fixed while the market moves: the curve dates, the
# surface grid and the book. The zero curve runs up to the first node past the
# book's last maturity, so that every node has a sensitivity. Expiries are
# spread between 1 month and 5 years, strikes between 60 and 140. The book is
# drawn from a Mersenne-Twister generator with a fixed seed, so it is the same
# for every surface size.

# %%
TODAY = ql.Date(15, ql.May, 2026)
BOOK_SIZE = 250
CURVE_MONTHS = [0, 3, 6, 12, 24, 36, 60]
SURFACES = [(4, 5), (6, 10), (10, 15), (15, 20), (20, 25)]  # expiries x strikes


@dataclass
class Setup:
    curve_dates: list
    expiries: list
    strikes: list
    book: list  # (option type, strike, maturity)


def make_book(size):
    # three draws per option: type, strike, maturity
    rng = ql.UniformRandomSequenceGenerator(3 * size, ql.UniformRandomGenerator(42))
    draws = iter(float(x) for x in rng.nextSequence().value())
    book = []
    for _ in range(size):
        option_type = ql.Option.Call if next(draws) < 0.5 else ql.Option.Put
        strike = 70.0 + 60.0 * next(draws)
        maturity = TODAY + int(30 + next(draws) * 1700)
        book.append((option_type, strike, maturity))
    return book


def make_setup(n_expiries, n_strikes, book_size=BOOK_SIZE):
    return Setup(
        curve_dates=[TODAY + ql.Period(m, ql.Months) for m in CURVE_MONTHS],
        expiries=[TODAY + ql.Period(1 + j * 59 // (n_expiries - 1), ql.Months)
                  for j in range(n_expiries)],
        strikes=[60.0 + 80.0 * i / (n_strikes - 1) for i in range(n_strikes)],
        book=make_book(book_size),
    )


# %% [markdown]
# ### Market data
#
# Every number in the market gets a sensitivity. The market is a dictionary
# from input name to value; the volatilities follow a smile in log-moneyness
# with a short-dated bump.

# %%
def make_market(setup):
    dc = ql.Actual365Fixed()
    market = {"spot": 100.0, "dividend yield": 0.015}
    for i, months in enumerate(CURVE_MONTHS):
        market[f"zero rate {months}M"] = 0.025 + 0.0015 * i
    for i, strike in enumerate(setup.strikes):
        for j, expiry in enumerate(setup.expiries):
            moneyness = math.log(strike / 100.0)
            t = dc.yearFraction(TODAY, expiry)
            market[f"vol strike {i + 1} expiry {j + 1}"] = (
                0.18 - 0.08 * moneyness + 0.15 * moneyness**2 + 0.03 * math.exp(-t))
    return market


# %% [markdown]
# ### Pricing the book
#
# The curves and the surface are built from the market data, then each option
# is priced with the analytic Black-Scholes engine. The same function works on
# plain floats (bumping) and on XAD values registered on a tape (AAD).

# %%
def price_book(setup, market):
    dc = ql.Actual365Fixed()
    n_strikes, n_expiries = len(setup.strikes), len(setup.expiries)
    vols = ql.Matrix(n_strikes, n_expiries)
    for i in range(n_strikes):
        for j in range(n_expiries):
            vols[i][j] = market[f"vol strike {i + 1} expiry {j + 1}"]
    process = ql.BlackScholesMertonProcess(
        ql.QuoteHandle(ql.SimpleQuote(market["spot"])),
        ql.YieldTermStructureHandle(ql.FlatForward(TODAY, market["dividend yield"], dc)),
        ql.YieldTermStructureHandle(ql.ZeroCurve(
            setup.curve_dates, [market[f"zero rate {m}M"] for m in CURVE_MONTHS], dc)),
        ql.BlackVolTermStructureHandle(ql.BlackVarianceSurface(
            TODAY, ql.TARGET(), setup.expiries, setup.strikes, vols, dc,
            ql.BlackVarianceSurface.ConstantExtrapolation,
            ql.BlackVarianceSurface.ConstantExtrapolation)))
    engine = ql.AnalyticEuropeanEngine(process)

    value = 0.0
    for option_type, strike, maturity in setup.book:
        option = ql.VanillaOption(ql.PlainVanillaPayoff(option_type, strike),
                                  ql.EuropeanExercise(maturity))
        option.setPricingEngine(engine)
        value += option.NPV()
    return value


# %% [markdown]
# ### AAD: one recording and one adjoint sweep
#
# The market values become XAD inputs on the tape; after recording the pricing,
# seeding the output adjoint and one sweep back through the tape give the
# derivatives to all inputs at once.

# %%
def price_with_aad(tape, setup, market):
    tape.clearAll()
    inputs = {name: ql.Real(x) for name, x in market.items()}
    tape.registerInputs(inputs.values())
    tape.newRecording()

    value = price_book(setup, inputs)

    tape.registerOutput(value)
    value.derivative = 1.0
    tape.computeAdjoints()
    return float(value), {name: x.derivative for name, x in inputs.items()}


def aad_sensitivities(n_expiries, n_strikes, book_size=BOOK_SIZE):
    ql.Settings.instance().evaluationDate = TODAY
    setup = make_setup(n_expiries, n_strikes, book_size)
    with Tape() as tape:
        return price_with_aad(tape, setup, make_market(setup))


# %% [markdown]
# ### Finite differences
#
# Bumping uses forward differences, one extra pricing per input. Central
# differences, two pricings per input, check the AAD results.

# %%
def bumped(market, name, h):
    shifted = dict(market)
    shifted[name] += h
    return shifted


def plain_price(setup, market):
    return float(price_book(setup, market))


def bumping_sensitivities(setup, market):
    value = plain_price(setup, market)
    sensitivities = {}
    for name, x in market.items():
        h = 1e-6 * max(1.0, abs(x))
        sensitivities[name] = (plain_price(setup, bumped(market, name, h)) - value) / h
    return value, sensitivities


def central_differences(setup, market):
    sensitivities = {}
    for name, x in market.items():
        h = 1e-5 * max(1.0, abs(x))
        up = plain_price(setup, bumped(market, name, h))
        down = plain_price(setup, bumped(market, name, -h))
        sensitivities[name] = (up - down) / (2.0 * h)
    return sensitivities


# %% [markdown]
# ### Checking AAD against central differences
#
# The difference is relative to each sensitivity, or absolute below 1, so that
# small sensitivities are checked too.

# %%
def check_against_central_differences():
    ql.Settings.instance().evaluationDate = TODAY
    for n_expiries, n_strikes in SURFACES:
        setup = make_setup(n_expiries, n_strikes)
        market = make_market(setup)
        with Tape() as tape:
            _, aad = price_with_aad(tape, setup, market)
        fd = central_differences(setup, market)
        if not all(math.isfinite(s) for s in [*aad.values(), *fd.values()]):
            raise ValueError("a sensitivity is not finite")
        errors = [abs(aad[name] - fd[name]) for name in market]
        relative = max(e / max(abs(fd[name]), 1.0) for e, name in zip(errors, market))
        print(f"AAD vs central differences, {len(market)} inputs: "
              f"largest difference {max(errors):.1e} "
              f"(largest sensitivity {max(abs(s) for s in aad.values()):.1e}), "
              f"largest relative difference {relative:.3e}")


# %% [markdown]
# ### Timing
#
# Each method runs repeatedly and the median wall-clock time is reported. The
# price column is a single pricing of the book without derivatives.

# %%
def time_ms(f):
    times = []
    while len(times) < 3 or (sum(times) < 500.0 and len(times) < 50):
        start = time.perf_counter()
        f()
        times.append(1000.0 * (time.perf_counter() - start))
    return sorted(times)[len(times) // 2]


def timing_table():
    ql.Settings.instance().evaluationDate = TODAY
    print(" inputs |    price    |   bumping   |     AAD     | AAD/price | bumping/AAD | tape memory")
    print("--------+-------------+-------------+-------------+-----------+-------------+------------")
    with Tape() as tape:
        for n_expiries, n_strikes in SURFACES:
            setup = make_setup(n_expiries, n_strikes)
            market = make_market(setup)
            price = time_ms(lambda: plain_price(setup, market))
            bumping = time_ms(lambda: bumping_sensitivities(setup, market))
            aad = time_ms(lambda: price_with_aad(tape, setup, market))
            tape_mb = tape.getMemory() / (1024.0 * 1024.0)
            print(f"{len(market):7d} | {price:8.1f} ms | {bumping:8.1f} ms | {aad:8.1f} ms "
                  f"| {aad / price:8.1f}x | {bumping / aad:10.1f}x | {tape_mb:7.1f} MB")


# %% [markdown]
# ### Results
#
# The check, the timings, and the sensitivities on the smallest surface.

# %%
if __name__ == "__main__":
    ql.Settings.instance().evaluationDate = TODAY
    print(f"Sensitivities of a book of {BOOK_SIZE} European options to spot, dividend yield,")
    print("a 7-point zero curve and a Black volatility surface of growing size\n")
    check_against_central_differences()
    print()
    timing_table()

    n_expiries, n_strikes = SURFACES[0]
    _, sensitivities = aad_sensitivities(n_expiries, n_strikes)
    print(f"\nSensitivities on the {len(sensitivities)}-input surface:")
    for name, s in sensitivities.items():
        print(f"{name} | {s:.4f}")
