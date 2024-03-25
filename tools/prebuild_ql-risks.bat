:: #############################################################################
::   
::
::  This file is part of quantlib-risks, a Python wrapper for QuantLib enabled
::  for risk computation using automatic differentiation. It uses XAD,
::  a fast and comprehensive C++ library for automatic differentiation.
::
::  Copyright (C) 2010-2024 Xcelerit Computing Ltd.
::
::  This program is free software: you can redistribute it and/or modify
::  it under the terms of the GNU Affero General Public License as published
::  by the Free Software Foundation, either version 3 of the License, or
::  (at your option) any later version.
::
::  This program is distributed in the hope that it will be useful,
::  but WITHOUT ANY WARRANTY; without even the implied warranty of
::  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
::  GNU Affero General Public License for more details.
::
::  You should have received a copy of the GNU Affero General Public License
::  along with this program.  If not, see <http://www.gnu.org/licenses/>.
::   
:: #############################################################################

pip install delvewheel 
call "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" amd64 -vcvars_ver=14.3
"C:\Program Files\Git\bin\bash.exe" tools/prebuild_ql-risks.sh || exit 1