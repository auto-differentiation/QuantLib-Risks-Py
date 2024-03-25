
/*
 Copyright (C) 2000, 2001, 2002, 2003 RiskMap srl

 This file is part of QuantLib, a free-software/open-source library
 for financial quantitative analysts and developers - http://quantlib.org/

 QuantLib is free software: you can redistribute it and/or modify it
 under the terms of the QuantLib license.  You should have received a
 copy of the license along with this program; if not, please email
 <quantlib-dev@lists.sf.net>. The license is also available online at
 <http://quantlib.org/license.shtml>.

 This program is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the license for more details.
*/

#ifndef quantlib_types_i
#define quantlib_types_i

%include common.i
%include std_common.i

%{
using QuantLib::Integer;
using QuantLib::BigInteger;
using QuantLib::Natural;
using QuantLib::BigNatural;
using QuantLib::Real;
using QuantLib::Decimal;
using QuantLib::Time;
using QuantLib::Rate;
using QuantLib::Spread;
using QuantLib::DiscountFactor;
using QuantLib::Volatility;
using QuantLib::Probability;
using QuantLib::Size;
%}

typedef int Integer;
typedef long BigInteger;
typedef unsigned int Natural;
typedef unsigned long BigNatural;
#ifdef QL_XAD
typedef xad::AReal<double> Real;
#define XAD_ENABLED 1
#else
typedef double Real;
#define XAD_ENABLED 0
#endif

typedef Real Decimal;
typedef Real Time;
typedef Real Rate;
typedef Real Spread;
typedef Real DiscountFactor;
typedef Real Volatility;
typedef Real Probability;

#if defined(SWIGPYTHON)
// needed for those using SWIG 1.3.21 in order to compile with VC++6
%typecheck(SWIG_TYPECHECK_INTEGER) std::size_t {
    $1 = (PyInt_Check($input) || PyLong_Check($input)) ? 1 : 0;
}
#endif

#if defined(SWIGPYTHON)
typedef size_t Size;
#else
typedef std::size_t Size;
#endif

#ifdef QL_XAD

%{
    #include "converters.hpp"
%}

%typemap(in) Real, xad::AReal<double> {
    try {
        $1 = make_Real($input);
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "active Real, float, or long expected");
    }
}

%typemap(in) const Real& (Real temp) {
    try {
        temp = make_Real($input);
        $1 = &temp;
    } catch(...) {
        SWIG_exception(SWIG_TypeError, "active Real, float, or long expected");
    }

}

%define QL_TYPECHECK_REALOBJ 4990 %enddef

%typemap(out) Real, xad::AReal<double> {
    $result = make_PyObject($1);
}

%typecheck(QL_TYPECHECK_REALOBJ) Real, xad::AReal<double>, const Real&
{
    $1 = PyFloat_Check($input) || PyLong_Check($input) || check_Real($input) ? 1 : 0;
}
#endif

#endif