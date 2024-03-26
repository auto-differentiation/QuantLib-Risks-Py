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
# # Interest-rate swap pricing on multiple curves with sensitivities
#
# This sample prices a forward-starting interest rate swap on a curve that
# has been bootrapped on a large number of market quotes. 
# It calculates all sensitivities using QuantLib-Risks and measures the performance
# (averaged over a number of repetitions).
#
# Pricing using standard QuantLib can also be done by simply changing the import
# statement (in which case it does not calculate sensitivities),
# to establish correctness of results and a performance baseline.
#
# Copyright (&copy;) 2000, 2001, 2002, 2003 RiskMap srl<br>
# Copyright (&copy;) 2003, 2004, 2005, 2006, 2007 StatPro Italia srl<br>
# Copyright (&copy;) 2004 Ferdinando Ametrano<br>
# Copyright (&copy;) 2018 Jose Garcia<br>
# Copyright (&copy;) 2024 Xcelerit Computing Limited.
#
# This file is part of QuantLib-Risks, a Python wrapper for QuantLib enabled
# for risk computation using automatic differentiation. It uses XAD,
# a fast and comprehensive C++ library for automatic differentiation.
#
# QuantLib-Risks and XAD are free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QuantLib-Risks is distributed in the hope that it will be useful,
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

# %%

import QuantLib_Risks as ql  # enable this to calculate sensitivities

# import QuantLib as ql  # enable this for regular QuantLib performance

from xad_autodiff.adj_1st import Tape
import time

# %% [markdown]
# #### bootstrapping and pricing function

# %%

def priceMulticurveBootstrappingSwap(
    depos: list,
    calendar: ql.Calendar,
    shortOis: list,
    datesOIS: list,
    longTermOIS: list,
    todaysDate: ql.Date,
    termStructureDayCounter: ql.DayCounter,
    d6MRate,
    fra: list,
    swapRates: list,
    settlementDate: ql.Date,
    fwdStart: ql.Period,
    nominal,
    fixedRate,
    spread,
    lengthInYears: int,
):
    eonia = ql.Eonia()

    #####   Deposits
    # settlement days -> quote
    depoQuotes = [
        (0, ql.SimpleQuote(depos[0])),
        (1, ql.SimpleQuote(depos[1])),
        (2, ql.SimpleQuote(depos[2])),
    ]
    depositDayCounter = ql.Actual360()
    eoniaInstruments = [
        ql.DepositRateHelper(
            ql.QuoteHandle(quote),
            ql.Period(1, ql.Days),
            settlementDays,
            calendar,
            ql.Following,
            False,
            depositDayCounter,
        )
        for settlementDays, quote in depoQuotes
    ]

    ####### short-term OIS
    shortOisQuotes = [
        (ql.Period(1, ql.Weeks), ql.SimpleQuote(shortOis[0])),
        (ql.Period(2, ql.Weeks), ql.SimpleQuote(shortOis[1])),
        (ql.Period(3, ql.Weeks), ql.SimpleQuote(shortOis[2])),
        (ql.Period(1, ql.Months), ql.SimpleQuote(shortOis[3])),
    ]

    eoniaInstruments.extend(
        ql.OISRateHelper(2, tenor, ql.QuoteHandle(quote), eonia)
        for tenor, quote in shortOisQuotes
    )

    ######## Dated OIS
    datedOisQuotes = [
        (
            ql.Date(16, ql.January, 2013),
            ql.Date(13, ql.February, 2013),
            ql.SimpleQuote(datesOIS[0]),
        ),
        (
            ql.Date(13, ql.February, 2013),
            ql.Date(13, ql.March, 2013),
            ql.SimpleQuote(datesOIS[1]),
        ),
        (
            ql.Date(13, ql.March, 2013),
            ql.Date(10, ql.April, 2013),
            ql.SimpleQuote(datesOIS[2]),
        ),
        (
            ql.Date(10, ql.April, 2013),
            ql.Date(8, ql.May, 2013),
            ql.SimpleQuote(datesOIS[3]),
        ),
        (
            ql.Date(8, ql.May, 2013),
            ql.Date(12, ql.June, 2013),
            ql.SimpleQuote(datesOIS[4]),
        ),
    ]
    eoniaInstruments.extend(
        ql.DatedOISRateHelper(startDate, endDate, ql.QuoteHandle(quote), eonia)
        for startDate, endDate, quote in datedOisQuotes
    )

    ######## long-term OIS
    longOisQuotes = (
        (ql.Period(15, ql.Months), ql.SimpleQuote(longTermOIS[0])),
        (ql.Period(18, ql.Months), ql.SimpleQuote(longTermOIS[1])),
        (ql.Period(21, ql.Months), ql.SimpleQuote(longTermOIS[2])),
        (ql.Period(2, ql.Years), ql.SimpleQuote(longTermOIS[3])),
        (ql.Period(3, ql.Years), ql.SimpleQuote(longTermOIS[4])),
        (ql.Period(4, ql.Years), ql.SimpleQuote(longTermOIS[5])),
        (ql.Period(5, ql.Years), ql.SimpleQuote(longTermOIS[6])),
        (ql.Period(6, ql.Years), ql.SimpleQuote(longTermOIS[7])),
        (ql.Period(7, ql.Years), ql.SimpleQuote(longTermOIS[8])),
        (ql.Period(8, ql.Years), ql.SimpleQuote(longTermOIS[9])),
        (ql.Period(9, ql.Years), ql.SimpleQuote(longTermOIS[10])),
        (ql.Period(10, ql.Years), ql.SimpleQuote(longTermOIS[11])),
        (ql.Period(11, ql.Years), ql.SimpleQuote(longTermOIS[12])),
        (ql.Period(12, ql.Years), ql.SimpleQuote(longTermOIS[13])),
        (ql.Period(15, ql.Years), ql.SimpleQuote(longTermOIS[14])),
        (ql.Period(20, ql.Years), ql.SimpleQuote(longTermOIS[15])),
        (ql.Period(25, ql.Years), ql.SimpleQuote(longTermOIS[16])),
        (ql.Period(30, ql.Years), ql.SimpleQuote(longTermOIS[17])),
    )
    eoniaInstruments.extend(
        ql.OISRateHelper(2, tenor, ql.QuoteHandle(quote), eonia)
        for tenor, quote in longOisQuotes
    )

    ########### curve
    eoniaTermStructure = ql.PiecewiseLogCubicDiscount(
        todaysDate, eoniaInstruments, termStructureDayCounter
    )
    eoniaTermStructure.enableExtrapolation()

    # This curve will be used for discounting cash flows
    discountingTermStructure = ql.RelinkableYieldTermStructureHandle()
    discountingTermStructure.linkTo(eoniaTermStructure)

    euribor6MInstruments = []

    euribor6M = ql.Euribor6M()

    d6M = ql.DepositRateHelper(
        ql.QuoteHandle(ql.SimpleQuote(d6MRate)),
        ql.Period(6, ql.Months),
        3,
        calendar,
        ql.Following,
        False,
        depositDayCounter,
    )

    euribor6MInstruments.append(d6M)

    ###### FRAs
    fraQuotes = [
        (1, ql.SimpleQuote(fra[0])),
        (2, ql.SimpleQuote(fra[1])),
        (3, ql.SimpleQuote(fra[2])),
        (4, ql.SimpleQuote(fra[3])),
        (5, ql.SimpleQuote(fra[4])),
        (6, ql.SimpleQuote(fra[5])),
        (7, ql.SimpleQuote(fra[6])),
        (8, ql.SimpleQuote(fra[7])),
        (9, ql.SimpleQuote(fra[8])),
        (10, ql.SimpleQuote(fra[9])),
        (11, ql.SimpleQuote(fra[10])),
        (12, ql.SimpleQuote(fra[11])),
        (13, ql.SimpleQuote(fra[12])),
        (14, ql.SimpleQuote(fra[13])),
        (15, ql.SimpleQuote(fra[14])),
        (16, ql.SimpleQuote(fra[15])),
        (17, ql.SimpleQuote(fra[16])),
        (18, ql.SimpleQuote(fra[17])),
    ]
    euribor6MInstruments.extend(
        ql.FraRateHelper(ql.QuoteHandle(quote), monthsToStart, euribor6M)
        for monthsToStart, quote in fraQuotes
    )

    ###### swaps
    swapQuotes = (
        (ql.Period(3, ql.Years), ql.SimpleQuote(swapRates[0])),
        (ql.Period(4, ql.Years), ql.SimpleQuote(swapRates[1])),
        (ql.Period(5, ql.Years), ql.SimpleQuote(swapRates[2])),
        (ql.Period(6, ql.Years), ql.SimpleQuote(swapRates[3])),
        (ql.Period(7, ql.Years), ql.SimpleQuote(swapRates[4])),
        (ql.Period(8, ql.Years), ql.SimpleQuote(swapRates[5])),
        (ql.Period(9, ql.Years), ql.SimpleQuote(swapRates[6])),
        (ql.Period(10, ql.Years), ql.SimpleQuote(swapRates[7])),
        (ql.Period(12, ql.Years), ql.SimpleQuote(swapRates[8])),
        (ql.Period(15, ql.Years), ql.SimpleQuote(swapRates[9])),
        (ql.Period(20, ql.Years), ql.SimpleQuote(swapRates[10])),
        (ql.Period(25, ql.Years), ql.SimpleQuote(swapRates[11])),
        (ql.Period(30, ql.Years), ql.SimpleQuote(swapRates[12])),
        (ql.Period(35, ql.Years), ql.SimpleQuote(swapRates[13])),
        (ql.Period(40, ql.Years), ql.SimpleQuote(swapRates[14])),
        (ql.Period(50, ql.Years), ql.SimpleQuote(swapRates[15])),
        (ql.Period(60, ql.Years), ql.SimpleQuote(swapRates[16])),
    )

    swFixedLegFrequency = ql.Annual
    swFixedLegConvention = ql.Unadjusted
    swFixedLegDayCounter = ql.Thirty360(ql.Thirty360.European)
    euribor6MInstruments.extend(
        ql.SwapRateHelper(
            ql.QuoteHandle(quote),
            tenor,
            calendar,
            swFixedLegFrequency,
            swFixedLegConvention,
            swFixedLegDayCounter,
            euribor6M,
            ql.QuoteHandle(),
            ql.Period(0, ql.Days),
            discountingTermStructure,
        )
        for tenor, quote in swapQuotes
    )

    euribor6MTermStructure = ql.PiecewiseLogCubicDiscount(
        settlementDate,
        euribor6MInstruments,
        termStructureDayCounter,
    )

    forecastingTermStructure = ql.RelinkableYieldTermStructureHandle()
    forecastingTermStructure.linkTo(euribor6MTermStructure)

    euriborIndex = ql.Euribor6M(forecastingTermStructure)

    fwdStartDate = calendar.advance(settlementDate, fwdStart)
    fwdMaturity = fwdStartDate + ql.Period(lengthInYears, ql.Years)
    fwdFixedSchedule = ql.Schedule(
        fwdStartDate,
        fwdMaturity,
        ql.Period(ql.Annual),
        calendar,
        ql.Unadjusted,
        ql.Unadjusted,
        ql.DateGeneration.Forward,
        False,
    )
    fwdFloatSchedule = ql.Schedule(
        fwdStartDate,
        fwdMaturity,
        ql.Period(ql.Semiannual),
        calendar,
        ql.ModifiedFollowing,
        ql.ModifiedFollowing,
        ql.DateGeneration.Forward,
        False,
    )
    oneYearForward5YearSwap = ql.VanillaSwap(
        ql.Swap.Payer,
        nominal,
        fwdFixedSchedule,
        fixedRate,
        ql.Thirty360(ql.Thirty360.European),
        fwdFloatSchedule,
        euriborIndex,
        spread,
        ql.Actual360(),
    )
    swapEngine = ql.DiscountingSwapEngine(discountingTermStructure)

    oneYearForward5YearSwap.setPricingEngine(swapEngine)

    return oneYearForward5YearSwap.NPV()


# %% [markdown]
# #### pricing with sensitivity extraction

# %%
tape = Tape()


def priceWithSensi(
    depos: list,
    calendar: ql.Calendar,
    shortOis: list,
    datesOIS: list,
    longTermOIS: list,
    todaysDate: ql.Date,
    termStructureDayCounter: ql.DayCounter,
    d6MRate,
    fra: list,
    swapRates: list,
    settlementDate: ql.Date,
    fwdStart: ql.Period,
    nominal,
    fixedRate,
    spread,
    lengthInYears: int,
):

    tape.clearAll()
    with tape:
        depos_t = [ql.Real(q) for q in depos]
        shortOis_t = [ql.Real(q) for q in shortOis]
        datesOIS_t = [ql.Real(q) for q in datesOIS]
        longTermOIS_t = [ql.Real(q) for q in longTermOIS]
        swapRates_t = [ql.Real(q) for q in swapRates]
        fra_t = [ql.Real(q) for q in fra]
        fixedRate_t = ql.Real(fixedRate)
        spread_t = ql.Real(spread)
        nominal_t = ql.Real(nominal)
        d6MRate_t = ql.Real(d6MRate)

        tape.registerInputs(depos_t)
        tape.registerInputs(shortOis_t)
        tape.registerInputs(datesOIS_t)
        tape.registerInputs(longTermOIS_t)
        tape.registerInputs(swapRates_t)
        tape.registerInputs(fra_t)
        tape.registerInput(fixedRate_t)
        tape.registerInput(spread_t)
        tape.registerInput(nominal_t)
        tape.registerInput(d6MRate_t)
        tape.newRecording()

        value = priceMulticurveBootstrappingSwap(
            depos_t,
            calendar,
            shortOis_t,
            datesOIS_t,
            longTermOIS_t,
            todaysDate,
            termStructureDayCounter,
            d6MRate_t,
            fra_t,
            swapRates_t,
            settlementDate,
            fwdStart,
            nominal_t,
            fixedRate_t,
            spread_t,
            lengthInYears,
        )

        # register output, set its adjoint, and roll-back the tape
        tape.registerOutput(value)
        value.derivative = 1.0
        tape.computeAdjoints()

        # obtain the sensitivities (input adjoints)
        gradient = []
        gradient.extend(g.derivative for g in depos_t)
        gradient.extend(g.derivative for g in shortOis_t)
        gradient.extend(g.derivative for g in datesOIS_t)
        gradient.extend(g.derivative for g in longTermOIS_t)
        gradient.extend(g.derivative for g in swapRates_t)
        gradient.extend(g.derivative for g in fra_t)
        gradient.append(fixedRate_t.derivative)
        gradient.append(spread_t.derivative)
        gradient.append(nominal_t.derivative)
        gradient.append(d6MRate_t.derivative)

        return value.value, gradient


# %% [markdown]
# ### Results Printing

# %%
def printResults(
    v, gradient: list, nDepos, nShortOis, ndatesOIS, nlongOIS, nSwapRates, nFRA
):
    print(f"Price  = {v:,.2f}")
    print("Sensitivities w.r.t. depo quotes, for 1bp shift   = [")
    cnt = 0
    for i in range(cnt, cnt + nDepos):
        print(f"{gradient[i] * 0.0001:.2f},")
    cnt += nDepos
    print("]")
    print("Sensitivities w.r.t. short OIS quotes, for 1bp shift = [")
    for i in range(cnt, cnt + nShortOis):
        print(f"{gradient[i] * 0.0001:.2f},")
    cnt += nShortOis
    print("]")
    print("Sensitivities w.r.t. date OIS quotes, for 1bp shift = [")
    for i in range(cnt, cnt + ndatesOIS):
        print(f"{gradient[i] * 0.0001:.2f},")
    cnt += ndatesOIS
    print("]")
    print("Sensitivities w.r.t. long OIS quotes, for 1bp shift = [")
    for i in range(cnt, cnt + nlongOIS):
        print(f"{gradient[i] * 0.0001:.2f},")
    cnt += nlongOIS
    print("]")
    print("Sensitivities w.r.t. swap quotes, for 1bp shift    = [")
    for i in range(cnt, cnt + nSwapRates):
        print(f"{gradient[i] * 0.0001:.2f},")
    cnt += nSwapRates
    print("]")
    print("Sensitivities w.r.t. FRA quotes, for 1bp shift     = [")
    for i in range(cnt, cnt + nFRA):
        print(f"{gradient[i] * 0.0001:.2f},")
    cnt += nFRA
    print("]")
    print(
        f"Sensitivity w.r.t. swap fixed Rate, 1bp shift      = {gradient[cnt] * 0.0001:.2f}"
    )
    print(
        f"Sensitivity w.r.t. swap spread, 1bp shift          = {gradient[cnt+1] * 0.0001:.2f}"
    )
    print(f"Sensitivity w.r.t. swap nominal, USD 1,000 shift   = {gradient[cnt+2]:.2f}")
    print(
        f"Sensitivity w.r.t. swap d6Mrate, 1bp shift         = {gradient[cnt+3] * 0.0001:.2f}"
    )
    print(f"Total number of sensitivities computed: {len(gradient)}")


# %% [markdown]
# ### Global Parameters

# %%
calendar = ql.TARGET()
todaysDate = ql.Date(11, ql.December, 2012)
ql.Settings.instance().evaluationDate = todaysDate

fixingDays = 2
settlementDate = calendar.advance(todaysDate, fixingDays, ql.Days)
# must be a business day
settlementDate = calendar.adjust(settlementDate)

# %% [markdown]
# ### EONIA CURVE quotes

# %%
termStructureDayCounter = ql.Actual365Fixed()
depos = [0.0004, 0.0004, 0.0004]
shortOis = [0.00070, 0.00069, 0.00078, 0.00074]
datesOIS = [0.000460, 0.000160, -0.000070, -0.000130, -0.000140]
longTermOIS = [
    0.00002,
    0.00008,
    0.00021,
    0.00036,
    0.00127,
    0.00274,
    0.00456,
    0.00647,
    0.00827,
    0.00996,
    0.01147,
    0.0128,
    0.01404,
    0.01516,
    0.01764,
    0.01939,
    0.02003,
    0.02038,
]
fra = [
    0.002930,
    0.002720,
    0.002600,
    0.002560,
    0.002520,
    0.002480,
    0.002540,
    0.002610,
    0.002670,
    0.002790,
    0.002910,
    0.003030,
    0.003180,
    0.003350,
    0.003520,
    0.003710,
    0.003890,
    0.004090,
]
swapRates = [
    0.004240,
    0.005760,
    0.007620,
    0.009540,
    0.011350,
    0.013030,
    0.014520,
    0.015840,
    0.018090,
    0.020370,
    0.021870,
    0.022340,
    0.022560,
    0.022950,
    0.023480,
    0.024210,
    0.024630,
]

# %% [markdown]
# ### Swap Parameters

# %%
# forward-starting 5 year swap

nominal = 1000000.0
spread = 0.007
fixedRate = 0.007
lengthInYears = 5
d6MRate = 0.00312
fwdStart = ql.Period(15, ql.Months)

# %% [markdown]
# ### Benchmark Parameters

# %%
N = 20  # iterations to repeat pricing for performance measurements

# %% [markdown]
# ### Pricing

# %%


if not getattr(ql, "XAD_ENABLED", False):
    # ql.XAD_ENABLED is set if we're using QuantLib-Risks
    print("Pricing swap with multicurve bootstrapping without sensitivities...")
    start = time.perf_counter_ns()
    for _ in range(N):
        v = priceMulticurveBootstrappingSwap(
            depos,
            calendar,
            shortOis,
            datesOIS,
            longTermOIS,
            todaysDate,
            termStructureDayCounter,
            d6MRate,
            fra,
            swapRates,
            settlementDate,
            fwdStart,
            nominal,
            fixedRate,
            spread,
            lengthInYears,
        )
    end = time.perf_counter_ns()
    duration = (end - start) * 1e-6 / N
    print(f"Price = {v:,.2f}")
else:
    # pricing with AAD
    print("Pricing swap with multicurve bootstrapping with sensitivities...")
    start = time.perf_counter_ns()
    for _ in range(N):
        v2, gradient = priceWithSensi(
            depos,
            calendar,
            shortOis,
            datesOIS,
            longTermOIS,
            todaysDate,
            termStructureDayCounter,
            d6MRate,
            fra,
            swapRates,
            settlementDate,
            fwdStart,
            nominal,
            fixedRate,
            spread,
            lengthInYears,
        )
    end = time.perf_counter_ns()
    duration = (end - start) * 1e-6 / N

    printResults(
        v2,
        gradient,
        len(depos),
        len(shortOis),
        len(datesOIS),
        len(longTermOIS),
        len(swapRates),
        len(fra),
    )

print("-" * 30)
print(f"Took (average over {N} repetitions): {duration:.2f}ms")
