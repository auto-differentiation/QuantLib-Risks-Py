# Builds QuantLib as a static library with QuantLibAAD from lib/, against XAD::xad
# (QLRXad). Defines QuantLib::QuantLib. With QLR_QUANTLIB_ONLY, builds and installs only these.

set(QLR_LIB_DIR "${PROJECT_SOURCE_DIR}/lib")

include(QLRBoost)

# QuantLib: static, no tests/examples/benchmark
set(BUILD_SHARED_LIBS OFF)
foreach(opt QL_BUILD_TEST_SUITE QL_BUILD_EXAMPLES QL_BUILD_BENCHMARK
            QL_INSTALL_TEST_SUITE QL_INSTALL_EXAMPLES QL_INSTALL_BENCHMARK)
  set(${opt} OFF CACHE BOOL "" FORCE)
endforeach()
set(QL_NULL_AS_FUNCTIONS ON CACHE BOOL "" FORCE)
set(QL_EXTERNAL_SUBDIRECTORIES "${QLR_LIB_DIR}/QuantLibAAD" CACHE STRING "" FORCE)
set(QL_EXTRA_LINK_LIBRARIES QuantLibAAD CACHE STRING "" FORCE)
# QuantLib's find_package(Boost) (FindBoost module) uses the headers from QLRBoost
set(CMAKE_POLICY_DEFAULT_CMP0167 OLD)
set(Boost_NO_BOOST_CMAKE ON)
set(Boost_INCLUDE_DIR "${QLR_BOOST_INCLUDE_DIR}" CACHE PATH "" FORCE)
if(MSVC AND CMAKE_GENERATOR MATCHES "Visual Studio")
  add_compile_options(/MP)  # parallel compilation within the QuantLib project
endif()

# QuantLib with the temporary fixes in patches/quantlib, as a copy in the build tree
set(QUANTLIB_SOURCE_DIR "${QLR_LIB_DIR}/QuantLib")
set(QUANTLIB_PATCHED_DIR "${CMAKE_BINARY_DIR}/QuantLib-src")
include(QuantLibPatches)
add_subdirectory("${QUANTLIB_PATCHED_DIR}" "${CMAKE_BINARY_DIR}/QuantLib")
# QuantLibAAD always adds its examples (which need a newer QuantLib) and test-suite
foreach(dir Examples test-suite)
  if(EXISTS "${QLR_LIB_DIR}/QuantLibAAD/${dir}/CMakeLists.txt")
    set_property(DIRECTORY "${QLR_LIB_DIR}/QuantLibAAD/${dir}" PROPERTY EXCLUDE_FROM_ALL ON)
  endif()
endforeach()

if(NOT TARGET QuantLib::QuantLib)
  add_library(QuantLib::QuantLib ALIAS ql_library)
endif()

if(QLR_BOOST_DOWNLOADED)
  # downloaded headers live in the build tree: build-only include path,
  # installed next to QuantLib's headers instead
  foreach(prop INTERFACE_INCLUDE_DIRECTORIES INTERFACE_SYSTEM_INCLUDE_DIRECTORIES)
    get_target_property(dirs ql_library ${prop})
    set(new_dirs)
    foreach(dir IN LISTS dirs)
      if(dir STREQUAL QLR_BOOST_INCLUDE_DIR)
        set(dir "$<BUILD_INTERFACE:${dir}>")
      endif()
      list(APPEND new_dirs "${dir}")
    endforeach()
    if(dirs)
      set_target_properties(ql_library PROPERTIES ${prop} "${new_dirs}")
    endif()
  endforeach()
  if(QLR_QUANTLIB_ONLY)
    install(DIRECTORY "${QLR_BOOST_INCLUDE_DIR}/boost" DESTINATION "${QL_INSTALL_INCLUDEDIR}")
  endif()
endif()

if(QLR_QUANTLIB_ONLY)
  # checked by PrebuiltQuantLib: the extension must use the same XAD
  file(WRITE "${CMAKE_BINARY_DIR}/QLRXadVersion.cmake" "set(QLR_QUANTLIB_XAD_VERSION ${XAD_VERSION})\n")
  install(FILES "${CMAKE_BINARY_DIR}/QLRXadVersion.cmake" DESTINATION "${QLAAD_INSTALL_CMAKEDIR}")
endif()
