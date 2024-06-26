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

import unittest
import QuantLib_Risks as ql


class Foo:
    def __call__(self, x):
        return x * x - 1.0

    def derivative(self, x):
        return 2.0 * x


class Solver1DTest(unittest.TestCase):
    def test_solve(self):
        "Testing 1-D solvers"
        for factory in [ql.Brent, ql.Bisection, ql.FalsePosition, ql.Ridder, ql.Secant]:
            solver = factory()
            for accuracy in [1.0e-4, 1.0e-6, 1.0e-8]:
                root = solver.solve(lambda x: x * x - 1.0, accuracy, 1.5, 0.1)
                if not (abs(root - 1.0) < accuracy):
                    self.fail(
                        """
%(factory)s
    solve():
    expected:         1.0
    calculated root:  %(root)g
    accuracy:         %(accuracy)s
                          """
                        % locals()
                    )
                root = solver.solve(lambda x: x * x - 1.0, accuracy, 1.5, 0.0, 1.0)
                if not (abs(root - 1.0) < accuracy):
                    self.fail(
                        """
%(factory)s
    bracketed solve():
    expected:         1.0
    calculated root:  %(root)g
    accuracy:         %(accuracy)s
                          """
                        % locals()
                    )
        for factory in [ql.Newton, ql.NewtonSafe]:
            solver = factory()
            for accuracy in [1.0e-4, 1.0e-6, 1.0e-8]:
                root = solver.solve(Foo(), accuracy, 1.5, 0.1)
                if not (abs(root - 1.0) < accuracy):
                    self.fail(
                        """
%(factory)s
    solve():
    expected:         1.0
    calculated root:  %(root)g
    accuracy:         %(accuracy)s
                          """
                        % locals()
                    )
                root = solver.solve(Foo(), accuracy, 1.5, 0.0, 1.0)
                if not (abs(root - 1.0) < accuracy):
                    self.fail(
                        """
%(factory)s
    bracketed solve():
    expected:         1.0
    calculated root:  %(root)g
    accuracy:         %(accuracy)s
                          """
                        % locals()
                    )


if __name__ == "__main__":
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
