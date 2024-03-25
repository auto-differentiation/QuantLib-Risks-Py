"""
 This file is part of quantlib-risks, a Python wrapper for QuantLib enabled
 for risk computation using automatic differentiation. It uses XAD,
 a fast and comprehensive C++ library for automatic differentiation.

 quantlib-risks and XAD are free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 quantlib-risks is distributed in the hope that it will be useful,
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

import quantlib_risks as ql
import unittest


class DayCountersTest(unittest.TestCase):
    def test_bus252(self):
        """Test Business252 daycounter"""

        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)

        #
        # Check that SWIG signature for Business252 calendar allows to
        # pass custom calendar into the class constructor.  Old
        # QuantLib-SWIG versions allow only to create Business252
        # calendar with default constructor parameter (Brazil
        # calendar), and generate an exception when trying to pass a
        # custom calendar as a parameter. So we just check here that
        # no exception occurs.
        #
        ql.Business252(calendar)


if __name__ == "__main__":
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
