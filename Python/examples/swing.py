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

# # Swing options
#
# Copyright (&copy;) 2018 Klaus Spanderen
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

import QuantLib_Risks as ql
from xad_autodiff import math

todaysDate = ql.Date(30, ql.September, 2018)
ql.Settings.instance().evaluationDate = todaysDate
settlementDate = todaysDate
riskFreeRate = ql.FlatForward(settlementDate, 0.0, ql.Actual365Fixed())
dividendYield = ql.FlatForward(settlementDate, 0.0, ql.Actual365Fixed())
underlying = ql.SimpleQuote(30.0)
volatility = ql.BlackConstantVol(todaysDate, ql.TARGET(), 0.20, ql.Actual365Fixed())


exerciseDates = [ql.Date(1, ql.January, 2019) + i for i in range(31)]

swingOption = ql.VanillaSwingOption(
    ql.VanillaForwardPayoff(ql.Option.Call, underlying.value()), ql.SwingExercise(exerciseDates), 0, len(exerciseDates)
)

bsProcess = ql.BlackScholesMertonProcess(
    ql.QuoteHandle(underlying),
    ql.YieldTermStructureHandle(dividendYield),
    ql.YieldTermStructureHandle(riskFreeRate),
    ql.BlackVolTermStructureHandle(volatility),
)

swingOption.setPricingEngine(ql.FdSimpleBSSwingEngine(bsProcess))

print("Black Scholes Price: {:f}".format(swingOption.NPV()))

x0 = 0.0
x1 = 0.0

beta = 4.0
eta = 4.0
jumpIntensity = 1.0
speed = 1.0
volatility = 0.1

curveShape = []
for d in exerciseDates:
    t = ql.Actual365Fixed().yearFraction(todaysDate, d)
    gs = (
        math.log(underlying.value())
        - volatility * volatility / (4 * speed) * (1 - math.exp(-2 * speed * t))
        - jumpIntensity / beta * math.log((eta - math.exp(-beta * t)) / (eta - 1.0))
    )
    curveShape.append((t, gs))

ouProcess = ql.ExtendedOrnsteinUhlenbeckProcess(speed, volatility, x0, lambda x: x0)
jProcess = ql.ExtOUWithJumpsProcess(ouProcess, x1, beta, jumpIntensity, eta)

swingOption.setPricingEngine(ql.FdSimpleExtOUJumpSwingEngine(jProcess, riskFreeRate, 25, 25, 200, curveShape))

print("Kluge Model Price  : {:f}".format(swingOption.NPV()))
