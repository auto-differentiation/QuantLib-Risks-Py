/******************************************************************************
 *  Extra type converters for vectors of date/Real pairs. 
 *
 *  This file is part of quantlib-risks, a Python wrapper for QuantLib enabled
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

#ifndef vectors_extra_i
#define vectors_extra_i

%{
    #include "converters.hpp"
%}

%init {
    add_to_module(m);
}

%{

PyObject* make_PyList_pair_date_vector(const std::vector<std::pair<QuantLib::Date, Real>>& v)
{
  auto l = PyList_New(v.size());
  for (size_t i = 0; i < v.size(); ++i) {
    auto t = make_date_real_pair_tuple(v[i]);
    PyList_SET_ITEM(l, i, t);
  }
  return l;
}

std::vector<std::pair<QuantLib::Date, Real>> make_date_real_pair_vector_from_list(PyObject* obj)
{
    std::vector<std::pair<QuantLib::Date, Real>> ret;
    auto l = PyList_Size(obj);
    ret.reserve(l);
    for (size_t i = 0; i < l; ++i)
    {
        auto t = PyList_GetItem(obj, i);
        // tuple(Date, Real)
        ret.emplace_back(make_date_real_pair_from_tuple(t));
    }
    return ret;
}

bool check_date_real_pair_list(PyObject* obj)
{
    if (!PyList_Check(obj))
        return false;
    auto l = PyList_Size(obj);
    for (size_t i = 0; i < l; ++i) {
        auto t = PyList_GetItem(obj, i);
        if (!check_date_real_pair_input(t))
            return false;
    }
    return true;
}

%}

%typemap(in) std::vector<Real> {
    try {
        if (PyList_Check($input)) {
            $1 = make_Real_vector_from_list($input);
        } else if (PyTuple_Check($input)) {
            $1 = make_Real_vector_from_tuple($input);
        } else {
            $1 = make_Real_vector_ref($input);
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "vector of Real expected");
    }
}

%typemap(in) const std::vector<Real>& (std::vector<Real> temp) {
    try {
        if (PyList_Check($input)) {
            temp = make_Real_vector_from_list($input);
            $1 = &temp;
        } else if (PyTuple_Check($input)) {
            temp = make_Real_vector_from_tuple($input);
            $1 = &temp;
        } else {
            $1 = &make_Real_vector_ref($input);
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "vector of Real expected");
    }
}

%typemap(in) std::vector<std::pair<Real,Real>> {
    try {
        if (PyList_Check($input)) {
            $1 = make_DoublePairVector_from_list($input);
        } else if (PyTuple_Check($input)) {
            $1 = make_DoublePairVector_from_tuple($input);
        } else {
            $1 = make_DoublePairVector_ref($input);
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "vector of Real pairs expected");
    }
}

%typemap(in) const std::vector<std::pair<Real,Real>>& (std::vector<std::pair<Real,Real>> temp) {
    try {
        if (PyList_Check($input)) {
            temp = make_DoublePairVector_from_list($input);
            $1 = &temp;
        } else if (PyTuple_Check($input)) {
            temp = make_DoublePairVector_from_tuple($input);
            $1 = &temp;
        } else {
            $1 = &make_DoublePairVector_ref($input);
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "vector of Real pairs expected");
    }
}

%typemap(in) std::vector<std::vector<Real>> {
    try {
        if (PyList_Check($input)) {
            $1 = make_DoubleVectorVector_from_list($input);
        } else if (PyTuple_Check($input)) {
            $1 = make_DoubleVectorVector_from_tuple($input);
        } else {
            $1 = make_DoubleVectorVector_ref($input);
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "vector of vector of Real expected");
    }
}

%typemap(in) const std::vector<std::vector<Real>>& (std::vector<std::vector<Real>> temp) {
    try {
        if (PyList_Check($input)) {
            temp = make_DoubleVectorVector_from_list($input);
            $1 = &temp;
        } else if (PyTuple_Check($input)) {
            temp = make_DoubleVectorVector_from_tuple($input);
            $1 = &temp;
        } else {
            $1 = &make_DoubleVectorVector_ref($input);
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "vector of vector of Real expected");
    }
}

///

%typemap(in) std::pair<std::vector<Real>, std::vector<Real>> {
    try {
        if (PyList_Check($input)) {
            $1 = make_PairDoubleVector_from_list($input);
        } else if (PyTuple_Check($input)) {
            $1 = make_PairDoubleVector_from_tuple($input);
        } else {
            $1 = make_PairDoubleVector_ref($input);
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "pair of vector of Real expected");
    }
}

%typemap(in) const std::pair<std::vector<Real>, std::vector<Real>>& (std::pair<std::vector<Real>, std::vector<Real>> temp) {
    try {
        if (PyList_Check($input)) {
            temp = make_PairDoubleVector_from_list($input);
            $1 = &temp;
        } else if (PyTuple_Check($input)) {
            temp = make_PairDoubleVector_from_tuple($input);
            $1 = &temp;
        } else {
            $1 = &make_PairDoubleVector_ref($input);
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "pair vector of Real expected");
    }
}

%define QL_TYPECHECK_REALOBJ_VEC 4991 %enddef
%define QL_TYPECHECK_REALOBJ_PAIR 4992 %enddef
%define QL_TYPECHECK_DATE_REAL_VEC 4997 %enddef
%define QL_TYPECHECK_REALOBJ_PAIR_VEC 4997 %enddef
%define QL_TYPECHECK_REALOBJ_VEC_VEC 4997 %enddef
%define QL_TYPECHECK_REALOBJ_PAIR_VEC_VEC 4997 %enddef

%typecheck(QL_TYPECHECK_REALOBJ_VEC) const std::vector<Real>&, std::vector<Real>
{
    $1 = check_Real_vector($input) ? 1 : 0;
}

%typecheck(QL_TYPECHECK_REALOBJ_PAIR_VEC) const std::vector<std::pair<Real,Real>>&, std::vector<std::pair<Real,Real>>
{
    $1 = check_DoublePairVector($input) ? 1 : 0;
}

%typecheck(QL_TYPECHECK_REALOBJ_VEC_VEC) const std::vector<std::pair<Real,Real>>&, std::vector<std::pair<Real,Real>>
{
    $1 = check_DoubleVectorVector($input) ? 1 : 0;
}

%typecheck(QL_TYPECHECK_REALOBJ_PAIR_VEC_VEC) const std::pair<std::vector<Real>, std::vector<Real>>&, std::pair<std::vector<Real>, std::vector<Real>>
{
    $1 = check_PairDoubleVector($input) ? 1 : 0;
}

%typemap(out) std::vector<Real> {
    $result = make_PyTuple_Real_vector($1);
}

%typemap(out) const std::vector<Real>& {
    $result = make_PyTuple_Real_vector(*$1);
}

%typemap(out) std::vector<Real>& {
    $result = make_PyObject_Real_vector($1);
}

%typemap(out) std::vector<std::pair<Real,Real>> {
    $result = make_PyTuple_DoublePairVector($1);
}

%typemap(out) const std::vector<std::pair<Real,Real>>& {
    $result = make_PyTuple_DoublePairVector(*$1);
}

%typemap(out) std::vector<std::pair<Real,Real>>& {
    $result = make_PyObject_DoublePairVector($1);
}

%typemap(out) std::vector<std::vector<Real>> {
    $result = make_PyTuple_DoubleVectorVector($1);
}

%typemap(out) const std::vector<std::vector<Real>>& {
    $result = make_PyTuple_DoubleVectorVector(*$1);
}

%typemap(out) std::vector<std::vector<Real>>& {
    $result = make_PyObject_DoubleVectorVector($1);
}

%typemap(out) std::pair<std::vector<Real>, std::vector<Real>> {
    $result = make_PyTuple_PairDoubleVector($1);
}

%typemap(out) const std::pair<std::vector<Real>, std::vector<Real>>& {
    $result = make_PyTuple_PairDoubleVector(*$1);
}

%typemap(out) std::pair<std::vector<Real>, std::vector<Real>>& {
    $result = make_PyObject_PairDoubleVector($1);
}

%typemap(in) std::pair<Real, Real> {
    try {
        if (PyTuple_Check($input)) {
            $1 = make_Real_pair_from_tuple($input);
        } 
        else if (PyList_Check($input)) {
            $1 = make_Real_pair_from_list($input);
        } else {
            SWIG_exception(SWIG_TypeError, "Only tuples or lists can be converted to pairs");
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "tuple or list with 2 elements expected for pair initializer");
    }
}

%typemap(in) const std::pair<Real, Real>& (std::pair<Real, Real> temp) {
    try {
        if (PyTuple_Check($input)) {
            temp = make_Real_pair_from_tuple($input);
            $1 = &temp;
        } 
        else if (PyList_Check($input)) {
            temp = make_Real_pair_from_list($input);
            $1 = &temp;
        } else {
            SWIG_exception(SWIG_TypeError, "Only tuples or lists can be converted to pairs");
        }
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "tuple or list with 2 elements expected for pair initializer");
    }
}

%typecheck(QL_TYPECHECK_REALOBJ_PAIR) std::pair<Real, Real>, const std::pair<Real, Real>&
{
    $1 = check_Real_pair($input) ? 1 : 0;
}

%typemap(out) std::pair<Real, Real> {
    $result = make_PyTuple_Real_pair($1);
}

%typemap(in) const std::vector<std::pair<Date, Real>>& (std::vector<std::pair<Date, Real>> temp)
{
    try {
        temp = make_date_real_pair_vector_from_list($1);
        $1 = &temp;
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "type conversion error from list of tuples of Date, Real");
    }

}

%typemap(in) std::vector<std::pair<Date, Real>>
{
    try {
        $1 = make_date_real_pair_vector_from_list($1);
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "type conversion error from list of tuples of Date, Real");
    }

}

%typemap(out) std::vector<std::pair<Date, Real>>, const std::vector<std::pair<Date, Real>>
{
    $result = make_PyList_pair_date_vector($1);
}

%typecheck(QL_TYPECHECK_REALOBJ_VEC) const std::vector<std::pair<Date, Real>>&
{
    $1 = check_date_real_pair_list($input) ? 1 : 0;
}

#endif