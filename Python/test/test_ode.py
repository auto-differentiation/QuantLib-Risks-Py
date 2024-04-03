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

class OdeTest(unittest.TestCase):

    def test1dODE(self):
        """ Testing one dimesnional ODE """

        yEnd = ql.RungeKutta(1e-8)(lambda x, y : y, 1, 0, 1)

        self.assertAlmostEqual(yEnd, math.exp(1), 5,
            msg="Unable to reproduce one dimensional ODE solution.")


    def test2dODE(self):
        """ Testing multi-dimesnional ODE """

        yEnd = ql.RungeKutta(1e-8)(lambda x, y : [y[1], -y[0]],
                                   [0, 1], 0, 0.5*math.pi)[0]

        self.assertAlmostEqual(yEnd, 1.0, 5,
            msg="Unable to reproduce multi-dimensional ODE solution.")


if __name__ == '__main__':
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
