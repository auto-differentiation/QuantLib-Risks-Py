/******************************************************************************
 *   Extra type converters for vectors of tuples of Real, Real, bool - required
 *   for QuantLib-Risks.
 *
 *  This file is part of QuantLib-Risks, a Python wrapper for QuantLib enabled
 *  for risk computation using automatic differentiation. It uses XAD,
 *  a fast and comprehensive C++ library for automatic differentiation.
 *
 *  Copyright (C) 2010-2024 Xcelerit Computing Ltd.
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as published
 *  by the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *   
 ******************************************************************************/

#ifndef fdm_extra_i
#define fdm_extra_i

%{
    #include "converters.hpp"
%}

%typemap(in) const std::vector<ext::tuple<Real, Real, bool> >& (std::vector<ext::tuple<Real, Real, bool>> temp) {
    try {
        if (PyList_Check($input)) {
            temp = make_mesher_point_vector_from_list($input);
            $1 = &temp;
        } 
        else 
          SWIG_exception(SWIG_TypeError, "vector of Concentrating1dMesherPoint tuples expected");
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "vector of Real expected");
    }
}

%define QL_TYPECHECK_CONC_VEC 4993 %enddef

%typecheck(QL_TYPECHECK_CONC_VEC) const std::vector<ext::tuple<Real, Real, bool> >&
{
    $1 = mesher_point_vector_check($input) ? 1 : 0;
}

#endif