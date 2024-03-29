/******************************************************************************
 *   Type converters and checks for the SWIG interface, interacting with XAD's
 *   Pybind11 based bindings.
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

#pragma once
#include <XAD/XAD.hpp>
#include <tuple>
#include <utility>
#include <vector>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef xad::AReal<double> Real;

// adds additional definitions to the QuantLib module at init time
void add_to_module(PyObject *mdef);

Real make_Real(PyObject *obj);
bool check_Real(PyObject *obj);
bool check_Real_pair(PyObject *obj);
PyObject *make_PyObject(const Real &x);

////////////////////// Vectors Real ////////////////////

// converter ql.DoubleVector -> std::vector
std::vector<Real> &make_Real_vector_ref(PyObject *obj);

// converter std::vector& -> ql.DoubleVector
PyObject *make_PyObject_Real_vector(std::vector<Real> &v);

// converter const std::vector& -> python list
PyObject *make_PyList_Real_vector(const std::vector<Real> &v);

// converter const std::vector& -> python tuple
PyObject *make_PyTuple_Real_vector(const std::vector<Real> &v);

// converter python list -> std::vector
std::vector<Real> make_Real_vector_from_list(PyObject *obj);

// converter python tuple -> std::vector
std::vector<Real> make_Real_vector_from_tuple(PyObject *obj);

// check if the obj is a ql.DoubleVector
bool check_Real_vector(PyObject *obj);

//////////////////// DoublePairVector /////////////////

using DoublePairVector = std::vector<std::pair<Real, Real>>;

DoublePairVector &make_DoublePairVector_ref(PyObject *obj);
DoublePairVector make_DoublePairVector_from_list(PyObject *obj);
DoublePairVector make_DoublePairVector_from_tuple(PyObject *obj);
PyObject *make_PyObject_DoublePairVector(DoublePairVector &v);
PyObject *make_PyList_DoublePairVector(const DoublePairVector &v);
PyObject *make_PyTuple_DoublePairVector(const DoublePairVector &v);
bool check_DoublePairVector(PyObject *obj);

//////////////////// DoubleVectorVector /////////////////

using DoubleVectorVector = std::vector<std::vector<Real>>;

DoubleVectorVector &make_DoubleVectorVector_ref(PyObject *obj);
DoubleVectorVector make_DoubleVectorVector_from_list(PyObject *obj);
DoubleVectorVector make_DoubleVectorVector_from_tuple(PyObject *obj);
PyObject *make_PyObject_DoubleVectorVector(DoubleVectorVector &v);
PyObject *make_PyList_DoubleVectorVector(const DoubleVectorVector &v);
PyObject *make_PyTuple_DoubleVectorVector(const DoubleVectorVector &v);
bool check_DoubleVectorVector(PyObject *obj);

//////////////////// PairDoubleVector /////////////////

using PairDoubleVector = std::pair<std::vector<Real>, std::vector<Real>>;

PairDoubleVector &make_PairDoubleVector_ref(PyObject *obj);
PairDoubleVector make_PairDoubleVector_from_list(PyObject *obj);
PairDoubleVector make_PairDoubleVector_from_tuple(PyObject *obj);
PyObject *make_PyObject_PairDoubleVector(PairDoubleVector &v);
PyObject *make_PyTuple_PairDoubleVector(const PairDoubleVector &v);
bool check_PairDoubleVector(PyObject *obj);


///////////////////// Pairs /////////////////////////

// convert tuple -> std::pair
std::pair<Real, Real> make_Real_pair_from_tuple(PyObject *obj);

// convert list -> std::pair
std::pair<Real, Real> make_Real_pair_from_list(PyObject *obj);

// convert std::pair -> tuple
PyObject *make_PyTuple_Real_pair(const std::pair<Real, Real> &p);

// check if object is convertible to std::pair<Real, Real>
bool Real_pair_check(PyObject *obj);

/////////////////// Concentrating1dMesherPointVector ////////////////
std::vector<std::tuple<Real, Real, bool>>
make_mesher_point_vector_from_list(PyObject *obj);

bool mesher_point_vector_check(PyObject *obj);

/////////////////// Dates ///////////////////
namespace QuantLib {
class Date;
}

PyObject *convert_to_SwigDate(const QuantLib::Date &date);

PyObject *make_date_real_pair_tuple(const std::pair<QuantLib::Date, Real> &p);
std::pair<QuantLib::Date, Real> make_date_real_pair_from_tuple(PyObject *obj);
bool check_date_real_pair_input(PyObject *obj);
// converter const std::vector& -> python list
PyObject *make_PyList_pair_date_vector(
    const std::vector<std::pair<QuantLib::Date, Real>> &v);
std::vector<std::pair<QuantLib::Date, Real>>
make_date_real_pair_vector_from_list(PyObject *obj);
bool check_date_real_pair_list(PyObject *obj);

/////////// Tape ///////////////
bool check_Tape(PyObject* obj);
xad::Tape<double> &make_Tape_ref(PyObject *obj);