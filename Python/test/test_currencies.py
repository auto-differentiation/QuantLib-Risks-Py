"""
 Copyright (C) 2021 Marcin Rybacki
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


class CurrencyTest(unittest.TestCase):

    def test_default_currency_constructor(self):
        """Testing default currency constructor"""
        fail_msg = "Failed to create default currency."
        default_ccy = ql.Currency()
        self.assertTrue(default_ccy.empty(), fail_msg)

    def test_eur_constructor(self):
        """Testing EUR constructor"""
        fail_msg = "Failed to create EUR currency."
        eur = ql.EURCurrency()
        self.assertFalse(eur.empty(), fail_msg)

    def test_bespoke_currency_constructor(self):
        """Testing bespoke currency constructor"""
        fail_msg = "Failed to create bespoke currency."
        custom_ccy = ql.Currency(
            "CCY", "CCY", 100, "#", "", 100, ql.Rounding(), "")
        self.assertFalse(custom_ccy.empty(), fail_msg)


if __name__ == '__main__':
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
