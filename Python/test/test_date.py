"""
 Copyright (C) 2000, 2001, 2002, 2003 RiskMap srl
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


class DateTest(unittest.TestCase):
    def setUp(self):
        pass

    def testArithmetics(self):
        "Testing date arithmetics"
        today = ql.Date.todaysDate()
        date = today - ql.Period(30, ql.Years)
        end_date = today + ql.Period(30, ql.Years)

        dold = date.dayOfMonth()
        mold = date.month()
        yold = date.year()

        while date < end_date:
            date += 1

            d = date.dayOfMonth()
            m = date.month()
            y = date.year()

            # check if skipping any date
            if not (
                (d == dold + 1 and m == mold and y == yold)
                or (d == 1 and m == mold + 1 and y == yold)
                or (d == 1 and m == 1 and y == yold + 1)
            ):
                self.fail(
                    """
wrong day, month, year increment
    date: %(t)s
    day, month, year: %(d)d, %(m)d, %(y)d
    previous:         %(dold)d, %(mold)d, %(yold)d
                """
                    % locals()
                )
            dold = d
            mold = m
            yold = y

    def testHolidayList(self):
        """ Testing Calendar testHolidayList() method. """
        holidayLstFunction = ql.Calendar.holidayList(ql.Poland(), ql.Date(31, 12, 2014), ql.Date(3, 4, 2015), False)
        holidayLstManual = (ql.Date(1, 1, 2015), ql.Date(6, 1, 2015))
        # check if dates both from function and from manual imput are the same
        self.assertTrue(all([(a == b) for a, b in zip(holidayLstFunction, holidayLstManual)]))

    def tearDown(self):
        pass


if __name__ == "__main__":
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
