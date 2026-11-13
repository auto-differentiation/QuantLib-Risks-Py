# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Credit default swaps
#
# Copyright (&copy;) 2014 Thema Consulting SA
# Copyright (&copy;) 2024 Xcelerit Computing Limited.
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

# ### Setup

import QuantLibAAD as ql

calendar = ql.TARGET()

todaysDate = ql.Date(15, ql.May, 2007)
ql.Settings.instance().evaluationDate = todaysDate

flat_rate = 0.01
risk_free_rate = ql.YieldTermStructureHandle(ql.FlatForward(todaysDate, flat_rate, ql.Actual365Fixed()))

# ### CDS parameters

recovery_rate = 0.5
quoted_spreads = [0.0150, 0.0150, 0.0150, 0.0150]
tenors = [ql.Period(3, ql.Months), ql.Period(6, ql.Months), ql.Period(1, ql.Years), ql.Period(2, ql.Years)]
maturities = [calendar.adjust(todaysDate + x, ql.Following) for x in tenors]

instruments = [
    ql.SpreadCdsHelper(
        ql.makeQuoteHandle(s),
        tenor,
        0,
        calendar,
        ql.Quarterly,
        ql.Following,
        ql.DateGeneration.TwentiethIMM,
        ql.Actual365Fixed(),
        recovery_rate,
        risk_free_rate,
    )
    for s, tenor in zip(quoted_spreads, tenors)
]

hazard_curve = ql.PiecewiseFlatHazardRate(todaysDate, instruments, ql.Actual365Fixed())
print("Calibrated hazard rate values: ")
for x in hazard_curve.nodes():
    print("hazard rate on {} is {:.7f}".format(*x))

print("Some survival probability values: ")
print(
    "1Y survival probability: {:.4g}, \n\t\texpected {:.4g}".format(
    hazard_curve.survivalProbability(todaysDate + ql.Period("1Y")), 0.9704)
)
print(
    "2Y survival probability: {:.4g}, \n\t\texpected {:.4g}".format(
    hazard_curve.survivalProbability(todaysDate + ql.Period("2Y")), 0.9418)
)

# ### Reprice instruments

nominal = 1000000.0
probability = ql.DefaultProbabilityTermStructureHandle(hazard_curve)

# We'll create a cds for every maturity:

all_cds = []
for maturity, s in zip(maturities, quoted_spreads):
    schedule = ql.Schedule(
        todaysDate,
        maturity,
        ql.Period(ql.Quarterly),
        calendar,
        ql.Following,
        ql.Unadjusted,
        ql.DateGeneration.TwentiethIMM,
        False,
    )
    cds = ql.CreditDefaultSwap(ql.Protection.Seller, nominal, s, schedule, ql.Following, ql.Actual365Fixed())
    engine = ql.MidPointCdsEngine(probability, recovery_rate, risk_free_rate)
    cds.setPricingEngine(engine)
    all_cds.append(cds)

print("Repricing of quoted CDSs employed for calibration: ")
for cds, tenor in zip(all_cds, tenors):
    print("{} fair spread: {:.7g}".format(tenor, cds.fairSpread()))
    print("   NPV: {:g}".format(cds.NPV()))
    print("   default leg: {:.7g}".format(cds.defaultLegNPV()))
    print("   coupon leg: {:.7g}".format(cds.couponLegNPV()))
    print("")

# ### Sensitivities with AAD
#
# QuantLibAAD records every operation on a tape, including the bootstrap of
# the hazard curve, so one backward pass gives the sensitivities of the 2Y CDS
# to all its inputs at once: the quoted spreads (through the bootstrap), the
# risk-free rate and recovery rate (used by both the bootstrap and the
# engine), the CDS's own running coupon and its nominal.
#
# The inputs are `ql.Real` values registered on the tape before the curves,
# helpers and CDS are built from them. As a check, we compare with central
# differences, re-bootstrapping the curve for each bump.

from xad.adj_1st import Tape

tenor_labels = [str(tenor) for tenor in tenors]
market_inputs = {"spread %s" % label: s for label, s in zip(tenor_labels, quoted_spreads)}
market_inputs.update({"risk-free rate": flat_rate, "recovery rate": recovery_rate,
                      "coupon": quoted_spreads[-1], "nominal": nominal})


def cds_npv(x):
    day_counter = ql.Actual365Fixed()
    risk_free = ql.YieldTermStructureHandle(ql.FlatForward(todaysDate, x["risk-free rate"], day_counter))
    helpers = [
        ql.SpreadCdsHelper(
            ql.QuoteHandle(ql.SimpleQuote(x["spread %s" % label])),
            tenor,
            0,
            calendar,
            ql.Quarterly,
            ql.Following,
            ql.DateGeneration.TwentiethIMM,
            day_counter,
            x["recovery rate"],
            risk_free,
        )
        for label, tenor in zip(tenor_labels, tenors)
    ]
    hazard = ql.DefaultProbabilityTermStructureHandle(
        ql.PiecewiseFlatHazardRate(todaysDate, helpers, day_counter))
    schedule = ql.Schedule(
        todaysDate,
        maturities[-1],
        ql.Period(ql.Quarterly),
        calendar,
        ql.Following,
        ql.Unadjusted,
        ql.DateGeneration.TwentiethIMM,
        False,
    )
    cds = ql.CreditDefaultSwap(ql.Protection.Seller, x["nominal"], x["coupon"], schedule,
                               ql.Following, day_counter)
    cds.setPricingEngine(ql.MidPointCdsEngine(hazard, x["recovery rate"], risk_free))
    return cds.NPV()


def aad_sensitivities():
    ql.Settings.instance().evaluationDate = todaysDate
    with Tape() as tape:
        inputs = {name: ql.Real(value) for name, value in market_inputs.items()}
        tape.registerInputs(inputs.values())
        tape.newRecording()

        npv = cds_npv(inputs)

        tape.registerOutput(npv)
        npv.derivative = 1.0
        tape.computeAdjoints()
        return float(npv), {name: x.derivative for name, x in inputs.items()}


def bumped_sensitivities(relative_bump=1e-4):
    sensitivities = {}
    for name, value in market_inputs.items():
        h = relative_bump * max(1.0, abs(value))
        up, down = dict(market_inputs), dict(market_inputs)
        up[name] += h
        down[name] -= h
        sensitivities[name] = (float(cds_npv(up)) - float(cds_npv(down))) / (2 * h)
    return sensitivities


npv, aad = aad_sensitivities()
bumped = bumped_sensitivities()

print("2Y CDS NPV = {:.6f}".format(npv))
print("{:<16}{:>18}{:>18}".format("Input", "AAD", "Central diff."))
for name in market_inputs:
    print("{:<16}{:>18.6f}{:>18.6f}".format(name, aad[name], bumped[name]))
