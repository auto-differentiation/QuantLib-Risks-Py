/******************************************************************************
 *   Extra type converters for Dates that are needed with QuantLib-Risks in order
 *   to cover pair<Date, Real> and vectors thereof. The functions are declared in
 *   converters.hpp
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

#ifndef quantlib_date_extra_i
#define quantlib_date_extra_i

%{

PyObject* convert_to_SwigDate(const Date& date) {
   return SWIG_NewPointerObj(
    (new Date(static_cast< const Date& >(date))), 
    SWIGTYPE_p_Date, 
    SWIG_POINTER_OWN |  0 );
}

Date convert_to_QlDate(PyObject* obj) {
   void* argp1 = nullptr;
   int res1 = SWIG_ConvertPtr(obj, &argp1,SWIGTYPE_p_Date, 0 |  0 );
   if (!SWIG_IsOK(res1)) {
    throw std::runtime_error("error in date conversion"); 
  }
  Date *arg1 = reinterpret_cast<Date*>(argp1);
  return *arg1;
}

PyObject* make_date_real_pair_tuple(const std::pair<QuantLib::Date, Real>& p) {
    auto t = PyTuple_New(2);
    PyTuple_SET_ITEM(t, 0, convert_to_SwigDate(p.first));
    PyTuple_SET_ITEM(t, 1, make_PyObject(p.second));
    return t;
}

std::pair<Date, Real> make_date_real_pair_from_tuple(PyObject* obj) {
    Date d = convert_to_QlDate(PyTuple_GetItem(obj, 0));
    Real r = make_Real(PyTuple_GetItem(obj, 1));
    return {d, r};
}

bool check_date_real_pair_input(PyObject* obj)
{
    if (!PyTuple_Check(obj))
        return false;
    if (PyTuple_Size(obj) != 2)
        return false;
    if (!check_Real(PyTuple_GetItem(obj, 1)))
        return false;
   void* argp1 = nullptr;
   int res1 = SWIG_ConvertPtr(obj, &argp1,SWIGTYPE_p_Date, 0 |  0 );
   if (!SWIG_IsOK(res1))
       return false;
   return true;
}

%}

%typemap(in) std::pair<Date, Real> {
    if (PyTuple_Check($input) && PyTuple_Size($input) == 2) {
        $1 = make_date_real_pair_from_tuple($input);
    } else {
        SWIG_exception(SWIG_TypeError, "Could not convert to date/Real pair")
    }
}

%typemap(in) const std::pair<Date, Real>& (std::pair<Date, Real> temp) {
    if (PyTuple_Check($input) && PyTuple_Size($input) == 2) {
        temp = make_date_real_pair_from_tuple($input);
        $1 = &temp;

    } else {
        SWIG_exception(SWIG_TypeError, "Could not convert to date/Real pair")
    }
}

%typemap(out) std::pair<Date, Real> {
    $result = make_date_real_pair_tuple($1);
}

%define QL_TYPECHECK_REALDATEOBJ_PAIR 4993 %enddef

%typecheck(QL_TYPECHECK_REALDATEOBJ_PAIR) std::pair<Date, Real>, const std::pair<Date, Real>& {
    $1 = check_date_real_pair_input($input) ? 1 : 0;
}

#endif