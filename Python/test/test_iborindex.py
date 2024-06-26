# coding=utf-8-unix
"""
 Copyright (C) 2018 Wojciech Ślusarski
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


class IborIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.euribor3m = ql.Euribor3M()

    def setUp(self):
        self.euribor3m.clearFixings()
        # values are not real due to copyrights of the fixing
        self.euribor3m.addFixing(ql.Date(17, 7, 2018), -0.3)
        self.euribor3m.addFixings([ql.Date(12, 7, 2018), ql.Date(13, 7, 2018)], [-0.3, -0.3])

    def testAddFixingFail(self):
        """Testing for RuntimeError while trying to overwrite fixing value"""

        with self.assertRaises(RuntimeError):
            # attempt to overwrite value that is already set at different level
            self.euribor3m.addFixing(ql.Date(17, 7, 2018), -0.4)

        with self.assertRaises(RuntimeError):
            # attempt to overwrite value that is already set at different level
            self.euribor3m.addFixings([ql.Date(12, 7, 2018), ql.Date(13, 7, 2018)], [-0.4, -0.4])

    def testAddFixing(self):
        """Testing for overwriting fixing value"""

        force_overwrite = True
        try:
            # attempt to overwrite value that is already set at different level
            self.euribor3m.addFixing(ql.Date(17, 7, 2018), -0.4, force_overwrite)
            self.euribor3m.addFixings([ql.Date(12, 7, 2018), ql.Date(13, 7, 2018)], [-0.4, -0.4], force_overwrite)
            # try clearFixings and repeat with original levels
            self.euribor3m.clearFixings()
            self.euribor3m.addFixing(ql.Date(17, 7, 2018), -0.3)
            self.euribor3m.addFixings([ql.Date(12, 7, 2018), ql.Date(13, 7, 2018)], [-0.3, -0.3])

        except RuntimeError as err:
            raise AssertionError("Failed to overwrite index fixixng " + "{}".format(err))

    def testTimeSeries(self):
        """Testing for getting time series of the fixing"""

        dates = (ql.Date(12, 7, 2018), ql.Date(13, 7, 2018), ql.Date(17, 7, 2018))
        values = (-0.3, -0.3, -0.3)
        for expected, actual in zip(dates, self.euribor3m.timeSeries().dates()):
            self.assertTrue(expected == actual)
        for expected, actual in zip(values, self.euribor3m.timeSeries().values()):
            self.assertTrue(expected == actual)


if __name__ == "__main__":
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
