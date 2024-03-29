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

#include "converters.hpp"
#include <XAD/XAD.hpp>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <tuple>

namespace py = pybind11;

typedef xad::AReal<double> Real;

inline void check(int s) {
  if (s != 0) {
    throw std::runtime_error("failure");
  }
}

inline void check(PyObject *s) {
  if (s == nullptr) {
    throw std::runtime_error("could not create pyobject");
  }
}

// may throw a cast exception
Real make_Real(PyObject *obj) {
  if (PyFloat_Check(obj))
    return Real(PyFloat_AsDouble(obj));
  if (PyLong_Check(obj))
    return Real(PyLong_AsDouble(obj));

  // otherwise try to convert to Real
  auto p = py::reinterpret_borrow<py::object>(obj);
  return py::cast<Real>(p);
}

bool check_Real(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  return py::isinstance<Real>(p);
}

bool check_Real_pair(PyObject *obj) {
  if (PyList_Check(obj)) {
    auto p = py::reinterpret_borrow<py::object>(obj);
    auto l = p.cast<py::list>();
    if (len(l) != 2)
      return false;
    if (!py::isinstance<Real>(l[0]) && !py::isinstance<py::float_>(l[0]) &&
        !py::isinstance<py::int_>(l[0]))
      return false;
    if (!py::isinstance<Real>(l[1]) && !py::isinstance<py::float_>(l[1]) &&
        !py::isinstance<py::int_>(l[1]))
      return false;

    return true;
  } else if (PyTuple_Check(obj)) {
    auto p = py::reinterpret_borrow<py::object>(obj);
    auto l = p.cast<py::tuple>();
    if (len(l) != 2)
      return false;
    if (!py::isinstance<Real>(l[0]) && !py::isinstance<py::float_>(l[0]) &&
        !py::isinstance<py::int_>(l[0]))
      return false;
    if (!py::isinstance<Real>(l[1]) && !py::isinstance<py::float_>(l[1]) &&
        !py::isinstance<py::int_>(l[1]))
      return false;

    return true;
  }
  return false;
}

PyObject *make_PyObject(const Real &x) {
  py::detail::type_caster<Real> caster;
  py::handle out = caster.cast(x, py::return_value_policy::copy, py::handle());
  return out.ptr();
}

///////////// Double vector

PYBIND11_MAKE_OPAQUE(std::vector<Real>);

std::vector<Real> &make_Real_vector_ref(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  return py::cast<std::vector<Real> &>(p);
}

inline Real cast_obj(const py::handle &obj) {
  if (py::isinstance<py::float_>(obj)) {
    return obj.cast<double>();
  } else if (py::isinstance<py::int_>(obj)) {
    return obj.cast<long>();
  }
  return obj.cast<Real>();
}

std::vector<Real> make_Real_vector_from_list(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto l = py::cast<py::list>(p);

  std::vector<Real> ret;
  ret.reserve(py::len(l));
  for (const auto &element : l) {
    ret.push_back(cast_obj(element));
  }
  return ret;
}

std::vector<Real> make_Real_vector_from_tuple(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto t = py::cast<py::tuple>(p);

  std::vector<Real> ret;
  ret.reserve(py::len(t));
  for (const auto &element : t) {
    ret.push_back(cast_obj(element));
  }
  return ret;
}

PyObject *make_PyObject_Real_vector(std::vector<Real> &v) {
  py::detail::type_caster<std::vector<Real> &> caster;
  py::handle out = caster.cast(v, py::return_value_policy::copy, py::handle());
  return out.ptr();
}

PyObject *make_PyList_Real_vector(const std::vector<Real> &v) {
  py::detail::list_caster<std::vector<Real>, Real> caster;
  py::handle out = caster.cast(v, py::return_value_policy::copy, py::handle());
  return out.ptr();
}

PyObject *make_PyTuple_Real_vector(const std::vector<Real> &v) {
  auto t = PyTuple_New(v.size());
  check(t);
  for (size_t i = 0; i < v.size(); ++i) {
    PyTuple_SET_ITEM(t, i, make_PyObject(v[i]));
  }
  return t;
}

bool check_Real_vector(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  if (py::isinstance<std::vector<Real>>(p))
    return true;
  if (py::isinstance<py::list>(p)) {
    auto l = p.cast<py::list>();
    if (py::len(l) == 0)
      return true;
    if (py::isinstance<py::int_>(l[0]) || py::isinstance<py::float_>(l[0]) ||
        py::isinstance<Real>(l[0]))
      return true;
    return false;
  }
  if (py::isinstance<py::tuple>(p)) {
    auto t = p.cast<py::tuple>();
    if (py::len(t) == 0)
      return true;
    if (py::isinstance<py::int_>(t[0]) || py::isinstance<py::float_>(t[0]) ||
        py::isinstance<Real>(t[0]))
      return true;
    return false;
  }
  return false;
}

PYBIND11_MAKE_OPAQUE(DoublePairVector);

DoublePairVector &make_DoublePairVector_ref(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  return py::cast<DoublePairVector &>(p);
}

DoublePairVector make_DoublePairVector_from_list(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto l = py::cast<py::list>(p);

  DoublePairVector ret;
  ret.reserve(py::len(l));
  for (const auto &element : l) {
    auto t = py::cast<py::tuple>(element);
    assert(py::len(t) == 2);
    ret.emplace_back(cast_obj(t[0]), cast_obj(t[1]));
  }
  return ret;
}

DoublePairVector make_DoublePairVector_from_tuple(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto t = py::cast<py::tuple>(p);

  DoublePairVector ret;
  ret.reserve(py::len(t));
  for (const auto &element : t) {
    auto tt = py::cast<py::tuple>(element);
    assert(py::len(tt) == 2);
    ret.emplace_back(cast_obj(tt[0]), cast_obj(tt[1]));
  }
  return ret;
}

PyObject *make_PyObject_DoublePairVector(DoublePairVector &v) {
  py::detail::type_caster<DoublePairVector &> caster;
  py::handle out = caster.cast(v, py::return_value_policy::copy, py::handle());
  return out.ptr();
}

PyObject *make_PyList_DoublePairVector(const DoublePairVector &v) {
  py::detail::list_caster<DoublePairVector, std::pair<Real, Real>> caster;
  py::handle out = caster.cast(v, py::return_value_policy::copy, py::handle());
  return out.ptr();
}

PyObject *make_PyTuple_DoublePairVector(const DoublePairVector &v) {
  auto t = PyTuple_New(v.size());
  check(t);
  for (size_t i = 0; i < v.size(); ++i) {
    auto tt = PyTuple_New(2);
    PyTuple_SET_ITEM(tt, 0, make_PyObject(v[i].first));
    PyTuple_SET_ITEM(tt, 1, make_PyObject(v[i].second));
    PyTuple_SET_ITEM(t, i, tt);
  }
  return t;
}

bool check_DoublePairVector(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  if (py::isinstance<DoublePairVector>(p))
    return true;
  if (py::isinstance<py::list>(p)) {
    auto l = p.cast<py::list>();
    if (py::len(l) == 0)
      return true;
    auto item = l[0];
    if (!py::isinstance<py::tuple>(item))
      return false;
    auto tt = item.cast<py::tuple>();
    if (py::len(tt) != 2)
      return false;
    for (size_t i = 0; i < 2; ++i) {
      if (!py::isinstance<py::int_>(tt[i]) &&
          !py::isinstance<py::float_>(tt[i]) && !py::isinstance<Real>(tt[i]))
        return false;
    }
    return true;
  }
  if (py::isinstance<py::tuple>(p)) {
    auto t = p.cast<py::tuple>();
    if (py::len(t) == 0)
      return true;
    auto item = t[0];
    if (!py::isinstance<py::tuple>(item))
      return false;
    auto tt = item.cast<py::tuple>();
    if (py::len(tt) != 2)
      return false;
    for (size_t i = 0; i < 2; ++i) {
      if (!py::isinstance<py::int_>(tt[i]) &&
          !py::isinstance<py::float_>(tt[i]) && !py::isinstance<Real>(tt[i]))
        return false;
    }
    return true;
  }
  return false;
}

PYBIND11_MAKE_OPAQUE(DoubleVectorVector);

DoubleVectorVector &make_DoubleVectorVector_ref(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  return py::cast<DoubleVectorVector &>(p);
}

DoubleVectorVector make_DoubleVectorVector_from_list(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto l = py::cast<py::list>(p);

  DoubleVectorVector ret;
  ret.reserve(py::len(l));
  for (const auto &element : l) {
    if (py::isinstance<py::list>(element))
      ret.emplace_back(make_Real_vector_from_list(element.ptr()));
    else if (py::isinstance<py::tuple>(element))
      ret.emplace_back(make_Real_vector_from_tuple(element.ptr()));
  }
  return ret;
}

DoubleVectorVector make_DoubleVectorVector_from_tuple(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto l = py::cast<py::tuple>(p);

  DoubleVectorVector ret;
  ret.reserve(py::len(l));
  for (const auto &element : l) {
    if (py::isinstance<py::list>(element))
      ret.emplace_back(make_Real_vector_from_list(element.ptr()));
    else if (py::isinstance<py::tuple>(element))
      ret.emplace_back(make_Real_vector_from_tuple(element.ptr()));
  }
  return ret;
}

PyObject *make_PyObject_DoubleVectorVector(DoubleVectorVector &v) {
  py::detail::type_caster<DoubleVectorVector &> caster;
  py::handle out = caster.cast(v, py::return_value_policy::copy, py::handle());
  return out.ptr();
}

PyObject *make_PyList_DoubleVectorVector(const DoubleVectorVector &v) {
  py::detail::list_caster<DoubleVectorVector, std::vector<Real>> caster;
  py::handle out = caster.cast(v, py::return_value_policy::copy, py::handle());
  return out.ptr();
}

PyObject *make_PyTuple_DoubleVectorVector(const DoubleVectorVector &v) {
  auto t = PyTuple_New(v.size());
  check(t);
  for (size_t i = 0; i < v.size(); ++i) {
    auto tt = make_PyTuple_Real_vector(v[i]);
    PyTuple_SET_ITEM(t, i, tt);
  }
  return t;
}

bool check_DoubleVectorVector(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  if (py::isinstance<DoubleVectorVector>(p))
    return true;
  if (py::isinstance<py::list>(p)) {
    auto l = p.cast<py::list>();
    if (std::all_of(l.begin(), l.end(), [](const py::handle &h) {
          return check_Real_vector(h.ptr());
        }))
      return true;
    return false;
  }
  if (py::isinstance<py::tuple>(p)) {
    auto t = p.cast<py::tuple>();
    if (std::all_of(t.begin(), t.end(), [](const py::handle &h) {
          return check_Real_vector(h.ptr());
        }))
      return true;
    return false;
  }
  return false;
}

///// PairDoubleVector

PYBIND11_MAKE_OPAQUE(PairDoubleVector);

PairDoubleVector &make_PairDoubleVector_ref(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  return py::cast<PairDoubleVector &>(p);
}

PairDoubleVector make_PairDoubleVector_from_list(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto l = py::cast<py::list>(p);

  PairDoubleVector ret;
  assert(py::len(l) == 2);
  ret.first = py::isinstance<py::list>(l[0]) ? make_Real_vector_from_list(l[0].ptr()) : make_Real_vector_from_tuple(l[0].ptr());
  ret.second = py::isinstance<py::list>(l[1]) ? make_Real_vector_from_list(l[1].ptr()) : make_Real_vector_from_tuple(l[1].ptr());
  return ret;
}

PairDoubleVector make_PairDoubleVector_from_tuple(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto l = py::cast<py::tuple>(p);

  PairDoubleVector ret;
  assert(py::len(l) == 2);
  ret.first = py::isinstance<py::list>(l[0]) ? make_Real_vector_from_list(l[0].ptr()) : make_Real_vector_from_tuple(l[0].ptr());
  ret.second = py::isinstance<py::list>(l[1]) ? make_Real_vector_from_list(l[1].ptr()) : make_Real_vector_from_tuple(l[1].ptr());
  return ret;
}

PyObject *make_PyObject_PairDoubleVector(PairDoubleVector &v) {
  py::detail::type_caster<PairDoubleVector &> caster;
  py::handle out = caster.cast(v, py::return_value_policy::copy, py::handle());
  return out.ptr();
}

PyObject *make_PyTuple_PairDoubleVector(const PairDoubleVector &v) {
  auto t = PyTuple_New(2);
  check(t);
  PyTuple_SET_ITEM(t, 0, make_PyTuple_Real_vector(v.first));
  PyTuple_SET_ITEM(t, 1, make_PyTuple_Real_vector(v.second));
  return t;
}

bool check_PairDoubleVector(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  if (py::isinstance<PairDoubleVector>(p))
    return true;
  if (py::isinstance<py::list>(p)) {
    auto l = p.cast<py::list>();
    if (py::len(l) != 2)
    {
      return false;
    }
    return check_Real_vector(l[0].ptr()) && check_Real_vector(l[1].ptr());
  }
  if (py::isinstance<py::tuple>(p)) {
    auto t = p.cast<py::tuple>();
    if (py::len(t) != 2)
    {
      return false;
    }
    return check_Real_vector(t[0].ptr()) && check_Real_vector(t[1].ptr());;
  }
  return false;
}


////// DoublePair

std::pair<Real, Real> make_Real_pair_from_tuple(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto t = p.cast<py::tuple>();
  if (len(t) != 2) {
    throw std::runtime_error("invalid tuple length");
  }
  auto first = cast_obj(t[0]);
  auto second = cast_obj(t[1]);
  return {first, second};
}

std::pair<Real, Real> make_Real_pair_from_list(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto l = p.cast<py::list>();
  if (len(l) != 2) {
    throw std::runtime_error("invalid list length");
  }
  auto first = cast_obj(l[0]);
  auto second = cast_obj(l[1]);
  return {first, second};
}

PyObject *make_PyTuple_Real_pair(const std::pair<Real, Real> &p) {
  py::detail::type_caster<std::pair<Real, Real>> caster;
  py::handle out = caster.cast(p, py::return_value_policy::copy, py::handle());
  return out.ptr();
}

std::vector<std::tuple<Real, Real, bool>>
make_mesher_point_vector_from_list(PyObject *obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto l = py::cast<py::list>(p);

  py::detail::type_caster<std::tuple<Real, Real, bool>> caster;

  std::vector<std::tuple<Real, Real, bool>> ret;
  ret.reserve(py::len(l));
  int index = 0;
  for (const auto &element : l) {
    auto t = py::cast<py::tuple>(element);
    if (py::len(t) != 3) {
      throw std::runtime_error("Only lists of 3-tuples are supported");
    }
    auto t0 = cast_obj(t[0]);
    auto t1 = cast_obj(t[1]);
    auto t2 = bool(py::cast<py::bool_>(t[2]));
    ret.emplace_back(t0, t1, t2);
  }
  return ret;
}

bool mesher_point_vector_check(PyObject *obj) {
  if (!PyList_Check(obj))
    return false;
  auto p = py::reinterpret_borrow<py::object>(obj);
  auto l = py::cast<py::list>(p);
  for (const auto &element : l) {
    if (!py::isinstance<py::tuple>(element))
      return false;
    auto t = py::cast<py::tuple>(element);
    if (py::len(t) != 3)
      return false;
    if (!py::isinstance<Real>(t[0]) && !py::isinstance<py::float_>(t[0]) &&
        !py::isinstance<py::int_>(t[0]))
      return false;
    if (!py::isinstance<Real>(t[1]) && !py::isinstance<py::float_>(t[1]) &&
        !py::isinstance<py::int_>(t[1]))
      return false;
    if (!py::isinstance<py::bool_>(t[2]))
      return false;
  }
  return true;
}

void add_to_module(PyObject *mdef) {
  auto m = py::reinterpret_borrow<py::module_>(mdef);

  py::bind_vector<std::vector<Real>>(m, "DoubleVector")
      .def("empty", [](const std::vector<Real> &self) { return self.empty(); })
      .def("size", [](const std::vector<Real> &self) { return self.size(); })
      .def("append", [](std::vector<Real> &self, long x) { self.push_back(x); })
      .def("append",
           [](std::vector<Real> &self, double x) { self.push_back(x); })
      .def("push_back",
           [](std::vector<Real> &self, const Real &x) { self.push_back(x); })
      .def("push_back",
           [](std::vector<Real> &self, long x) { self.push_back(x); })
      .def("push_back",
           [](std::vector<Real> &self, double x) { self.push_back(x); })
      .def("pop_back", [](std::vector<Real> &self) { self.pop_back(); })
      .def("front", [](const std::vector<Real> &self) { return self.front(); })
      .def("back", [](const std::vector<Real> &self) { return self.back(); })
      .def("assign", [](std::vector<Real> &self, int n,
                        const Real &x) { self.assign(n, x); })
      .def("assign",
           [](std::vector<Real> &self, int n, double x) { self.assign(n, x); })
      .def("assign",
           [](std::vector<Real> &self, int n, long x) { self.assign(n, x); });

  py::bind_vector<DoubleVectorVector>(m, "DoubleVectorVector")
      .def("empty", [](const DoubleVectorVector &self) { return self.empty(); })
      .def("size", [](const DoubleVectorVector &self) { return self.size(); })
      .def("append",
           [](DoubleVectorVector &self, const std::vector<double> &x) {
             self.emplace_back(x.begin(), x.end());
           })
      .def("append",
           [](DoubleVectorVector &self, const std::vector<int> &x) {
             self.emplace_back(x.begin(), x.end());
           })
      .def("push_back",
           [](DoubleVectorVector &self, std::vector<Real> x) {
             self.push_back(std::move(x));
           })
      .def("push_back",
           [](DoubleVectorVector &self, const std::vector<int> &x) {
             self.emplace_back(x.begin(), x.end());
           })
      .def("push_back",
           [](DoubleVectorVector &self, const std::vector<double> &x) {
             self.emplace_back(x.begin(), x.end());
           })
      .def("pop_back", [](DoubleVectorVector &self) { self.pop_back(); })
      .def("front", [](const DoubleVectorVector &self) { return self.front(); })
      .def("back", [](const DoubleVectorVector &self) { return self.back(); })
      .def("assign", [](DoubleVectorVector &self, int n,
                        const std::vector<Real> &x) { self.assign(n, x); })
      .def("assign",
           [](DoubleVectorVector &self, int n, const std::vector<double> &x) {
             std::vector<Real> xx(x.begin(), x.end());
             self.assign(n, xx);
           })
      .def("assign",
           [](DoubleVectorVector &self, int n, const std::vector<int> &x) {
             std::vector<Real> xx(x.begin(), x.end());
             self.assign(n, xx);
           });

  py::bind_vector<DoublePairVector>(m, "DoublePairVector")
      .def("empty", [](const DoublePairVector &self) { return self.empty(); })
      .def("size", [](const DoublePairVector &self) { return self.size(); })
      .def("append",
           [](DoublePairVector &self, std::pair<long, long> x) {
             self.emplace_back(x.first, x.second);
           })
      .def("append",
           [](DoublePairVector &self, std::pair<double, double> x) {
             self.emplace_back(x.first, x.second);
           })
      .def("push_back",
           [](DoublePairVector &self, const std::pair<Real, Real> &x) {
             self.push_back(x);
           })
      .def("push_back",
           [](DoublePairVector &self, std::pair<long, long> x) {
             self.emplace_back(x.first, x.second);
           })
      .def("push_back",
           [](DoublePairVector &self, std::pair<double, double> x) {
             self.emplace_back(x.first, x.second);
           })
      .def("pop_back", [](DoublePairVector &self) { self.pop_back(); })
      .def("front", [](const DoublePairVector &self) { return self.front(); })
      .def("back", [](const DoublePairVector &self) { return self.back(); })
      .def("assign", [](DoublePairVector &self, int n,
                        const std::pair<Real, Real> &x) { self.assign(n, x); })
      .def("assign",
           [](DoublePairVector &self, int n, std::pair<double, double> x) {
             self.assign(n, std::pair<Real, Real>(x.first, x.second));
           })
      .def("assign",
           [](DoublePairVector &self, int n, std::pair<long, long> x) {
             self.assign(n, std::pair<Real, Real>(x.first, x.second));
           });
}

bool check_Tape(PyObject* obj) {
  auto p = py::reinterpret_borrow<py::object>(obj);
  return py::isinstance<xad::Tape<double>>(p);  
}

xad::Tape<double> &make_Tape_ref(PyObject *obj)
{
  auto p = py::reinterpret_borrow<py::object>(obj);
  return py::cast<xad::Tape<double>&>(p);  
}