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

class AmericanQuantoOptionTest(unittest.TestCase):
    def setUp(self):
        self.today = ql.Date(21, ql.April, 2019)
        self.dc = ql.Actual365Fixed()
        ql.Settings.instance().evaluationDate = self.today

        self.domesticTS = ql.FlatForward(self.today, 0.025, self.dc)
        self.foreignTS = ql.FlatForward(self.today, 0.075, self.dc)
        self.fxVolTS = ql.BlackConstantVol(self.today, ql.TARGET(), 0.15, self.dc)

        self.quantoHelper = ql.FdmQuantoHelper(
            self.domesticTS, self.foreignTS, self.fxVolTS, -0.75, 1.0)

        self.divYieldTS = ql.FlatForward(self.today, 0.03, self.dc)

        divDate = ql.DateVector()
        divDate.push_back(self.today + ql.Period(6, ql.Months))

        divAmount = ql.DoubleVector()
        divAmount.push_back(8.0)

        maturityDate = self.today + ql.Period(9, ql.Months)

        self.option = ql.DividendVanillaOption(
            ql.PlainVanillaPayoff(ql.Option.Call, 105),
            ql.AmericanExercise(self.today, maturityDate),
            divDate,
            divAmount)


    def tearDown(self):
        ql.Settings.instance().evaluationDate = ql.Date()

    def testAmericanBSQuantoOption(self):
        """ Testing American Black-Scholes quanto option """

        volTS = ql.BlackConstantVol(self.today, ql.TARGET(), 0.3, self.dc)

        bsmProcess = ql.BlackScholesMertonProcess(
            ql.QuoteHandle(ql.SimpleQuote(100)),
            ql.YieldTermStructureHandle(self.divYieldTS),
            ql.YieldTermStructureHandle(self.domesticTS),
            ql.BlackVolTermStructureHandle(volTS))

        fdmBlackScholesEngine = ql.FdBlackScholesVanillaEngine(
            bsmProcess, self.quantoHelper, 100, 400, 1)

        self.option.setPricingEngine(fdmBlackScholesEngine)

        fdmPrice = self.option.NPV()
        expected = 8.90611734

        self.assertAlmostEqual(fdmPrice, expected, 3,
            msg="Unable to reproduce American BS quanto option price.")


    def testAmericanHestonQuantoOption(self):
        """ Testing American Heston quanto option """

        hestonModel = ql.HestonModel(
            ql.HestonProcess(
                ql.YieldTermStructureHandle(self.domesticTS),
                ql.YieldTermStructureHandle(self.divYieldTS),
                ql.QuoteHandle(ql.SimpleQuote(100)),
                0.09, 1.0, 0.09, 1e-4, 0.0))

        fdmHestonVanillaEngine = ql.FdHestonVanillaEngine(
            hestonModel, self.quantoHelper, 100, 400, 3, 1)

        self.option.setPricingEngine(fdmHestonVanillaEngine)

        fdmPrice = self.option.NPV()
        expected = 8.90611734

        self.assertAlmostEqual(fdmPrice, expected, 3,
            msg="Unable to reproduce American Heston quanto option price.")


if __name__ == '__main__':
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
