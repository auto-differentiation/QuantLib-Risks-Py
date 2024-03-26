"""
 Copyright (C) 2023 Skandinaviska Enskilda Banken AB (publ)
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
import itertools
import unittest

import QuantLib_Risks as ql


class JointCalendarTest(unittest.TestCase):

    def test_joint_calendar_holidays(self):
        base_calendars = [ql.Sweden(), ql.Denmark(), ql.Finland(), ql.Norway(), ql.Iceland()]
        joint_nordics = ql.JointCalendar(base_calendars)
        start_date = ql.Date(1, ql.January, 2023)
        end_date = ql.Date(31, ql.December, 2023)

        joint_holidays = set(joint_nordics.holidayList(start_date, end_date))
        base_holidays = [calendar.holidayList(start_date, end_date) for calendar in base_calendars]
        base_holidays = set(itertools.chain.from_iterable(base_holidays))
        for holiday in base_holidays:
            self.assertIn(holiday, joint_holidays)


class ResetBespokeCalendarTest(unittest.TestCase):

    def test_reset_added_holidays(self):
        calendar = ql.BespokeCalendar("bespoke thing")

        test_date: ql.Date = ql.Date(1, ql.January, 2024)
        self.assertFalse(calendar.isHoliday(test_date))
        calendar.addHoliday(test_date)
        self.assertTrue(calendar.isHoliday(test_date))
        # TODO: Can extend test with this, if exposed:
        # self.assertEqual(len(calendar.addedHolidays()), 1)
        calendar.resetAddedAndRemovedHolidays()
        self.assertFalse(calendar.isHoliday(test_date))


if __name__ == "__main__":
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
