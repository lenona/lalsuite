#!/usr/bin/env @PYTHONPROG@
"""
followup utilities

$Id$

This
"""

__author__ = 'Chad Hanna <channa@phys.lsu.edu>'
__date__ = '$Date$'
__version__ = '$Revision$'[11:-2]



import sys
import os, shutil
import urllib
try:
  import sqlite3 as sqlite
except ImportError:
  import sqlite

from subprocess import *
import copy
import re
import exceptions
import glob
import fileinput
import linecache
import string
import random
from optparse import *
from types import *
import matplotlib
matplotlib.use('Agg')
import operator
from UserDict import UserDict

from pylab import *
from glue import segments
from glue import segmentsUtils
from glue.ligolw import ligolw
from glue.ligolw import table
from glue.ligolw import lsctables
from glue.ligolw import utils
from pylal import CoincInspiralUtils
from glue import iterutils
from glue import pipeline
from glue.lal import *
from glue import lal
from glue import markup
from lalapps import inspiralutils

########## CLASS TO WRITE LAL CACHE FROM HIPE OUTPUT #########################
class getCache(UserDict):
  """
  An instance of a lal cache
  """
  def __init__(self, options,cp, currentPath):
    UserDict.__init__(self)
    self.dir = os.listdir(os.getcwd())
    self.options = options
    self.types = ['TMPLTBANK', 'TRIGBANK', 'INSPIRAL_FIRST', \
                 'INSPIRAL_SECOND', 'THINCA_FIRST', 'THINCA_SECOND']
    self.iniNames = ['tmpltbank-path', 'trigbank-path', 'first-inspiral-path', \
         'second-inspiral-path', 'first-coinc-path', 'second-coinc-path']
    self.iniNameMaps = map(None, self.iniNames, self.types)
    self.oNames = ['bank.cache', 'trigbank.cache', 'first_inspiral.cache', \
         'second_inspiral.cache', 'first_thinca.cache', 'second_thinca.cache']
    self.nameMaps = map(None, self.oNames, self.types)
    self.ifoTypes = ['H1','H2','L1','V1','H1H2','H1L1','H2L1','H1V1', \
                          'H2V1','L1V1','H1H2L1','H1H2V1','H1L1V1', \
                          'H2L1V1','H1H2L1V1']


    if options.generate_fu_cache:
      print >> sys.stderr, "\nOption --generate-fu-cache is specified, it overwrites the hipe cache files  which already exist"
      self.getCacheAll(cp)
      self.writeCacheAll('fu_hipe.cache')
      print >> sys.stderr, "\nHIPE CACHE FILE WRITTEN TO: fu_hipe.cache"
    try:
      os.chdir("cache")
      os.chdir(currentPath)
    except:
      if len(string.strip(cp.get('followup-hipe-cache','hipe-cache-path'))) > 0:
        try:
          os.symlink(string.strip(cp.get('followup-hipe-cache','hipe-cache-path')), 'cache')
        except: print >> sys.stderr, "WARNING: cache directory exists, cannot link"
      else: pass


    # Since we are continuing get useful stuff from the ini file.
    if options.generate_fu_cache or not cp.has_option('followup-triggers','hipe-output-cache'):
      cacheString = 'fu_hipe.cache'
    else:
      cacheString = string.strip(cp.get('followup-triggers','hipe-output-cache'))
    if cp.has_option('followup-triggers','triggers-tag'):
      self.triggerTag = string.strip(cp.get('followup-triggers','triggers-tag'))
    else:
      self.triggerTag = ''

    self.cache = Cache.fromfile(open(cacheString))



  def ifoDict(self):
    return {'H1':[],'H2':[],'L1':[],'V1':[],'H1H2':[], 'H1L1':[],'H2L1':[], \
                   'H1V1':[],'H2V1':[],'L1V1':[],'H1H2L1':[],'H1H2V1':[], \
                   'H1L1V1':[],'H2L1V1':[],'H1H2L1V1':[]}

  def getCacheType(self, iniName, type, cp=None):
    self[type] = []
    p = re.compile(type)
    f = re.compile("FOLLOWUP")
    m = re.compile("-")
    x = re.compile(".xml")
    g = re.compile(".gz")
    try:
      dir = os.listdir(string.strip(cp.get('followup-hipe-cache',iniName)))
      cache_path = os.path.abspath(string.strip(cp.get('followup-hipe-cache',iniName)))
    except:
      dir = self.dir
      cache_path = os.path.abspath(self.options.cache_path)
    for fname in dir:
      if f.search(fname): continue
      if p.search(fname):
        fnamebis =  g.split(fname)[0]
        ifo = m.split(fnamebis)[0]
        tag = m.split(fnamebis)[1]
        start = m.split(fnamebis)[-2]
        dur = x.split(m.split(fnamebis)[-1])
        try:
          # scirun = string.strip(cp.get('followup-hipe-cache','science-run'))
          # tmpentry = ifo+" "+scirun+" "+start+" "+dur[0]+" "+"file://localhost" +cache_path+"/"+fname
          tmpentry = ifo+" "+tag+" "+start+" "+dur[0]+" "+"file://localhost" +cache_path+"/"+fname
          entry = lal.CacheEntry(tmpentry)
          self[type].append(entry)
        except: pass

  def getCacheAll(self,cp=None):
    for iniName, type in self.iniNameMaps:
      self.getCacheType(iniName,type,cp)


  def writeCacheType(self,oName,type,cName):
    #cName = open(oName,'w')
    for fname in self[type]:
      cName.write(str(fname)+"\n")
    #cName.close()

  def writeCacheAll(self,outputfile):
    cName = open(outputfile,'w')
    for oName, type in self.nameMaps:
      self.writeCacheType(str(oName),type,cName)
    cName.close()


  def getListFromCache(self,cache):
    listInstance = []
    for ifo in cache:
      listInstance = listInstance + cache[ifo].pfnlist()
    return listInstance

  def filesMatchingGPSinCache(self, time=None, cacheType=None, ifo_tag=None, ifo_in_coinc=None, ):
    cacheSubSet = self.ifoDict()

    if self.cache:
      for ifo in self.ifoTypes:
        try:
          if time:
            if time[ifo]:
              time_ifo = time[ifo]
            else:
              #if ifo found in the analysed times, but not in coinc...
              if ifo_tag and len(ifo)==2 and re.search(ifo,ifo_tag):
                time_ifo = time[ifo_in_coinc[0]]
              else:
                continue
            seg1 = segments.segment(time_ifo,time_ifo+1)
            seg2 = segments.segment(time_ifo-1,time_ifo)
          else:
            seg1 = None
            seg2 = None          
	  listInstance = self.cache.sieve(ifo,cacheType,None,True)
          listInstance = listInstance.sieve(None,None,seg1)
          listInstance = listInstance.sieve(None,None,seg2)
          cacheSubSet[ifo] = listInstance
        except:
          continue #print "couldn't get sub cache for " + ifo 
    else: print "no valid cache file"
    return(cacheSubSet)


  def getProcessParamsFromCache(self, opts, cp, subCache, tag, time, getInsp = False, ifo_in_coinc=None):

    process = self.ifoDict()
    inspTable = self.ifoDict()
    for ifo in subCache:
      for f in subCache[ifo]:
        # As soon as process[ifo] is filled we can stop iterating in this loop.
        if process[ifo]:
          break

        path = f.path()
        extension = path.split('.')[len(path.split('.'))-1]
        if extension == 'gz': gz = True
        else: gz = False

        # if the option "--convert-evenid" is called, a copy of the xml file
        # is made under LOCAL_XML_COPY, and the event_id is converted 
        # from int_8s to ilwd:char
        if opts.convert_eventid:
          path = self.doFileCopyAndEventIdConvert(cp,[path])[0]
        doc = utils.load_filename(path,False,gz)
        proc = table.get_table(doc, lsctables.ProcessParamsTable.tableName)
        if getInsp:
          insp = table.get_table(doc, lsctables.SnglInspiralTable.tableName)
        for row in proc:          
          if str(row.param).find("--ifo-tag") >= 0:
             ifoTag = row.value
          # The default is to assume that the file matches if there is no tag
          else: ifoTag = tag
          # this is a hack to handle the "-userTag" string in some xml files...
          if str(row.param).find("-userTag") >= 0:
             row.param = "--user-tag"
          # end of the hack...

        # We check that the ifo names appearing in the tag (input argument) are 
        # found in the ifoTag of the process param table. But we don't require 
        # an exact match. We allow a "tag" being double times, and an "ifoTag"
        #  being triple times. This is to handle the case of candidates which 
        # were identified when one ifo was vetoed while still in science mode.
        # Notice that this method is a hack. However implementing
        # this loose condition on the ifo-tag was required in order to be able
        # to run the followup robustly over the candidates of the 1st calendar
        # of S5 (after the IFO TIME SEPARATION).
        # THIS SHOULD BE IMPROVED IN FUTURE ANALYSES #

        ifoTagTest = True
        for j in range(0,len(tag)-1,2):
          ifostring = tag[j:j+2]
          if ifostring not in ifoTag:
            ifoTagTest = False
            break
        if ifoTagTest:

          if time[ifo]:
            time_ifo = time[ifo]
          else:
            # if time[ifo] is not defined (happens for a double coinc in triple
            #  times) then use the end_time in the first ifo of the coinc
            time_ifo = time[ifo_in_coinc[0]]
          search = table.get_table(doc, lsctables.SearchSummaryTable.tableName)
          for row in search:
            out_start_time = float(row.out_start_time)
            out_start_time_ns = float(row.out_start_time_ns)/1000000000
            out_end_time = float(row.out_end_time)
            out_end_time_ns = float(row.out_end_time_ns)/1000000000
            if ( (time_ifo >= (out_start_time+out_start_time_ns)) and (time_ifo <= (out_end_time+out_end_time_ns)) ):
              process[ifo] = proc
              if getInsp: inspTable[ifo] = insp
              break          

    if getInsp:
      return process, inspTable
    else:
      return process

  def processFollowupCache(self, cp, opts, trig, type="INSPIRAL_SECOND_"):

    if type == "INSPIRAL_SECOND_":
      # get the list of interferometers from the ifoTag
      listIfoTime = []
      for j in range(0,len(trig.ifoTag)-1,2):
        ifo = trig.ifoTag[j:j+2]
        listIfoTime.append(ifo)

      # get an ifo tag with wild cards (example: *H1*H2*)
      wildIfoTag = "*" + "*".join(listIfoTime) + "*"
      # now we define a wildIfoTag type, for example '*H1*H2*'
      # This type will be used to sieve (in filesMatchingGPSinCache())
      wildType = type + wildIfoTag

      try:
        inspiral_process_params = self.getProcessParamsFromCache( \
                       opts,cp, self.filesMatchingGPSinCache(\
                       trig.gpsTime, wildType, trig.ifoTag, trig.ifolist_in_coinc), \
                       trig.ifoTag, trig.gpsTime, False, trig.ifolist_in_coinc)
      except:
        print "couldn't get inspiral process params for " + str(trig.eventID)
        inspiral_process_params = []
      return inspiral_process_params
    else:
      try:
        inspiral_process_params, sngl = self.getProcessParamsFromCache( \
                       opts,cp, self.filesMatchingGPSinCache(\
                       trig.gpsTime, type), \
                       trig.ifoTag, trig.gpsTime,True)
      except:
        print "couldn't get "+type+" process params for " + str(trig.eventID)
        inspiral_process_params = []
        sngl = []
      return inspiral_process_params, sngl

  def readTriggerFiles(self,cp,opts):
   
    if not self.cache or self.triggerTag == "":
      xml_glob = string.strip(cp.get('followup-triggers','xml-glob'))
      triggerList = glob.glob(xml_glob) 
    else:
      triggerCache = self.filesMatchingGPSinCache(None,self.triggerTag)
      triggerList = self.getListFromCache(triggerCache)

    # if the option "--convert-eventid" is called, a copy of the xml file 
    # is made under LOCAL_XML_COPY, and the event_id is converted
    # from int_8s to ilwd:char
    if opts.convert_eventid:
      triggerList = self.doFileCopyAndEventIdConvert(cp,triggerList)
      
    numtrigs = string.strip(cp.get('followup-triggers','num-trigs'))
    statistic =  string.strip(cp.get('followup-triggers','statistic'))
    bla =  string.strip(cp.get('followup-triggers','bitten-l-a'))
    blb =  string.strip(cp.get('followup-triggers','bitten-l-b'))
    found, coincs, search = readFiles(triggerList,getstatistic(statistic,bla,blb))
    return numtrigs, found, coincs, search


  def doFileCopyAndEventIdConvert(self,cp,inputxmlfilelist):
    newfilelist = []
    for inputxmlfile in inputxmlfilelist:
      if not os.path.isfile("LOCAL_XML_COPY/" + inputxmlfile.split('/')[-1]):
        shutil.copy(inputxmlfile,'LOCAL_XML_COPY')
        convert_process = call(cp.get('condor','pylal_conv_eventid') + " LOCAL_XML_COPY/" + inputxmlfile.split('/')[-1], shell=True)
        if convert_process != 0:
          print >> sys.stderr, "ligolw_conv_inspid could not be run on file " + inputxmlfile.split('/')[-1]
          sys.exit(1)
      else:
        print "The file " + inputxmlfile.split('/')[-1] + " already exist in LOCAL_XML_COPY. It will not be overwritten"
      newfilelist.append("LOCAL_XML_COPY/" + inputxmlfile.split('/')[-1])
    return newfilelist

##############################################################################
# functions to parse qscan cache files (used in analyseQscan)
##############################################################################

def getPathFromCache(fileName,type,ifo=None,time=None):
  qscanList = []
  cacheList = listFromFile(fileName)
  if len(cacheList) == 0:
    return qscanList
  for line in cacheList:
    test_line = True
    if not re.search(type,line.split(' ')[1]):
      test_line = False
    if ifo:
      if not ifo == line.split(' ')[0]:
        test_line = False
      else: pass
    if time:
      if not time == line.split(' ')[2]:
        test_line = False
      else: pass
    if test_line:
      path_output = line.split(' ')[-1]
      time_output = line.split(' ')[2]
      type_output = line.split(' ')[1]
      ifo_output = line.split(' ')[0]
      qscanList.append([path_output,time_output,type_output,ifo_output])
    else: continue
  return qscanList

##############################################################################
# class for qscan intermediate table
##############################################################################

class QscanIntermediateTable(table.Table):
  tableName = "qscan:intermediate:table"
  validcolumns = {
    "type": "lstring",
    "param": "lstring",
    "ifo": "lstring",
    "qscan_time": "lstring",
    "qscan_dir": "lstring",
  }

##############################################################################
# Function to get qscan foreground.
##############################################################################

def getForegroundTimes(cp,opts,ifo):
  times = []
  fileName = ""

  if cp.has_option('followup-triggers',ifo+'times') and string.strip(cp.get('followup-triggers',ifo+'times')):
    fileName = string.strip(cp.get('followup-triggers',ifo+'times'))
    if not os.path.exists(fileName):
      print >> sys.stderr, "File " + fileName + " does not exist"
      sys.exit(1)
    timeList = listFromFile(fileName)
    if not timeList:
      print >> sys.stderr, "the list of times in file " + fileName + " could not be found"
      sys.exit(1)
    times = stringToFloatList(timeList)

  else:
    print >> sys.stderr, "Field "+ifo+"times in [triggers] section is not specified. The ifo " + ifo + " will be ignored"

  return times,fileName

##############################################################################
# Function to get qscan background. 
##############################################################################

def getQscanBackgroundTimes(cp, opts, ifo, dq_url_pattern, segFile):
    times = []
    fileName = ''
  
    if cp.has_option('followup-background-qscan-times',ifo+'range'):
      rangeString = string.strip(cp.get('followup-background-qscan-times',ifo+'range'))
    else:
      rangeString = ''
    if cp.has_option('followup-background-qscan-times',ifo+'segment-list'):
      segmentListFile = string.strip(cp.get('followup-background-qscan-times',ifo+'segment-list'))
    else:
      segmentListFile = ''
    if cp.has_option('followup-background-qscan-times',ifo+'time-list'):
      timeListFile = string.strip(cp.get('followup-background-qscan-times',ifo+'time-list'))
    else:
      timeListFile = ''

    if len(rangeString) == 0 and len(segmentListFile) == 0 and len(timeListFile) == 0:
      print "No qscan background specified for " + ifo
    else:

      # Generate the list of science segments (excluding cat 1 vetoes) if a time range is provided in the ini file
      if not len(rangeString) == 0:
        epochStart = rangeString.split(',')[0]
        epochEnd = rangeString.split(',')[1]
        opts.gps_start_time = int(epochStart)
        opts.gps_end_time = int(epochEnd)
        opts.use_available_data = False
        opts.run_data_quality = False
        # overwrite the ini file if the field "analyze" in section [segments] exist...
        cp.set("segments", "analyze", "Science")

        inspiralutils.findSegmentsToAnalyze(cp,opts,ifo,dq_url_pattern,segFile)
        segmentListFile = segFile[ifo]

      # Use the segment list if provided, and generate a list of random times
      if not len(segmentListFile) == 0:
        segmentList = pipeline.ScienceData()
        segmentMin = cp.getint('followup-background-qscan-times','segment-min-len')
        segmentList.read(segmentListFile,segmentMin)
        segmentListLength = segmentList.__len__()
        segmentListStart = segmentList.__getitem__(0).start()
        segmentListEnd = segmentList.__getitem__(segmentListLength - 1).end()

        seed = cp.getint('followup-background-qscan-times','random-seed')
        statistics = cp.getint('followup-background-qscan-times','background-statistics')

        random.seed(seed)
        counter = 0
        times = []

        while counter < statistics:
          gps = float(segmentListStart) + float(segmentListEnd - segmentListStart)*random.random()
          testList = copy.deepcopy(segmentList)
          secondList = [pipeline.ScienceSegment(tuple([0,int(gps),int(gps)+1,1]))]        
          if testList.intersection(secondList):
            times.append(gps)
            counter = counter + 1
          else:
            continue
        # Save the list of times in a file (for possibly re-using it later)
        timeList = floatToStringList(times)
        fileName = "timeList-" + ifo + "-" + repr(seed) + "-" + repr(statistics) + "-" + repr(segmentListStart) + "-" + repr(segmentListEnd) + ".txt"
        saveRandomTimes(timeList,fileName)

      # Use the time-list file if provided
      if len(segmentListFile) == 0 and not len(timeListFile) == 0:
        timeList = listFromFile(timeListFile)
        fileName = timeListFile
        if not timeList:
          print >> sys.stderr, "the list of times in file " + timeListFile + " could not be found"
          sys.exit(1)
        times = stringToFloatList(timeList)

    return times, fileName

##############################################################################
# function to read/write a list of strings in a file
##############################################################################
def listFromFile(fileName):
  listInstance = []
  try:
    file = open(fileName,"r")
  except:
    print >> sys.stderr, "could not open file " + fileName
    return listInstance
  list_in_file = file.readlines()
  file.close()
  if not len(list_in_file):
    print >> sys.stderr, "No lines found in file " + fileName
    print >> sys.stderr, "Is the first line blank ?"
    return listInstance
  for line in list_in_file:
    if not line[0] == '#':
      listInstance.append(string.strip(line))
    else: pass
  return listInstance

def saveRandomTimes(timeList,fileName):
  file = open(fileName,"w")
  for time in timeList:
    file.write(time + '\n')
  file.close()

def stringToFloatList(listin):
  listout = []
  for line in listin:
    listout.append(float(line))
  return listout

def floatToStringList(listin):
  listout = []
  for line in listin:
    listout.append(repr(line))
  return listout

##############################################################################
# function to read in a list of files and extract the simInspiral tables
# and sngl_inspiral tables
##############################################################################
def readFiles(fileGlob,statistic=None):
  """
  read in the Sngl and SimInspiralTables from a list of files
  if Sngls are found, construct coincs, add injections (if any)
  also return Sims (if any)
  @param fileGlob: glob of input files
  @param statistic: statistic to use in creating coincs
  """
  #if fileGlob is empty return empty structures
  if not fileGlob:
    print "Warning: No glob specified, returning empty structures..."
    return None, CoincInspiralUtils.coincInspiralTable(), None

  # if there aren't any files globbed exit
  #fList = glob.glob(fileGlob)
  #if not fList:
  #  print >>sys.stderr, "The glob for " + fileGlob + " returned no files"
  #  sys.exit(1)
  fList = fileGlob
  sims = None
  coincs = None
  search = None
  for thisFile in fList:
    extension = thisFile.split('.')[len(thisFile.split('.'))-1]
    if extension == 'gz': gz = True
    else: gz = False
    doc = utils.load_filename(thisFile,False,gz)
    # extract the sim inspiral table
    try:
      simInspiralTable = \
          table.get_table(doc, lsctables.SimInspiralTable.tableName)
      if sims: sims.extend(simInspiralTable)
      else: sims = simInspiralTable
    except: simInspiralTable = None

    # extract the sngl inspiral table, construct coincs
    try: snglInspiralTable = \
      table.get_table(doc, lsctables.SnglInspiralTable.tableName)
    except: 
      snglInspiralTable = None
      searchSumTable = None
    if snglInspiralTable:
      coincInspiralTable = \
        CoincInspiralUtils.coincInspiralTable(snglInspiralTable,statistic)
      if simInspiralTable:
        coincInspiralTable.add_sim_inspirals(simInspiralTable)
      # extract the search_summary table only if a sngl inspiral table is found
      searchSumTable = table.get_table(doc,lsctables.SearchSummaryTable.tableName)
      if coincs: 
        coincs.extend(coincInspiralTable)
        search.extend(searchSumTable)         
      else: 
        coincs = coincInspiralTable
        search = searchSumTable    
  print "processed " + str(len(fList)) + " files..." 
  #for ck in coincs:
  #  print getattr(ck, 'event_id'), getattr(ck, 'numifos')
  return sims,coincs,search


#############################################################################
# function to set up directories
#############################################################################

def createdir(newDir):
  try:
    os.mkdir(newDir)
  except:
    pass


def setupdirs():

  try:
    os.chdir("clustered")
    os.chdir('..')
  except: os.mkdir("clustered")

  try:
    os.chdir("found")
    os.chdir('..')
  except: os.mkdir("found")

  try:
    os.chdir("missed")
    os.chdir('..')
  except: os.mkdir("missed")

  try:
    os.chdir("followuptrigs")
    os.chdir('..')
  except: os.mkdir("followuptrigs")

  try:
    os.chdir("followupfound")
    os.chdir('..')
  except: os.mkdir("followupfound")

  try:
    os.chdir("followupmissed")
    os.chdir('..')
  except: os.mkdir("followupmissed")

  try:
    os.chdir("logs")
    os.chdir('..')
  except: os.mkdir("logs")

  try:
    os.chdir("datafind_cache")
    os.chdir('..')
  except: os.mkdir("datafind_cache")

#############################################################################
# function to return the number of slides in a file (as a string)
#############################################################################
def getslidenum(fName):
  command = "grep -m 1 -e '--num-slides' " + fName + " | sed -e 's@\"@\'@g"
  fStr = os.popen(command).readlines()
  if fStr:
    fStrlist = fStr[0].rsplit(",")
    return fStrlist[-2]
  else:
   return "0"

#############################################################################
# function to glob files
#############################################################################
def globxmlandinj(opts):

  #Glob for the files both injections and trigger files
  fList = glob.glob(opts.xml_glob)
  if not fList:
    print >>sys.stderr, "The glob for " + opts.xml_glob + " returned no files"
    sys.exit(1)

  if opts.injection_glob:
    iList = glob.glob(opts.injection_glob)
    if not iList:
      print >> sys.stderr, "The glob for " + opts.injection_glob + " returned no files"
      sys.exit(1)
  else:
    iList = None

  return fList,iList

##############################################################################
# function to coire the input files
##############################################################################
def coire(opts,fList,iList=None):
  """
  do coires
  """
  sims = None
  coincs = None

  # we need to get slide num and data type from the files
  # this is just hard coded now!!!
  for xmls in fList:
    if opts.verbose:
      print "running lalapps_coire on " + xmls
    numslides = getslidenum(xmls)
    command = "lalapps_coire " + \
              "--glob '" + xmls + "'" + \
              " --data-type " + str(opts.data_type) + \
              " --num-slides " + numslides + " --coinc-stat " + \
              opts.statistic + " --cluster-time " + \
              str(1000*opts.cluster_time)

    if iList:
      command += " --injection-file " + iList[0]
      command += " --injection-window " + str(opts.injection_coinc_time)
      command += " --missed-injections missed/MISSED" + xmls
      command += " --output found/FOUND" + xmls
    else:
      command += " --output clustered/CLUSTER"
      command += str(opts.cluster_time) + "s_" + xmls
    if opts.bitten_l_a and opts.bitten_l_b:
      command += " --h1-bittenl-a " + str(opts.bitten_l_a)
      command += " --h2-bittenl-a " + str(opts.bitten_l_a)
      command += " --l1-bittenl-a " + str(opts.bitten_l_a)
      command += " --h1-bittenl-b " + str(opts.bitten_l_b)
      command += " --h2-bittenl-b " + str(opts.bitten_l_b)
      command += " --l1-bittenl-b " + str(opts.bitten_l_b)

    os.system(command)

##############################################################################
# function to extract the statistic information
##############################################################################
def getstatistic(stat, bla, blb):

  if stat == "effective_snrsq":
    newstat = "effective_snr"
  else:
    newstat = stat

  statistic=CoincInspiralUtils.coincStatistic( newstat, bla, blb )
  return statistic


#############################################################################
# Follow up list class definition
#############################################################################
class followUpList:
  """
  Class to hold gps and ifo pairs to send to subsequent functions
  It also holds an instance of the coinc class which contains
  All of the relevant xml information
  """
  def __init__(self,Coincs = None, Missed = None ):
    self.gpsTime = {"H1" : None, "H2" : None, "L1" : None,
                  "G1" : None, "V1" : None, "T1" : None}
    self.ifos = '' # added to construct a new field in "followups", see function getfollowuptrigs
    self.ifolist_in_coinc = None
    self.ifoTag = ''
    self.coincs = Coincs
    self.missed = Missed
    self.eventID = None
    self.stat = None
    self.far = None
    self.page = None
    self.summarydir = None
    self.summarypage = None
    self.types = ['H1H2', 'H1H2L1', 'H1H2L1V1', 'H1H2V1', 'H1L1', 'H1L1V1', 'H1V1', 'H2L1', 'H2L1V1', 'H2V1', 'L1V1']

  def get_coinc_type(self):
    ifostring = ""
    for t in ['H1','H2','L1','V1']:
      if self.gpsTime[t]: ifostring+=t
    return ifostring

  def add_coincs(self,Coincs):
    setattr(self,"coincs",Coincs)
    # convert the ilwdchar "Coincs.event_id" into an integer. This removes
    # the extra table_name and column_name and keeps only the ID string
    self.eventID = int(Coincs.event_id)
    self.statValue = Coincs.stat
    self.ifos, self.ifolist_in_coinc = Coincs.get_ifos()
    if self.is_trigs():
      self.summarydir = "followuptrigs"
    if self.is_found():
      self.summarydir = "followupfound"
  
  def add_missed(self,Missed):
    setattr(self,"missed",Missed)
    self.summarydir = "followupmissed"
  
  def is_trigs(self):
    if isinstance(self.coincs,CoincInspiralUtils.coincInspiralTable.row):
      return 1
  
  def is_found(self):
    sim = None
    try: 
      sim = isinstance(self.coincs.sim,lsctables.SimInspiral)
    except: return 0
    if sim:
      return 1
  def is_missed(self):
    if isinstance(self.missed,lsctables.SimInspiralTable):
      return 1
  def add_page(self,page):
    self.page = page

#############################################################################
# Function to generate a trigbank xml file
#############################################################################
def generateXMLfile(cp,ckey,ifo,outputPath=None,type='plot',use_max_template=None,use_col_from_installation=None):

  if outputPath:
    try:
      os.mkdir(outputPath) 
    except: pass

  xmldoc = ligolw.Document()
  xmldoc.appendChild(ligolw.LIGO_LW())
 
  # if we want our trigbank files to use the loudest template
  maxSNR = 0
  if use_max_template:
    maxSNR = 0
    maxIFO = ""
    for t in ckey:
      snr = t.snr
      if snr > maxSNR:
        maxSNR = snr
        maxIFO = t.ifo
    trig = getattr(ckey,maxIFO)
  else:
    trig = getattr(ckey,ifo)

  if type == "coh":
    if cp.has_option("followup-coh-trigbank",ifo+"_channel"):
      trig.channel = cp.get("followup-coh-trigbank",ifo+"_channel")
    else:
      print >> sys.stderr, "the section [followup-coh-trigbank] in the .ini file should contain a field \""+ifo+"_channel\""
      sys.exit(1)
  else:
    properChannelTrig = getattr(ckey,ifo)
    trig.channel = properChannelTrig.channel
  trig.ifo = ifo
  #print ifo, getattr(ckey,ifo).ifo
  #print trig.channel, trig.ifo, maxSNR, getattr(ckey, 'event_id')
  # BEFORE WE MAKE A NEW TABLE FIGURE OUT WHAT COLUMNS ARE VALID !!!
  valid_columns = trig.__slots__
  columns = []
  notcolumns = []
  for col in valid_columns:
    try: 
      getattr(trig,col)
      columns.append(col)
    except:
      notcolumns.append(col)
  # IF "use_col_from_installation" IS TRUE, ADD NEW COLUMNS TO THE SNGL_INSPIRAL TABLE
  if use_col_from_installation:
    for col in notcolumns:
      print "\n adding column " + col
      columns.append(col)
      setattr(trig,col,0)

  process_params_table = lsctables.New(lsctables.ProcessParamsTable)
  xmldoc.childNodes[-1].appendChild(process_params_table) 

  sngl_inspiral_table = lsctables.New(lsctables.SnglInspiralTable,columns)
  xmldoc.childNodes[-1].appendChild(sngl_inspiral_table)
  sngl_inspiral_table.append(trig)

  fileName = ifo + '-TRIGBANK_FOLLOWUP_' + type + str(int(ckey.event_id)) + ".xml.gz"
  if outputPath:
    fileName = outputPath + '/' + fileName
  utils.write_filename(xmldoc, fileName, verbose = False, gz = True)   

def generateBankVetoBank(fuTrig, ifo,sngl,subBankSize,outputPath=None):
  
  trig =  getattr(fuTrig.coincs,ifo)
  mass = trig.mass1 + trig.mass2
  if outputPath:
    try:
      os.mkdir(outputPath)  
    except: pass
  xmldoc = ligolw.Document()
  xmldoc.appendChild(ligolw.LIGO_LW())
  process_params_table = lsctables.New(lsctables.ProcessParamsTable)
  xmldoc.childNodes[-1].appendChild(process_params_table)
  valid_columns = lsctables.SnglInspiralTable.validcolumns
  columns = []
  notcolumns = []
  for col in valid_columns:
    try:
      getattr(sngl[0],col)
      columns.append(col)
    except:
      notcolumns.append(col) 
  sngl_inspiral_table = lsctables.New(lsctables.SnglInspiralTable)
  sngl.sort(lambda a, b: cmp(a.mtotal, b.mtotal))
  index = sngl.getColumnByName('mtotal').index(mass)
  fromEnd = len(sngl)-index-int(subBankSize/2)
  if fromEnd < 0:
    sngl_sub = sngl[index+fromEnd-int(subBankSize/2):-1]
  else: 
    sngl_sub = sngl[index-int(subBankSize/2):index+int(subBankSize/2)]
 
  for row in sngl_sub:
    for col in notcolumns:
      setattr(row,col,0)
    sngl_inspiral_table.append(row)
  xmldoc.childNodes[-1].appendChild(sngl_inspiral_table)
 
  fileName = ifo + '-BANKVETO_FOLLOWUP_' + str(fuTrig.eventID) + ".xml.gz"
  if outputPath:
    fileName = outputPath + '/' + fileName
  utils.write_filename(xmldoc, fileName, verbose = True, gz = True)
  return fileName

#############################################################################
# Function to return the follow up list of coinc triggers
#############################################################################
def getfollowuptrigs(cp,numtrigs,trigtype=None,page=None,coincs=None,missed=None,search=None,trigbank_test=None,ifar=True,add_columns=False):

  followups = []
  xmfilenum = 0
  if coincs:
      if not ifar:
          sim = None
          try:
              sim = isinstance(coincs[0].sim,lsctables.SimInspiral)
          except: pass
          if sim:
	      print "following up injections..."
              coincs.sort() # This does an descending sort even for found inj !!! CHANGE THIS? It USED TO BE ASCENDING
          else:
              coincs.sort()
          numTrigs = 0
          for ckey in coincs:
              fuList = followUpList()
              fuList.add_coincs(ckey)
              if page:
                  fuList.add_page(page)
              ifo_list = ['H1','H2','L1','G1','V1','T1']
              for ifo in ifo_list:
                  try:
                      getattr(ckey,ifo)
		      #print getattr(ckey, 'numifos'), getattr(ckey, 'event_id')
                      fuList.gpsTime[ifo] = (float(getattr(ckey,ifo).end_time_ns)/1000000000)+float(getattr(ckey,ifo).end_time)
                  except: fuList.gpsTime[ifo] = None
        
                  if fuList.gpsTime[ifo] and trigbank_test:
                      generateXMLfile(cp,ckey,ifo,'trigTemplateBank',"plot",None,add_columns)
                      generateXMLfile(cp,ckey,ifo,'trigTemplateBank',"notrig",None,add_columns)
                      # Also make a trigbank xml with the max template
                      generateXMLfile(cp,ckey,ifo,'trigTemplateBank',"coh",True,add_columns)
		      xmfilenum += 3
	      # if the trigger type is wrong don't count it
              if trigtype: 
	        stop = 0
	        for t in trigtype.split(','):
		  if t.strip() == fuList.get_coinc_type(): stop = 1
		if not stop: continue  
		  
              numTrigs += 1
              if numTrigs > int(numtrigs):
                break
	      
              # now, find the ifoTag associated with the triggers, 
              # using the search summary tables...
              if fuList.ifolist_in_coinc:
                  firstIfo = fuList.ifolist_in_coinc[0]
                  triggerTime = fuList.gpsTime[firstIfo]
                  if search:  
                      for chunk in search:
                          out_start_time = float(chunk.out_start_time)
                          out_start_time_ns = float(chunk.out_start_time_ns)/1000000000
                          out_end_time = float(chunk.out_end_time)
                          out_end_time_ns = float(chunk.out_end_time_ns)/1000000000
                          if ( (triggerTime >= (out_start_time+out_start_time_ns)) and (triggerTime <= (out_end_time+out_end_time_ns)) ):
                              fuList.ifoTag = chunk.ifos
                              break
              followups.append(fuList)
              if search:
                # generate a cohbank xml file for this coinc trigger
                generateCohbankXMLfile(ckey,fuList.gpsTime[firstIfo],fuList.ifoTag,fuList.ifolist_in_coinc,search,'trigTemplateBank',"coh",add_columns)
                # generate a trigbank with max templates for ifo in science but not found in coincidence
                if trigbank_test:
                  for j in range (0,len(fuList.ifoTag)-1,2):
                    itf = fuList.ifoTag[j:j+2]
                    if not itf in fuList.ifolist_in_coinc:
                      generateXMLfile(cp,ckey,itf,'trigTemplateBank',"coh",True,add_columns)

      else:

          ifarList=list()
          for ckey in coincs:
              myIFAR = getattr(ckey,ckey.get_ifos()[1][0]).alpha
              myKey = ckey
              ifarList.append([myIFAR,myKey])
          ifarList.sort()
          ckeyList=list()
          for key in ifarList:
              ckeyList.append(key[1])
          numTrigs = 0
          for ckey in ckeyList:
              fuList = followUpList()
              fuList.far = getattr(ckey,ckey.get_ifos()[1][0]).alpha
              fuList.add_coincs(ckey)
              if page:
                  fuList.add_page(page)
              ifo_list = ['H1','H2','L1','G1','V1','T1']
              for ifo in ifo_list:
                  try:
                      getattr(ckey,ifo)
                      fuList.gpsTime[ifo] = (float(getattr(ckey,ifo).end_time_ns)/1000000000)+float(getattr(ckey,ifo).end_time)
                  except: fuList.gpsTime[ifo] = None
                  if fuList.gpsTime[ifo] and trigbank_test:
                      generateXMLfile(cp,ckey,ifo,'trigTemplateBank',"plot",None,add_columns)
                      generateXMLfile(cp,ckey,ifo,'trigTemplateBank',"notrig",None,add_columns)
                      # Also make a trigbank xml with the max template
                      generateXMLfile(cp,ckey,ifo,'trigTemplateBank',"coh",True,add_columns)
		      xmfilenum += 3

              # if the trigger type is wrong don't count it
              if trigtype:
                stop = 0
                for t in trigtype.split(','):
                  if t.strip() == fuList.get_coinc_type(): stop = 1
                if not stop: continue

              numTrigs += 1
              if numTrigs > int(numtrigs):
                break

              # now, find the ifoTag associated with the triggers, 
              # using the search summary tables...
              if fuList.ifolist_in_coinc:
                  firstIfo = fuList.ifolist_in_coinc[0]
                  triggerTime = fuList.gpsTime[firstIfo]
                  if search:  
                      for chunk in search:
                          out_start_time = float(chunk.out_start_time)
                          out_start_time_ns = float(chunk.out_start_time_ns)/1000000000
                          out_end_time = float(chunk.out_end_time)
                          out_end_time_ns = float(chunk.out_end_time_ns)/1000000000
                          if ( (triggerTime >= (out_start_time+out_start_time_ns)) and (triggerTime <= (out_end_time+out_end_time_ns)) ):
                              fuList.ifoTag = chunk.ifos
                              break 
              followups.append(fuList)
              # generate a cohbank xml file for this coinc trigger
              if search:
                generateCohbankXMLfile(ckey,fuList.gpsTime[firstIfo],fuList.ifoTag,fuList.ifolist_in_coinc,search,'trigTemplateBank',"coh",add_columns)
                print "produced cohbank files 2..."
                if trigbank_test:
                  for j in range (0,len(fuList.ifoTag)-1,2):
                    itf = fuList.ifoTag[j:j+2]
                    if not itf in fuList.ifolist_in_coinc:
                      generateXMLfile(cp,ckey,itf,'trigTemplateBank',"coh",True,add_columns)


  # the missed stuff doesnt work yet!!!
  print "produced " + str(xmfilenum) + " trig bank files..."

  # compute the trigger types found
  typesdict = {"H1H2" : 0, "H1L1" : 0, "H1V1" : 0, "H2L1" : 0, "H2V1" : 0, "L1V1" : 0, "H1H2L1" : 0, "H1H2V1" : 0, "H2L1V1" : 0, "H1L1V1" : 0, "H1H2L1V1" : 0}
  for f in followups:
    typesdict[f.get_coinc_type()] += 1
  for f in typesdict:
    print "found " + str(typesdict[f]) + " " + str(f) +  " triggers"

  if missed:
    followups
  return followups


#############################################################################
# Method to write a table of inspiral parameters
#############################################################################
def writeParamTable(trigger,opts):
  page = markup.page(mode="strict_html")
  page._escape = False
  #doctype="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">"""
  #doctype+="""\n<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">"""

  title = "Inspiral Parameters for trigger " + str(trigger.eventID)
  #page.init(title=title, doctype=doctype) 
  page.init(title=title)

  paramList = [['SNR','snr'],['CHISQ','chisq'],['Chirp Mass','mchirp'],['Eta','eta'],['Mass 1','mass1'],['Mass 2','mass2'],['Eff Dist (Mpc)', 'eff_distance']]

  page.add('<table bgcolor=cyan border=1px>')
  page.tr();
  page.td('Ifo');
  page.td('End Time')
  for param in paramList:
    page.td("<b>"+param[0]+"</b>");
  page.td('<b>Combined Stat</b>');
  if not opts.disable_ifarsorting:
    page.td('<b>FAR</b>');
  page.tr.close()
  for ifo in trigger.ifolist_in_coinc:
    page.tr();
    page.td(ifo);
    page.td(repr(trigger.gpsTime[ifo]));
    for param in paramList:
      page.td("%0.3f"%(eval("getattr(trigger.coincs,ifo)."+param[1]))); 
    page.td("%0.2f"%(trigger.statValue));
    if not opts.disable_ifarsorting:
      page.td("%0.4f"%(trigger.far))
    page.tr.close()
  page.table.close()

  if not os.access('PARAM_TABLES',os.F_OK):
    os.mkdir('PARAM_TABLES')
  else: pass
  html_file = file("PARAM_TABLES/table_" + str(trigger.eventID) + ".txt","w")
  html_file.write(page(False))
  html_file.close()

#############################################################################
# Class to hold summary HTML information for all of the functions
#############################################################################
class summaryHTMLTable:

  def __init__(self,trig):
    if trig.is_trigs() and not trig.is_found():
      self.summarypath =  "followuptrigs/"
    if trig.is_trigs() and trig.is_found():
      self.summarypath = "followupfound/"
    self.eventID = trig.eventID
    self.statValue = trig.statValue
    self.H1time = trig.gpsTime["H1"]
    self.H2time = trig.gpsTime["H2"]
    self.L1time = trig.gpsTime["L1"]
    self.G1time = trig.gpsTime["G1"]
    self.V1time = trig.gpsTime["V1"]
    self.T1time = trig.gpsTime["T1"]
    self.containers = []

class HTMLcontainer:

  def __init__(self,trig,name,alt_web=None):
    # The missed injections dont work yet!!!
    self.name = name.rsplit(".")[-1]
    self.detailpath = ""
    if trig.is_trigs() and not trig.is_found():   
      os.chdir("followuptrigs")
      try: 
        os.chdir(self.name)
        os.chdir("../../")
      except: 
        os.mkdir(self.name)
        os.chdir("../")
      self.detailpath = trig.page + "/followuptrigs/" + self.name + "/"
      self.localdetailpath = "followuptrigs/" + self.name + "/"

    if trig.is_trigs() and trig.is_found():
      os.chdir("followupfound")
      try:
        os.chdir(self.name)
        os.chdir("../../")
      except:
        os.mkdir(self.name)
        os.chdir("../")
      self.detailpath = trig.page + "/followupfound/" + self.name + "/"
      self.localdetailpath = "followupfound/" + self.name + "/"

    self.image = self.detailpath + str(trig.statValue) + "_" + str(trig.eventID) + "_" + self.name + ".png"
    self.localimage = self.localdetailpath + str(trig.statValue) + "_" + str(trig.eventID) + "_" + self.name + ".png" 
    self.text = "click here"
    if alt_web: name = alt_web
    else: name = self.name
    self.link = self.detailpath + str(trig.statValue) + "_" + str(trig.eventID) + "_" + name + ".html"
    self.locallink = self.localdetailpath + str(trig.statValue) + "_" + str(trig.eventID) + "_" + name + ".html"



##############################################################################
# Function to write the HTML tables to pages
##############################################################################
def writeIULHeader(file):
  file.write('<%method title>Follow Up Report</%method><%method headline>Follow Up Report</%method><%method cvsid>$Id$</%method>\n')

def beginSummaryTable(file, table):
  file.write("<h3>Trigger [" + str(table.eventID) + 
             "] with combined statistic = " + str(table.statValue) + "</h3>")
  file.write('\n<br><table width=800 border=1>')
  
def endSummaryTable(file, table):
  file.write('\n</table>')

def writeModule(file, container):
  file.write('\n<tr><td width=400><font color="red" size=5>'+
             container.name + '</font>')
  file.write('\n<br><a href= "' + container.link + '">' + container.text 
             + "</a></td>")
  file.write('\n<td><a href= "' + container.image + '">\n<img src="' + 
              container.image + '" width=400 alt="No Image"></a></td></tr>')

def writeHTMLTables(summaryHTMLlist):
  for table in summaryHTMLlist:
    tableFile = open(table.summarypath + str(table.statValue) + "_" + 
                      str(table.eventID) + "_summary.html" ,'w')
    beginSummaryTable(tableFile,table)
    for container in table.containers:
      writeModule(tableFile, container)
    endSummaryTable(tableFile,table)
    writeIULHeader(tableFile)
    tableFile.close()

class HTMLTable:
  def __init__(self):
    self.columns = []
    self.headers = []

  def add_column(self,rows,header):
    self.columns.append(rows)
    self.headers.append(header)

  def write(self,file):
    file.write('\n<br><table><tr>')
    cnt = 0
    for i in self.columns:
      file.write('<td><b>'+ self.headers[cnt]+'</b><table>')
      cnt +=1
      for j in i:
        file.write('<tr><td>'+str(j)+'</td></tr>\n')
      file.write('</table></td>')
    file.write('\n</tr></table><br>\n')

##############################################################################
# Function to publish the web tree
##############################################################################
def publishOnHydra(page):
  indexFile = open("index.html","w")
  patt = re.compile('.*summary.html')
  
  # First do the found injections
  files = os.chdir('followupfound')
  files = os.listdir('.')
  table = HTMLTable()
  fList = []
  stat = []
  ID = []
  if files:
    for f in files:
      temp = patt.match(f)
      if temp:
        fList.append((float(temp.group().rsplit('_')[0]), \
                  temp.group().rsplit('_')[1]))
    indexFile.write('<h3>Found Injection follow ups</h3>\n')
    sortedF = sorted(fList,key=operator.itemgetter(0),reverse=False)
    for i in sortedF:
      stat.append(str(i[0]))
      ID.append('<a href="' +page+ '/followupfound/'+str(i[0])+'_'+str(i[1])+
                '_summary.html">'+i[1]+'</a>')
    table.add_column(stat,'Stat Value')
    table.add_column(ID,'ID')
    table.write(indexFile)  
  os.chdir('..')

# then do trigs
  files = os.chdir('followuptrigs')
  files = os.listdir('.')
  table = HTMLTable()
  fList = []
  stat = []
  ID = []
  if files:
    for f in files:
      temp = patt.match(f)
      if temp:
        fList.append((float(temp.group().rsplit('_')[0]), \
                  temp.group().rsplit('_')[1]))
    indexFile.write('<h3>Found Trigger follow ups</h3>\n')
    sortedF = sorted(fList,key=operator.itemgetter(0),reverse=True)
    for i in sortedF:
      stat.append(str(i[0]))
      ID.append('<a href="' +page+ '/followuptrigs/'+str(i[0])+'_'+str(i[1])+
                '_summary.html">'+i[1]+'</a>')
    table.add_column(stat,'Stat Value')
    table.add_column(ID,'ID')
    table.write(indexFile)
  os.chdir('..')



#  # Then do the triggers 
#  files = os.chdir('followuptrigs')
#  files = os.listdir('.')
#  table = HTMLTable()
#  fList = []
#  stat = []
#  ID = []
#  if files:
#    for f in files:
#      temp = patt.match(f)
#      if temp:
#        fList.append((float(temp.group().rsplit('_')[0]), \
#                  temp.group().rsplit('_')[1]))
#    indexFile.write('<h3>Trigger follow ups</h3>\n')
#    sortedF = sorted(fList,key=operator.itemgetter(0),reverse=True)
#    for i in sortedF:
#      stat.append(str(i[0]))
#      ID.append('<a href="' +page+ '/followuptrigs/'+str(i[0])+'_'+str(i[1])+
#                '_summary.html">'+i[1]+'</a>')    
#    table.add_column(stat,'Stat Value')
#    table.add_column(ID,'ID')
#    table.write(indexFile)
#  
#  os.chdir('..')

  writeIULHeader(indexFile)
  indexFile.close()
  #This needs to be done so that it doesn't keep writing over this 
  #directory... ;)
  os.system('scp -r index.html followuptrigs followupfound followupmissed ' +
            'hydra.phys.uwm.edu:/home/htdocs/uwmlsc/root/'+
            page + '.')

############################################################
# Class for checking follow up GPS times to Nelson's veto lists.
############################################################
class nVeto:
  """
  Author: Cristina Valeria Torres
  Provides a method for checking S5y1 and S5y2 follow up candidates
  against locally cached static veto lists produced by Nelson Christensen
  """
  def __init__(self):
    """
    Initialize this class.
    """
    self.database=list([["L1","/archive/home/romain/Projects/LowMassCBC/20051104-20061114/triggers/upperlimits_v99_july08/nelsonVetoes/L1/VetoLists",list()],
                        ["H1","/archive/home/romain/Projects/LowMassCBC/20051104-20061114/triggers/upperlimits_v99_july08/nelsonVetoes/H1/VetoLists",list()],
                        ["H2","/archive/home/romain/Projects/LowMassCBC/20051104-20061114/triggers/upperlimits_v99_july08/nelsonVetoes/H2/VetoLists",list()]])
      #Form [[filename,list(gpsIntervals)],[filename2,list(gpsIntervals)]...
    self.vetoExtension=".veto"
    self.tolWin=float(0.01)
    self.filesLoaded=bool(False)
  #End self.__init__()

  def __loadFiles__(self):
    """
    This method is invoked automatically if required.
    It creates the dynamically structures to hold the veto lists.
    """
    #Check that the paths specified exist

    for ifoName,ifoPath,vetoData in self.database:
        if not os.path.exists(ifoPath):
          raise IOError("%s Path Invalid: %s"%(ifoName,ifoPath))
    for index in range(self.database.__len__()):
      self.__processPath__(index)
    self.filesLoaded=True
  #End self.__loadFiles__()

  def __processPath__(self,index=""):
    """
    This method is not to be called explicity.  It is called by
    self.__loadFiles__(). The role of this method is to fill up 
    the instance with the data required to check the veto intervals.
    """
    path=self.database[index][1]
    listOfFiles=os.listdir(path)
    listOfVetoFiles=list()
    for file in listOfFiles:
      if file.endswith(self.vetoExtension):
        listOfVetoFiles.append(file)
    listOfFiles=[os.path.normpath(path+"/"+file) for file in listOfVetoFiles]
    for filename in listOfFiles:
      fileData=list()
      fp=open(str(filename),'r')
      txtData=fp.readlines()
      fp.close()
      for row in txtData:
        a,b,c=map(float,row.split())
        fileData.append([a,b,c])
      self.database[index][2].append([filename,fileData])
  #End self.__processPath__()

  def __checkIntervals__(self,vList,gpsTime):
    """
    This method is not to be called explicity. It is called by
    self.findInterval(IFO,gpsTime).  This method returns a 
    text string giving the veto list names and intervals that
    the gpsTime intersects with.
    """
    vetoMatch=list()
    for vetoNameLong,vetoList in vList:
      for startT,stopT,KWSig in vetoList:
        if ((startT-self.tolWin)<=gpsTime<=(stopT+self.tolWin)):
          vetoMatch.append([os.path.basename(vetoNameLong).split(self.vetoExtension,1)[0],startT,stopT])
    tmpList=list()
    for a,b,c in vetoMatch:
      tmpList.append("%s %s %s\n"%(str(a),str(b),str(c)))
    outputString=str().join(tmpList)
    if vetoMatch.__len__()==0:
      outputString="%s %s %s\n"%("NONE","0","0")
    return outputString
  #End self.__checkIntervals__()

  def setIfoPath(self,ifoName="",ifoPath=""):
    """
    If you want to use something other than the hardwired path
    defaults to the veto files invoke this method with the IFO
    for which you need to adjust the path to those veto files.
    ie To adjust L1 paths do
    self.setIfopath("L1","/path/to/new/veto/files")
    """
    myIndex=-1
    for i in range(self.database.__len__()):
      if (self.database[i][0].lower()==ifoName.lower()):
        myIndex=i
    if myIndex==-1:
      raise IOError("%s Invalid IFO Name Path Unchanged."%(ifoName))
    self.database[myIndex][1]=ifoPath
  #End self.setIfoPath()

  def findInterval(self,ifoName,gpsTime):
    """
    Given an IFO name and GPS time it searches the veto lists to
    determine which if any of the veto intervals interset this
    gps time.
    """
    if not self.filesLoaded:
      self.__loadFiles__()
    myIndex=-1
    for i in range(self.database.__len__()):
      if (self.database[i][0].lower()==ifoName.lower()):
        myIndex=i
    if myIndex==-1:
      raise IOError("%s Invalid IFO Name"%(ifoName))
    vList=self.database[myIndex][2]
    outputString=self.__checkIntervals__(vList,gpsTime)
    return outputString
  #End self.findInterval()
#
#End nVeto() Class Definition
############################################################


#############################################################################
# Function to generate a coherentbank xml file
#############################################################################
def generateCohbankXMLfile(ckey,triggerTime,ifoTag,ifolist_in_coinc,search,outputPath=None,type='plot',use_col_from_installation=None):

  if outputPath:
    try:
      os.mkdir(outputPath)
    except: pass

  xmldoc = ligolw.Document()
  xmldoc.appendChild(ligolw.LIGO_LW())

  # Cohbank files use the loudest single-ifo template for all ifos in a coinc
  maxSNR = 0;
  maxIFO = ""
  for t in ckey:
    snr = t.snr
    if snr > maxSNR:
      maxSNR = snr
      maxIFO = t.ifo
  trig = getattr(ckey,maxIFO)

  #This is a hack since data channel can differ among ifos
  #properChannelTrig = getattr(ckey,maxIFO)
  #trig.channel = properChannelTrig.channel
  # BEFORE WE MAKE A NEW TABLE FIGURE OUT WHAT COLUMNS ARE VALID !!!
  valid_columns = trig.__slots__
  columns = []
  notcolumns = []
  for col in valid_columns:
    try:
      getattr(trig,col)
      columns.append(col)
    except:
      notcolumns.append(col)
  # IF "use_col_from_installation" IS TRUE, ADD NEW COLUMNS TO THE SNGL_INSPIRAL TABLE
  if use_col_from_installation:
    for col in notcolumns:
      print "\n adding column " + col
      columns.append(col)
      setattr(trig,col,0)

  process_table = lsctables.New(lsctables.ProcessTable)
  xmldoc.childNodes[-1].appendChild(process_table)

  process_params_table = lsctables.New(lsctables.ProcessParamsTable)
  xmldoc.childNodes[-1].appendChild(process_params_table)

  search_summary_table = lsctables.New(lsctables.SearchSummaryTable)
  xmldoc.childNodes[-1].appendChild(search_summary_table)
  for chunk in search:
    out_start_time = float(chunk.out_start_time)
    out_start_time_ns = float(chunk.out_start_time_ns)/1000000000
    out_end_time = float(chunk.out_end_time)
    out_end_time_ns = float(chunk.out_end_time_ns)/1000000000
    if ( (triggerTime >= (out_start_time+out_start_time_ns)) and (triggerTime <= (out_end_time+out_end_time_ns)) ):
      search_summary_table.append(chunk)
      break

  sngl_inspiral_table = lsctables.New(lsctables.SnglInspiralTable,columns)
  xmldoc.childNodes[-1].appendChild(sngl_inspiral_table)
  # Each coherent bank file should have trig rows for all ifos in a coinc
  #for ifo in ifolist_in_coinc:
  # Each coherent bank file should have trig rows for all ifos in science mode

  for j in range(0,len(ifoTag)-1,2):
    itf = ifoTag[j:j+2]
    trigger = copy.deepcopy(trig)
    trigger.ifo = itf
    sngl_inspiral_table.append(trigger)

  fileName = ifoTag + '-COHBANK_FOLLOWUP_' + str(int(ckey.event_id)) + '-' + str(int(triggerTime)) + "-2048.xml.gz"
  if outputPath:
    fileName = outputPath + '/' + fileName
  utils.write_filename(xmldoc, fileName, verbose = False, gz = True)

  return maxIFO

######################################################################
#New Class Definition for determining DQ segments active for a given
#GPS time 
#
class followupdqdb:
    """
    This class provides a method for doing DQ flag queries required
    by the follow up pipeline when creating the automatic checklists.
    Invoking this class requires a boolean option if you 
    need to override the default behavior for this class
    initialization.
    To override the default initialization call like:
    dq=followupDQdb(True)
    else just do not worry about it and everything should work.
    """
    def __init__(self,default=False):
        """
        The __init__ method which can be overrridden using 
        other methods defined in this class.
        """
        self.defaultVersion=99
        self.activeRecords="1"
        self.db=None
        self.dbSocket=None
        self.myHome=None
        self.myHome=os.getenv("HOME")
        self.urlPattern="http://ldas-cit.ligo.caltech.edu/segments/S5/%s/dq_segments.txt"
        self.pathPattern="%s/%s/dq_segments.txt"
        self.sqlFile="/followupDQ.sqlite"
        self.sqlPath=self.myHome
        self.ifoList=["L1","H1","H2"]
        self.dbFiles=[]
        for ifo in self.ifoList:
            thisFile=self.pathPattern%(self.myHome,ifo)
            thisUrl=self.urlPattern%(ifo)
            thisIfo=ifo
            thisFileExists=os.path.isfile(thisFile)
            self.dbFiles.append([thisIfo,thisFile,thisUrl,thisFileExists])
        #Default Behavior Code Below
        if not(default) and os.path.isfile(self.sqlPath+self.sqlFile):
            self.__connectDB__()
            try:
                x=self.__createRawCursor__()
                for table in self.ifoList:
                    x.execute("select * from %s limit 100"%(table))
                del x
            except:
                sys.stderr.write("Sqlite database at %s seems\
 corrupted. It will be rebuilt.\n"%(self.sqlPath+self.sqlFile))
                self.db.close()
                self.db=None
                os.unlink(self.sqlPath+self.sqlFile)
                self.createDB()
                self.__connectDB__()
        elif not(default) and not(os.path.isfile(self.sqlPath+self.sqlFile)):
            self.createDB()
            self.__connectDB__()
        else:
            self.db=None
    #End __init__()

    def __connectDB__(self):
        """
        Simple method to wrap connections to the DB to start queries.
        """
        self.db=sqlite.connect(self.sqlPath+self.sqlFile)
    #End connectDB()

    def __disconnectDB__(self):
        """
        Wrapper method to close the database file.
        """
        self.db.commit()
        self.db.close()
    #End __disconnectDB__()

    def close(self):
      """
      This explicity allows the user to close the database when done
      making all the queries we want.  Closing the DB helps prevent
      corruption and clears existing locks to the DQ so others can add
      elements to the DB.
      """
      self.__disconnectDB__()
    #End close()

    def __createRawCursor__(self):
        """
        A method that is only used for testing.  It return a cursor 
        object to the database currently open.
        """
        return self.db.cursor()
    #End __createRawCursor__()

    def createDB(self):
        """
        Method to create the sqlite database and install it to 
        location sqlPath.
        """
        sys.stderr.write("Trying to create SQLite database.\n")
        self.__connectDB__()
        self.dbSocket=self.db.cursor()
        for table,file,url,exists in self.dbFiles:
            sys.stderr.write("Adding table for %s\n"%(table))
            if not exists:
                sys.stderr.write("Missing %s fetching it from %s \n"%(file,url))
                sys.stderr.write("Downloading... please wait.\n")
                myPath=os.path.dirname(file)
                if not os.path.exists(myPath):
                    sys.stderr.write("File path not found creating\
path %s\n"%(myPath))
                    os.makedirs(myPath)
                urllib.urlretrieve(url,filename=file)
                sys.stderr.write("Downloaded. Saved to %s \n"%(file))
                sys.stderr.write("Converting to SQL syntax and inserting.\n")
            commandString="create table %s (flag text,version\
 integer,start integer,stop integer, active integer)"%(table)
            self.dbSocket.execute(commandString)
            fp=open(file,"r")
            for row in fp.readlines():
                token=None
                if len(row) > 0 and row[0] != "#":
                    token=row.split()
                    if token.__len__() < 5:
                        print "Problems with file %s"%(file)
                        self.dbSocket.commit()
                        db.close()
                        os.unlink(self.sqlPath+self.sqlFile)
                        os.abort()
                    else:
                        commandString2="insert into %s \
(flag,version,start,stop,active) values ('%s',%i,%i,%i,%i)"\
%(table,token[0],int(token[1]),int(token[2]),int(token[3]),int(token[4]))
                        self.dbSocket.execute(commandString2)
            self.db.commit()
            fp.close()
        self.db.close()
        sys.stderr.write("Created SQLite database and closed it.\n")
    #End method createDB            


    def setURL(self,ifo=None,url=None):
        """
        This method allows use to specify a ifo L1 etc and the URL
        to use to go onto the web fetching the appropriate DQ segments
        file. If the method is called with invalid options it does
        nothing.
        """
        if not(ifo.upper() in self.ifoList) or url == None:
            return
        for i in range(0,self.dbFiles.__len__()):
            if self.dbFiles[i][0] == ifo:
                self.dbFiles[i][2]=url
        return
    #End setURL()

    def setFile(self,ifo=None,file=None):
        """
        This method allows you to specify an override location
        specifying where or where to install the ASCII dq_segments
        type file for a given IFO.
        """
        if not(ifo.upper() in self.ifoList) or file == None:
            return
        for i in range(0,self.dbFiles.__len__()):
            if self.dbFiles[i][0] == ifo:
                self.dbFiles[i][1]=file
                if os.path.isfile(self.dbFiles[i][1]):
                    self.dbFiles[i][3]=True
                else:
                  self.dbFiles[i][3]=False
        return
    #End setFile()

    def setDB(self,file=None):
        """
        This method set the location to install the sqlite file to
        or the location of a preinstalled sqlite filed derived from
        ASCII dq_segments files.
        """
        if file==None:
            return
        filename=os.path.normpath(file)
        self.sqlFile=os.path.basename(filename)
        self.sqlPath=os.path.dirname(filename)
        return

    def setVersion(self,version=None):
        """
        This method sets the version number or greater to fetch from
        the segment lists sqlite database.
        """
        if (version == None):
           return
        self.defaultVersion=version
        return

    def queryDB(self,gps=None,window=int(30)):
        """
        Takes two arguments the gps time as an integer and the window
        to search around this time with default to 30 seconds. It
        returns a dictionary variable assesible via
        X["ifo"] which will be a list of [flag,version,start,stop,active]
        
        """
        try:
            dbSocket=self.__createRawCursor__()
        except:
            self.__connectDB__()
            dbSocket=self.__createRawCursor__()
        results=dict()
        for table in self.ifoList:
            results[table]=list()
            iStart=int(gps)-int(window)
            iStop=int(gps)+int(window)
            commandString=\
                "select * from %s where\
     (((start<=%i) and (stop >= %i)) or\
    ((start>=%i) and (stop <= %i)) or\
    ((start<=%i) and (stop >= %i))) and (active == 1)\
     and version == %i \
     order by flag,version desc"%\
    (table,\
    iStart,iStart,\
    iStart,iStop,\
    iStop,iStop,self.defaultVersion)
            dbSocket.execute(commandString)            
            results[table]=dbSocket.fetchall()
        return results
    #End def queryDB()

#End followupDQdb class()
######################################################################
