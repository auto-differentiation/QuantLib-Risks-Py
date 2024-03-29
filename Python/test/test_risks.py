"""
Swap test with derivatives - based on the original swap.py sample.

 Copyright (&copy;) 2004, 2005, 2006, 2007 StatPro Italia srl
 Copyright (&copy;) 2024 Xcelerit Computing Limited.

This file is part of QuantLib-Risks, a Python wrapper for QuantLib enabled
for risk computation using automatic differentiation. It uses XAD,
a fast and comprehensive C++ library for automatic differentiation.

QuantLib-Risks and XAD are free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

QuantLib-Risks is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

QuantLib is free software: you can redistribute it and/or modify it under the
terms of the QuantLib license.  You should have received a copy of the
license along with this program; if not, please email
<quantlib-dev@lists.sf.net>. The license is also available online at
<https://www.quantlib.org/license.shtml>.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the license for more details.
 """

import unittest
import QuantLib_Risks as ql
from xad_autodiff.adj_1st import Tape

class SwapWithSensiTest(unittest.TestCase):
    def setUp(self):
        self.calendar = ql.TARGET()
        self.todaysDate = ql.Date(6, ql.November, 2001)
        ql.Settings.instance().evaluationDate = self.todaysDate
        self.settlementDate = ql.Date(8, ql.November, 2001)
    
    def testSwapPrice(self):
        with Tape() as tape:
            swaps_in = {
                (2, ql.Years):  ql.Real(0.037125),
                (3, ql.Years):  ql.Real(0.0398),
                (5, ql.Years):  ql.Real(0.0443),
                (10, ql.Years): ql.Real(0.05165),
                (15, ql.Years): ql.Real(0.055175),
            }
            tape.registerInputs(swaps_in.values())
            tape.newRecording()
            
            swaps = dict()
            for n, unit in swaps_in.keys():
                swaps[(n, unit)] = ql.SimpleQuote(swaps_in[(n, unit)])
                
            discountTermStructure = ql.YieldTermStructureHandle(
                ql.FlatForward(self.settlementDate, 0.04, ql.Actual360()))

            fixedLegFrequency = ql.Annual
            fixedLegTenor = ql.Period(1, ql.Years)
            fixedLegAdjustment = ql.Unadjusted
            fixedLegDayCounter = ql.Thirty360(ql.Thirty360.BondBasis)
            floatingLegTenor = ql.Period(3, ql.Months)
            floatingLegAdjustment = ql.ModifiedFollowing
            swapHelpers = [
                ql.SwapRateHelper(
                    ql.QuoteHandle(swaps[(n, unit)]),
                    ql.Period(n, unit),
                    self.calendar,
                    fixedLegFrequency,
                    fixedLegAdjustment,
                    fixedLegDayCounter,
                    ql.Euribor3M(),
                    ql.QuoteHandle(),
                    ql.Period("0D"),
                    discountTermStructure,
                )
                for n, unit in swaps.keys()
            ]
            
            forecastTermStructure = ql.RelinkableYieldTermStructureHandle()

            helpers = swapHelpers[1:]
            curve = ql.PiecewiseFlatForward(self.settlementDate, helpers, ql.Actual360())

            swapEngine = ql.DiscountingSwapEngine(discountTermStructure)

            nominal = 1000000
            length = 5
            maturity = self.calendar.advance(self.settlementDate, length, ql.Years)

            fixedLegFrequency = ql.Annual
            fixedLegAdjustment = ql.Unadjusted
            fixedLegDayCounter = ql.Thirty360(ql.Thirty360.BondBasis)
            fixedRate = 0.04

            spread = 0.0
            index = ql.Euribor3M(forecastTermStructure)
            floatingLegAdjustment = ql.ModifiedFollowing
            floatingLegDayCounter = index.dayCounter()

            fixedSchedule = ql.Schedule(
                self.settlementDate,
                maturity,
                fixedLegTenor,
                self.calendar,
                fixedLegAdjustment,
                fixedLegAdjustment,
                ql.DateGeneration.Forward,
                False,
            )
            floatingSchedule = ql.Schedule(
                self.settlementDate,
                maturity,
                floatingLegTenor,
                self.calendar,
                floatingLegAdjustment,
                floatingLegAdjustment,
                ql.DateGeneration.Forward,
                False,
            )

            spot = ql.VanillaSwap(
                ql.Swap.Payer,
                nominal,
                fixedSchedule,
                fixedRate,
                fixedLegDayCounter,
                floatingSchedule,
                index,
                spread,
                floatingLegDayCounter,
            )
            spot.setPricingEngine(swapEngine)
            
            forecastTermStructure.linkTo(curve)
            npv = spot.NPV()
            
            tape.registerOutput(npv)
            npv.derivative = 1.0
            tape.computeAdjoints()
            
            for k, v in swaps_in.items():
                if k[0] == 5 and k[1] == ql.Years:
                    self.assertGreater(v.derivative, 0.0)
                else:
                    self.assertAlmostEqual(v.derivative, 0.0, 3)