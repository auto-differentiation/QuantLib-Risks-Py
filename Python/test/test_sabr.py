"""
 Copyright (C) 2019 Klaus Spanderen
 Copyright (C) 2024 Xcelerit Computing Limited.

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

 QuantLib is free software: you can redistribute it and/or modify it
 under the terms of the QuantLib license.  You should have received a
 copy of the license along with this program; if not, please email
 <quantlib-dev@lists.sf.net>. The license is also available online at
 <http://quantlib.org/license.shtml>.

 This program is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the license for more details.
"""

import unittest

import QuantLib_Risks as ql
if ql.XAD_ENABLED:
    from xad import math
else:
    import math

class SabrTest(unittest.TestCase):

    def testHagenFormula(self):
        """ Testing Hagen et al. formula """

        today = ql.Date(9,1,2019)
        dc = ql.Actual365Fixed()
        maturityDate = today + ql.Period(6, ql.Months)
        maturityTime = dc.yearFraction(today, maturityDate)

        alpha = 0.35
        beta = 0.85
        nu = 0.75
        rho = 0.85
        f0 = 100.0
        strike = 110.0

        sabrVol = ql.sabrVolatility(strike, f0, maturityTime, alpha, beta, nu, rho)

        self.assertAlmostEqual(sabrVol, 0.205953, 6,
                               msg="Unable to reproduce Hagen et al. SABR volatility")

        flochKennedyVol = ql.sabrFlochKennedyVolatility(
            strike, f0, maturityTime, alpha, beta, nu, rho)

        self.assertAlmostEqual(flochKennedyVol, 0.205447, 6,
                               msg="Unable to reproduce Le Floc'h-Kennedy SABR volatility")

    def testPdeSolver(self):
        """ Testing BENCHOP-SLV SABR example value """

        today = ql.Date(8, 1, 2019)
        dc = ql.Actual365Fixed()
        maturityDate = today + ql.Period(10 * 365, ql.Days)
        maturityTime = dc.yearFraction(today, maturityDate)

        f0 = 0.07
        alpha = 0.4
        nu = 0.8
        beta = 0.5
        rho = -0.6
        strike = f0 * math.exp(-0.1 * math.sqrt(maturityTime))

        rTS = ql.YieldTermStructureHandle(ql.FlatForward(today, 0.0, dc))

        # see https://ir.cwi.nl/pub/28249
        expected = 0.052450313614407

        option = ql.VanillaOption(
            ql.PlainVanillaPayoff(ql.Option.Call, strike),
            ql.EuropeanExercise(maturityDate))

        option.setPricingEngine(ql.FdSabrVanillaEngine(f0, alpha, beta, nu, rho, rTS, 30, 800, 30, 1, 0.8))

        calculated = option.NPV()

        self.assertAlmostEqual(calculated, expected, 4,
                               msg="Unable to reproduce Le Floc'h-Kennedy SABR volatility")


    def testSabrPdeVsCevPdeVsAnalyticCev(self):
        """ Testing SABR PDE vs CEV PDE vs Analytic CEV """

        today = ql.Date(1, 3, 2019)
        dc = ql.Actual365Fixed()

        maturityDate = today + ql.Period(12, ql.Months)
        f0 = 1.2
        alpha = 0.35
        beta = 0.9
        nu = 1e-3
        rho = 0.25
        strike = 1.1

        rTS = ql.YieldTermStructureHandle(ql.FlatForward(today, 0.05, dc))

        option = ql.VanillaOption(
            ql.PlainVanillaPayoff(ql.Option.Call, strike),
            ql.EuropeanExercise(maturityDate))

        option.setPricingEngine(ql.FdSabrVanillaEngine(f0, alpha, beta, nu, rho, rTS, 30, 400, 3))
        fdSabrNPV = option.NPV()

        option.setPricingEngine(ql.FdCEVVanillaEngine(f0, alpha, beta, rTS, 30, 400))
        fdCevNPV = option.NPV()

        option.setPricingEngine(ql.AnalyticCEVEngine(f0, alpha, beta, rTS))
        analyticCevNPV = option.NPV()

        self.assertAlmostEqual(fdSabrNPV, analyticCevNPV, 4,
                               msg="Unable to match PDE SABR value with analytic CEV value")

        self.assertAlmostEqual(fdCevNPV, analyticCevNPV, 4,
                               msg="Unable to match PDE CEV value with analytic CEV value")

if __name__ == '__main__':
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
