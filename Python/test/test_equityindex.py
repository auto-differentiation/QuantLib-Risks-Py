"""
 Copyright (C) 2023 Marcin Rybacki
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

import QuantLib_Risks as ql
import unittest


EPSILON = 1.e-2

CAL = ql.TARGET()
DCT = ql.Actual365Fixed()
VALUATION_DATE = CAL.adjust(ql.Date(31, ql.January, 2023))


def flat_rate(rate):
    return ql.FlatForward(
        2, CAL, ql.QuoteHandle(ql.SimpleQuote(rate)), DCT)


class EquityIndexTest(unittest.TestCase):
    def setUp(self):
        ql.Settings.instance().evaluationDate = VALUATION_DATE

        self.interest_handle = ql.YieldTermStructureHandle(flat_rate(0.03))
        self.dividend_handle = ql.YieldTermStructureHandle(flat_rate(0.01))
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(8690.0))

        ql.IndexManager.instance().clearHistory("eq_idx")
        self.equity_idx = ql.EquityIndex(
            "eq_idx", CAL, self.interest_handle, self.dividend_handle, spot_handle)

    def test_equity_index_inspectors(self):
        """Testing equity index inspectors"""
        fail_msg = "Unable to replicate the properties of an equity index."

        self.assertEqual(self.equity_idx.name(), "eq_idx", msg=fail_msg)
        self.assertEqual(self.equity_idx.fixingCalendar(), CAL, msg=fail_msg)

    def test_equity_index_projections(self):
        """Testing equity index projections"""
        fail_msg = "Failed to calculate the expected index projection."

        self.assertAlmostEqual(
            self.equity_idx.fixing(VALUATION_DATE), 8690.0, delta=EPSILON, msg=fail_msg)

        future_dt = ql.Date(20, ql.May, 2030)
        self.assertAlmostEqual(
            self.equity_idx.fixing(future_dt),  10055.76, delta=EPSILON, msg=fail_msg)


if __name__ == '__main__':
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
