BUILT_SOURCES =
MOSTLYCLEANFILES =
EXTRA_DIST =
include $(top_srcdir)/gnuscripts/lalsuite_python.am

if HAVE_PYTHON

pymoduledir = $(pkgpythondir)/bayestar

pymodule_PYTHON = \
	__init__.py \
	command.py \
	decorator.py \
	distance.py \
	filter.py \
	ligolw.py \
	sky_map.py \
	postprocess.py \
	timing.py \
	$(END_OF_LIST)

if HAVE_CHEALPIX
if SWIG_BUILD_PYTHON
pymodule_LTLIBRARIES = _sky_map.la _distance.la

_sky_map_la_CPPFLAGS = $(AM_CPPFLAGS) $(SWIG_PYTHON_CPPFLAGS) -I$(top_srcdir)/src
_sky_map_la_CFLAGS = $(AM_CFLAGS) $(SWIG_PYTHON_CFLAGS) -Wno-error
_sky_map_la_LDFLAGS = $(top_builddir)/src/liblalinference.la -shared -module -avoid-version

_distance_la_CPPFLAGS = $(AM_CPPFLAGS) $(SWIG_PYTHON_CPPFLAGS) -I$(top_srcdir)/src
_distance_la_CFLAGS = $(AM_CFLAGS) $(SWIG_PYTHON_CFLAGS) -Wno-error
<<<<<<< HEAD
<<<<<<< HEAD
_distance_la_LDFLAGS = -shared -module -avoid-version
_distance_la_LIBADD = $(top_builddir)/src/liblalinference.la
=======
=======
>>>>>>> 89f16f7... Do not use $(..._la_LIBADD) to link against external libraries
_distance_la_LDFLAGS = $(top_builddir)/src/liblalinference.la -shared -module -avoid-version

_moc_la_CPPFLAGS = $(AM_CPPFLAGS) $(SWIG_PYTHON_CPPFLAGS) -I$(top_srcdir)/src
_moc_la_CFLAGS = $(AM_CFLAGS) $(SWIG_PYTHON_CFLAGS) -Wno-error
_moc_la_LDFLAGS = $(top_builddir)/src/liblalinference.la -shared -module -avoid-version
<<<<<<< HEAD
>>>>>>> 89f16f7... Do not use $(..._la_LIBADD) to link against external libraries
=======
>>>>>>> 89f16f7... Do not use $(..._la_LIBADD) to link against external libraries
endif
endif

all-local: _sky_map.so _distance.so

_sky_map.so:
	rm -f $@ && $(LN_S) .libs/$@

_distance.so:
	rm -f $@ && $(LN_S) .libs/$@

CLEANFILES = _sky_map.so _distance.so

endif
