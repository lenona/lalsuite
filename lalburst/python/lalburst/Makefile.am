BUILT_SOURCES =
MOSTLYCLEANFILES =
EXTRA_DIST =
include $(top_srcdir)/gnuscripts/lalsuite_python.am
include $(top_srcdir)/gnuscripts/lalsuite_vcs_info.am

vcs_info_sources = git_version.py

if HAVE_PYTHON

pymoduledir = $(pkgpythondir)

pymodule_PYTHON = \
	__init__.py \
	git_version.py \
	timeslides.py \
	$(END_OF_LIST)

<<<<<<< HEAD
=======
pkgpython_LTLIBRARIES = \
	cs_gamma.la
cs_gamma_la_SOURCES = cs_gamma.c
cs_gamma_la_CPPFLAGS = $(AM_CPPFLAGS) $(CPPFLAGS) $(PYTHON_CPPFLAGS) -I$(top_srcdir)/src
cs_gamma_la_CFLAGS = $(AM_CFLAGS) $(CFLAGS) $(GSL_CFLAGS) $(LAL_CFLAGS) -Wno-cast-qual
cs_gamma_la_LDFLAGS = $(top_builddir)/src/liblalburst.la $(AM_LDFLAGS) $(LIBS) $(GSL_LIBS) $(LAL_LIBS) $(PYTHON_LIBS) -module -avoid-version

>>>>>>> 89f16f7... Do not use $(..._la_LIBADD) to link against external libraries
endif

#pkgpython_LTLIBRARIES = \
#	cs_gamma.la
#cs_gamma_la_SOURCES = cs_gamma.c
#cs_gamma_la_CPPFLAGS = $(AM_CPPFLAGS) $(CPPFLAGS) $(PYTHON_CPPFLAGS)
#cs_gamma_la_CFLAGS = $(AM_CFLAGS) $(CFLAGS) $(GSL_CFLAGS) $(LAL_CFLAGS)
#cs_gamma_la_LIBADD = $(top_builddir)/src/liblalburst.la
#cs_gamma_la_LDFLAGS = $(AM_LDFLAGS) $(LIBS) $(GSL_LIBS) $(LAL_LIBS) $(PYTHON_LDFLAGS) -module -avoid-version
