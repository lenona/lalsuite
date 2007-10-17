"""
Classes needed for the inspiral analysis pipeline.
This script produced the necessary condor submit and dag files to run
the standalone inspiral code on LIGO data
"""

__author__ = 'Duncan Brown <duncan@gravity.phys.uwm.edu>'
__date__ = '$Date$'
__version__ = '$Revision$'[11:-2]

import string
import exceptions
from glue import pipeline


class InspiralError(exceptions.Exception):
  def __init__(self, args=None):
    self.args = args


#############################################################################

class InspiralAnalysisJob(pipeline.CondorDAGJob, pipeline.AnalysisJob):
  """
  An inspiral analysis job captures some of the common features of the specific
  inspiral jobs that appear below.  Spcecifically, the universe and executable
  are set, the stdout and stderr from the job are directed to the logs 
  directory. The path to the executable is determined from the ini file.
  """
  def __init__(self,cp,sections,executable,dax=False):
    """
    cp = ConfigParser object from which options are read.
    sections = sections of the ConfigParser that get added to the opts
    executable = executable name in ConfigParser
    """
    self.__executable = cp.get('condor',executable)
    self.__universe = cp.get('condor','universe')
    pipeline.CondorDAGJob.__init__(self,self.__universe,self.__executable)
    pipeline.AnalysisJob.__init__(self,cp,dax)
    self.add_condor_cmd('environment',"KMP_LIBRARY=serial;MKL_SERIAL=yes")

    for sec in sections:
      try: self.add_ini_opts(cp,sec)
      except: pass

    self.set_stdout_file('logs/' + executable + \
        '-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/' + executable + \
        '-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).err')
    self.set_sub_file(executable + '.sub')

#############################################################################

class TmpltBankJob(InspiralAnalysisJob):
  """
  A lalapps_tmpltbank job used by the inspiral pipeline. The static options
  are read from the sections [data] and [tmpltbank] in the ini file. The
  stdout and stderr from the job are directed to the logs directory. The job
  runs in the universe specfied in the ini file. The path to the executable
  is determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='TMPLTBANK'):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'tmpltbank'
    sections = ['data','tmpltbank']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)
    self.tag_base = tag_base


class InspInjJob(InspiralAnalysisJob):
  """
  A lalapps_inspinj job used by the grb inspiral pipeline. The static options
  are read from the section [inspinj] in the ini file. The
  stdout and stderr from the job are directed to the logs directory. The
  job runs in the universe specified in the ini file. The path to the
  executable is determined from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'inspinj'
    sections = ['inspinj']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)

    self.__listDone=[]
    self.__listNodes=[]

  def set_done(self, number, node):
    self.__listDone.append(number)
    self.__listNodes.append(node)

  def check_node(self, number):
    if self.__listDone.count(number):
      index=self.__listDone.index(number)
      return self.__listNodes[index]
    return None    


class BbhInjJob(InspiralAnalysisJob):
  """
  A lalapps_bbhinj job used by the online inspiral pipeline. The static options
  are read from the section [bbhinj] in the ini file. The
  stdout and stderr from the job are directed to the logs directory. The
  job runs in the universe specified in the ini file. The path to the 
  executable is determined from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'bbhinj'
    sections = ['bbhinj']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)


class RandomBankJob(InspiralAnalysisJob):
  """
  A lalapps_randombank job used by the inspiral pipeline. The static options
  are read from the section [randombank] in the ini file. The stdout and
  stderr from the job are directed to the logs directory. The job runs in the
  universe specfied in the ini file. The path to the executable is determined
  from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'randombank'
    sections = ['randombank']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)


class SplitBankJob(InspiralAnalysisJob):
  """
  A lalapps_splitbank job used by the inspiral pipeline. The static options
  are read from the section [splitbank] in the ini file. The stdout and stderr
  from the job are directed to the logs directory. The job runs in the
  universe specfied in the ini file. The path to the executable is determined
  from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'splitbank'
    sections = ['splitbank']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)


class InspiralJob(InspiralAnalysisJob):
  """
  A lalapps_inspiral job used by the inspiral pipeline. The static options
  are read from the sections [data] and [inspiral] in the ini file. The
  stdout and stderr from the job are directed to the logs directory. The job
  runs in the universe specfied in the ini file. The path to the executable
  is determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='INSPIRAL'):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'inspiral'
    sections = ['data','inspiral']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)
    self.tag_base = tag_base


class TrigToTmpltJob(InspiralAnalysisJob):
  """
  A lalapps_trigtotmplt job used by the inspiral pipeline. The static
  options are read from the section [trigtotmplt] in the ini file.  The
  stdout and stderr from the job are directed to the logs directory. The job
  always runs in the scheduler universe. The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='TRIGBANK'):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'trigtotmplt'
    sections = ['trigtotmplt']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)
    self.tag_base = tag_base


class IncaJob(InspiralAnalysisJob):
  """
  A lalapps_inca job used by the inspiral pipeline. The static options are
  read from the section [inca] in the ini file.  The stdout and stderr from
  the job are directed to the logs directory.  The path to the executable is 
  determined from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'inca'
    sections = ['inca']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)


class ThincaJob(InspiralAnalysisJob):
  """
  A lalapps_thinca job used by the inspiral pipeline. The static options are
  read from the section [thinca] in the ini file.  The stdout and stderr from
  the job are directed to the logs directory.  The path to the executable is 
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='THINCA'):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'thinca'
    sections = ['thinca']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)
    self.tag_base = tag_base


class SireJob(InspiralAnalysisJob):
  """
  A lalapps_sire job used by the inspiral pipeline. The stdout and stderr from
  the job are directed to the logs directory. The path to the executable is 
  determined from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'sire'
    sections = ['sire']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)

    # sire currently doesn't take GPS start/end times
    self.set_stdout_file('logs/sire-$(macroifo)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/sire-$(macroifo)-$(cluster)-$(process).err')


class CoireJob(InspiralAnalysisJob):
  """
  A lalapps_coire job used by the inspiral pipeline. The stdout and stderr from
  the job are directed to the logs directory. The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'coire'
    sections = ['coire']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)

    # coire currently doesn't take GPS start/end times
    self.set_stdout_file('logs/coire-$(macroifo)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/coire-$(macroifo)-$(cluster)-$(process).err')
    

class FrJoinJob(InspiralAnalysisJob):
  """
  A lalapps_frjoin job used by the inspiral pipeline. The path to the
  executable is determined from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'frjoin'
    sections = []
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)

    # frjoin currently doesn't take GPS start/end times
    self.set_stdout_file('logs/frjoin-$(cluster)-$(process).out')
    self.set_stderr_file('logs/frjoin-$(cluster)-$(process).err')


class CohBankJob(InspiralAnalysisJob):
  """
  A lalapps_coherent_inspiral job used by the inspiral pipeline. The static
  options are read from the section [cohbank] in the ini file.  The stdout and
  stderr from the job are directed to the logs directory.  The path to the
  executable is determined from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'cohbank'
    sections = ['cohbank']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)


class ChiaJob(InspiralAnalysisJob):
  """
  A lalapps_coherent_inspiral job used by the inspiral pipeline. The static
  options are read from the section [chia] in the ini file.  The stdout and
  stderr from the job are directed to the logs directory.  The path to the
  executable is determined from the ini file.
  """
  def __init__(self,cp,dax=False):
    """
    cp = ConfigParser object from which options are read.
    """
    executable = 'chia'
    sections = ['chia']
    InspiralAnalysisJob.__init__(self,cp,sections,executable,dax)


#############################################################################


class InspiralAnalysisNode(pipeline.CondorDAGNode, pipeline.AnalysisNode):
  """
  An InspiralNode runs an instance of the inspiral code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_inspiral.
    """
    pipeline.CondorDAGNode.__init__(self,job)
    pipeline.AnalysisNode.__init__(self)
    try:
      self.__usertag = job.get_opts()['user-tag']
    except:
      self.__usertag = job.get_config('pipeline','user-tag')

    try:
      self.__pad_data = int(self.job().get_opts()['pad-data'])
    except: 
      self.__pad_data = None

    try:
      self.__zip_output = job.get_opts()['write-compress']
      self.__zip_output = True
    except:
      self.__zip_output = False 

  def set_pad_data(self, pad):
    """
    Set the pad data value for this node 
    """
    self.__pad_data = pad
    self.add_var_opt('pad-data', pad)

  def get_pad_data(self):
    """
    Returns the injection file
    """
    return self.__pad_data

  def set_zip_output(self,zip):
    """
    Set the zip output flag
    """
    self.__zip_output = zip

  def get_zip_output(self):
    """
    Set the zip output flag
    """
    return self.__zip_output

  def get_output(self):
    """
    Returns the file name of output from the inspiral code. This must be kept
    synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    basename = self.get_ifo() + '-' + self.job().tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.get_user_tag():
      basename += '_' + self._usertag()

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.get_zip_output():
      filename += '.gz'

    self.add_output_file(filename)

    return filename

  def get_froutput(self):
    """
    Returns the file name of output frame from the inspiral code. This
    must be kept synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.get_user_tag():
      basename += '_' + self.get_user_tag()

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.gwf'

    return filename  

  def finalize(self):
    """
    set the data_start_time and data_end_time
    """
    if self.get_pad_data():
      pipeline.AnalysisNode.set_data_start(self,self.get_start() - \
          self.get_pad_data())
      pipeline.AnalysisNode.set_data_end(self,self.get_end() + \
          self.get_pad_data())

#############################################################################

class InspInjNode(InspiralAnalysisNode):
  """
  A InspInjNode runs an instance of the inspinj generation job in a
  Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_inspinj.
    """
    InspiralAnalysisNode.__init__(self,job)

  def set_seed(self,seed):
    """
    Set the seed of the injection file by setting a --seed option to the
    node when it is executed. The seed is automatically the number of
    the injection 'round'.
    @param seed: seed of the job
    """
    self.add_var_opt('seed',seed)
    self.__seed = seed

  def set_output(self, outputName):
    """
    Set the output name of the injection file
    @param outputName: name of the injection file created
    """
    self.add_var_opt('output',outputName)
    self.__outputName = outputName


class BbhInjNode(InspiralAnalysisNode):
  """
  A BbhInjNode runs an instance of the bbhinj generation job in a 
  Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_bbhinj.
    """
    InspiralAnalysisNode.__init__(self,job)

  def set_seed(self,seed):
    """
    Set the seed of the injection file by setting a --seed option to the
    node when it is executed.
    @param seed: seed of the job
    """
    self.add_var_opt('seed',seed)
    self.__seed = seed

  def get_output(self):
    """
    Returns the file name of output from the injection generation code. This 
    must be kept synchronized with the name of the output file in bbhinj.c.
    """
    if not self.get_start() or not self.get_end():
      raise InspiralError, "Start time or end time has not been set"
    if self.get_user_tag():
      bbhinject = 'HL-INJECTIONS_' + self.get_usertag() + '-'
      bbhinject = bbhinject + str(self.get_start()) + '-'
      bbhinject = bbhinject + str(self.get_end()-self.get_start()) + '.xml'
    elif self.__seed:
      bbhinject = 'HL-INJECTIONS_' + str(self.__seed) + '-'
      bbhinject = bbhinject + str(self.get_start()) + '-'
      bbhinject = bbhinject + str(self.get_end()-self.get_start()) + '.xml'
    else:
      bbhinject = 'HL-INJECTIONS-' + str(self.get_start()) + '-'
      bbhinject = bbhinject + str(self.get_end()-self.get_start()) + '.xml'

    self.add_output_file(bbhinject)

    return bbhinject


class TmpltBankNode(InspiralAnalysisNode):
  """
  A TmpltBankNode runs an instance of the template bank generation job in a
  Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_tmpltbank.
    """
    InspiralAnalysisNode.__init__(self,job)


class RandomBankNode(InspiralAnalysisNode):
  """
  A RandomBankNode runs an instance of the random bank generation job in a
  Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_randombank.
    """
    InspiralAnalysisNode.__init__(self,job)

  def get_output(self):
    """
    Returns the file name of output from the template bank code. This must
    be kept synchronized with the name of the output file in randombank.c.
    """
    if not self.get_start() or not self.get_end():
      raise InspiralError, "Start time or end time has not been set"
    if self.get_user_tag():
      bank = 'P-TMPLTBANK_' + self.get_user_tag() + '-' 
      bank = bank + str(self.get_start())
    else:
      bank = 'P-TMPLTBANK-' + str(self.get_start())
    bank = bank + '-' + str(self.get_end() - self.get_start()) + '.xml'

    self.add_output_file(bank)

    return bank


class SplitBankNode(InspiralAnalysisNode):
  """
  A SplitBankNode runs an instance of the split template bank job in a
  Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_tmpltbank.
    """
    InspiralAnalysisNode.__init__(self,job)
    self.__bankfile = None
    self.__numbanks = None

  def set_bank(self,bank):
    self.add_var_opt('bank-file', bank)
    self.add_input_file(bank)
    self.__bankfile = bank

  def get_bank(self):
    return self.__bankfile

  def set_num_banks(self,numbanks):
    self.add_var_opt('number-of-banks',numbanks)
    self.__numbanks = int(numbanks)

  def get_num_banks(self):
    return self.__numbanks

  def get_output(self):
    """
    Returns a list of the file names of split banks. This must be kept
    synchronized with the name of the output files in splitbank.c.
    """
    if not self.get_bank() or not self.get_num_banks():
      raise InspiralError, "Bank file or number of banks has not been set"

    banks = []
    x = self.__bankfile.split('-')
    for i in range( 0, int(self.get_num_banks()) ):
      banks.append("%s-%s_%2.2d-%s-%s" % (x[0], x[1], i, x[2], x[3]))

    return banks


class InspiralNode(InspiralAnalysisNode):
  """
  An InspiralNode runs an instance of the inspiral code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_inspiral.
    """
    InspiralAnalysisNode.__init__(self,job)
    self.__injections = None

  def set_bank(self,bank):
    self.add_var_opt('bank-file', bank)
    self.add_input_file(bank)

  def set_injections(self, injections):
    """
    Set the injection file for this node
    """
    self.__injections = injections
    self.add_var_opt('injection-file', injections)
    self.add_input_file(injections)

  def get_injections(self):
    """
    Returns the injection file
    """
    return self.__injections

  def get_froutput(self):
    """
    Returns the file name of output frame from the inspiral code. This
    must be kept synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.get_user_tag():
      basename += '_' + self.get_usertag()

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.gwf'

    return filename  


class TrigToTmpltNode(InspiralAnalysisNode):
  """
  A TrigToTmpltNode runs an instance of the triggered bank generator in a
  Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of inca in trigtotmplt mode.
    """
    InspiralAnalysisNode.__init__(self,job)
    self.__input_ifo = None

  def set_input_ifo(self,ifo):
    self.add_var_opt('input-ifo', ifo)
    self.__input_ifo = ifo

  def get_input_ifo(self):
    return self.__input_ifo

  def set_output_ifo(self,ifo):
    self.add_var_opt('output-ifo', ifo)
    self.set_ifo(ifo)


class IncaNode(InspiralAnalysisNode):
  """
  An IncaNode runs an instance of the inspiral coincidence code in a Condor
  DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_inca.
    """
    InspiralAnalysisNode.__init__(self,job)
    self.__ifo_a = None
    self.__ifo_b = None

  def set_ifo_a(self, ifo):
    """
    Set the interferometer code to use as IFO A.
    ifo = IFO code (e.g. L1, H1 or H2).
    """
    self.add_var_opt('ifo-a', ifo)
    self.__ifo_a = ifo

  def get_ifo_a(self):
    """
    Returns the IFO code of the primary interferometer.
    """
    return self.__ifo_a

  def set_ifo_b(self, ifo):
    """
    Set the interferometer code to use as IFO B.
    ifo = IFO code (e.g. L1, H1 or H2).
    """
    self.add_var_opt('ifo-b', ifo)
    self.__ifo_b = ifo

  def get_ifo_b(self):
    """
    Returns the IFO code of the primary interferometer.
    """
    return self.__ifo_b

  def get_output_a(self):
    """
    Returns the file name of output from inca for ifo a. This must be kept
    synchronized with the name of the output file in inca.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo_a():
      raise InspiralError, "Start time, end time or ifo a has not been set"

    basename = self.get_ifo_a() + '-INCA'

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.get_user_tag():
      basename += '_' + self.get_usertag() 

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.get_zip_output():
      filename += '.gz'

    self.add_output_file(filename)
    return filename

  def get_output(self):
    return self.get_output_a()

  def get_output_b(self):
    """
    Returns the file name of output from inca for ifo b. This must be kept
    synchronized with the name of the output file in inca.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo_b():
      raise InspiralError, "Start time, end time or ifo a has not been set"

    basename = self.get_ifo_b() + '-INCA'

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.get_user_tag():
      basename += '_' + self.get_usertag()

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.get_zip_output():
      filename += '.gz'

    self.add_output_file(filename)
    return filename


class ThincaNode(InspiralAnalysisNode):
  """
  A ThincaNode runs an instance of the inspiral coincidence code in a Condor
  DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_inca.
    """
    InspiralAnalysisNode.__init__(self,job)
    self.__ifo_g1 = None
    self.__ifo_h1 = None
    self.__ifo_h2 = None
    self.__ifo_l1 = None
    self.__ifo_t1 = None
    self.__ifo_v1 = None
    self.__num_slides = None

  def set_ifo(self, ifo):
    """
    Add the interferometer to the list of ifos
    ifo = IFO code (e.g. G1,L1, H1 or H2).
    """
    if ifo == 'G1':
      self.add_var_opt('g1-triggers','')
      self.__ifo_g1 = 'G1'
    elif ifo == 'H1':
      self.add_var_opt('h1-triggers','')
      self.__ifo_h1 = 'H1'
    elif ifo == 'H2':
      self.add_var_opt('h2-triggers','')
      self.__ifo_h2 = 'H2'
    elif ifo == 'L1':
      self.add_var_opt('l1-triggers','')
      self.__ifo_l1 = 'L1'
    elif ifo == 'T1':
      self.add_var_opt('t1-triggers','')
      self.__ifo_t1 = 'T1'
    elif ifo == 'V1':
      self.add_var_opt('v1-triggers','')
      self.__ifo_v1 = 'V1'
  
  def get_ifo_g1(self):
    """
    Returns the IFO code of g1.
    """
    return self.__ifo_g1
    
  def get_ifo_h1(self):
    """
    Returns the IFO code of h1.
    """
    return self.__ifo_h1

  def get_ifo_h2(self):
    """
    Returns the IFO code of h2.
    """
    return self.__ifo_h2

  def get_ifo_l1(self):
    """
    Returns the IFO code of l1.
    """
    return self.__ifo_l1

  def get_ifo_t1(self):
    """
    Returns the IFO code of t1.
    """
    return self.__ifo_t1

  def get_ifo_v1(self):
    """
    Returns the IFO code of v1.
    """
    return self.__ifo_v1

  def get_ifos(self):
    """
    Returns the ordered list of ifos.
    """
    ifos = ''
    if self.get_ifo_g1():
      ifos += self.get_ifo_g1()
    if self.get_ifo_h1():
      ifos += self.get_ifo_h1()
    if self.get_ifo_h2():
      ifos += self.get_ifo_h2()
    if self.get_ifo_l1():
      ifos += self.get_ifo_l1()
    if self.get_ifo_t1():
      ifos += self.get_ifo_t1()
    if self.get_ifo_v1():
      ifos += self.get_ifo_v1()

    return ifos

  def set_num_slides(self, num_slides):
    """
    Set number of time slides to undertake
    """
    self.add_var_opt('num-slides',num_slides)
    self.__num_slides = num_slides

  def get_num_slides(self):
    """
    Returns the num_slides from .ini (>0 => time slides desired)
    """
    return self.__num_slides

  def get_output(self):
    """
    Returns the file name of output from thinca.  This must be kept
    synchronized with the name of the output file in thinca.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifos():
      raise InspiralError, "Start time, end time or ifos have not been set"
    
    tag_base = self.job().tag_base
    if self.__num_slides:
      basename = self.get_ifos() + '-' + tag_base + '_SLIDE'
    else:
      basename = self.get_ifos() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag() 

    if self.get_user_tag():
      basename += '_' + self.get_user_tag()

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.get_zip_output():
      filename += '.gz'

    self.add_output_file(filename)
    return filename


class SireNode(InspiralAnalysisNode):
  """
  A SireNode runs an instance of the single inspiral reader code in a Condor
  DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_sire.
    """
    InspiralAnalysisNode.__init__(self,job)
    self.__injection_file = None
    self.__ifo_tag = None

  def set_ifo(self, ifo):
    """
    Add the list of interferometers 
    """
    self.__ifo = ifo
    self.add_var_opt('ifo-cut',ifo)

  def get_ifo(self):
    """
    Returns the two letter IFO code for this node.
    """
    return self.__ifo

  def set_inj_file(self, file):
    """
    Sets the injection file
    """
    self.__injection_file = file
    self.add_var_opt('injection-file', file)

  def get_inj_file(self):
    """
    Gets the injection file
    """
    return self.__injection_file

  def set_start(self, start):
    """
    Sets GPS start time
    """
    self.__start = start

  def get_start(self):
    """
    Gets GPS start time
    """
    return self.__start

  def set_end(self, end):
    """
    Sets GPS end time
    """
    self.__end = end

  def get_end(self):
    """
    Gets GPS end time
    """
    return self.__end
  
  def set_ifo_tag(self,ifo_tag):
    """
    Set the ifo tag that is passed to the analysis code.
    @param ifo_tag: a string to identify one or more IFOs
    """
    self.__ifo_tag = ifo_tag

  def get_ifo_tag(self):
    """
    Returns the IFO tag string
    """
    return self.__ifo_tag

  def set_glob(self, file_glob):
    """
    Sets the glob name
    """
    self.add_var_opt('glob',file_glob)

  def set_input(self, input_file):
    """
    Sets the input file name
    """
    self.add_var_opt('input',input_file)

  def get_output(self):
    """
    get the name of the output file
    """
    if not self.get_ifo():
      raise InspiralError, "ifos have not been set"

    fname = self.get_ifo() + "-SIRE"
    if self.get_inj_file():
      fname += "_" + self.get_inj_file().split("-")[1]
      fname += "_FOUND"

    if self.get_ifo_tag(): fname += "_" + self.get_ifo_tag()
    if self.get_user_tag(): fname += "_" + self.get_user_tag()

    if (self.get_start() and not self.get_end()) or \
        (self.get_end() and not self.get_start()):
      raise InspiralError, "If one of start and end is set, both must be"

    if (self.get_start()):
      duration=self.get_end()- self.get_start()
      fname += "-" + str(self.get_start()) + "-" + str(duration)

    fname += ".xml"

    return fname

  def get_missed(self):
    """
    get the name of the missed file
    """
    if self.get_inj_file():
      return self.get_output().replace("FOUND", "MISSED")
    else:
      return None

  def finalize(self):
    """
    set the output options
    """
    output = self.get_output()
 
    self.add_var_opt("output", output)
    self.add_var_opt("summary", output.replace("xml", "txt"))

    if self.get_inj_file():
      self.add_var_opt('injection-file', self.get_inj_file())
      self.add_var_opt('missed-injections', self.get_missed() )


class CoireNode(InspiralAnalysisNode):
  """
  A CoireNode runs an instance of the inspiral coire code in a Condor
  DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_coire.
    """
    InspiralAnalysisNode.__init__(self,job)
    self.__ifos  = None
    self.__ifo_tag = None
    self.__num_slides = None
    self.__injection_file = None
    self.__output_tag = None

  def set_ifos(self, ifos):
    """
    Add the list of interferometers 
    """
    self.__ifos = ifos
    self.add_var_opt('coinc-cut',ifos)

  def get_ifos(self):
    """
    Returns the ifos
    """
    return self.__ifos

  def set_slides(self, slides):
    """
    Add the number of time slides
    """
    self.__num_slides = slides 
    self.add_var_opt('num-slides',slides)

  def get_slides(self):
    """
    Returns the number of slides
    """
    return self.__num_slides

  def set_inj_file(self, file):
    """
    Sets the injection file
    """
    if file:
      self.__injection_file = file
      self.add_var_opt('injection-file', file)

  def get_inj_file(self):
    """
    Gets the injection file
    """
    return self.__injection_file

  def set_start(self, start):
    """
    Sets GPS start time
    """
    self.__start = start

  def get_start(self):
    """
    Gets GPS start time
    """
    return self.__start

  def set_end(self, end):
    """
    Sets GPS end time
    """
    self.__end = end

  def get_end(self):
    """
    Gets GPS end time
    """
    return self.__end

  def set_ifo_tag(self,ifo_tag):
    """
    Set the ifo tag that is passed to the analysis code.
    @param ifo_tag: a string to identify one or more IFOs
    """
    self.__ifo_tag = ifo_tag

  def get_ifo_tag(self):
    """
    Returns the IFO tag string
    """
    return self.__ifo_tag

  def set_glob(self, file_glob):
    """
    Sets the glob name
    """
    self.add_var_opt('glob',file_glob)

  def set_input(self, input_file):
    """
    Sets the input file name
    """
    self.add_var_opt('input',input_file)

  def set_output_tag(self):
    fname = "COIRE"
    if self.get_slides(): fname += "_SLIDE"
    if self.get_inj_file():
      fname += "_" + self.get_inj_file().split("-")[1]
      fname += "_FOUND"
    if self.get_ifo_tag(): fname += "_" + self.get_ifo_tag()
    if self.get_user_tag(): fname += "_" + self.get_user_tag()
    self.__output_tag = fname

  def get_output_tag(self):
    return self.__output_tag

  def get_output(self):
    """
    get the name of the output file
    """
    if not self.get_ifos():
      raise InspiralError, "ifos have not been set"

    self.set_output_tag()
    fname = self.get_ifos() + '-' + self.get_output_tag()

    if (self.get_start() and not self.get_end()) or \
           (self.get_end() and not self.get_start()):
      raise InspiralError, "If one of start and end is set, "\
            "both must be"

    if (self.get_start()):
      duration=self.get_end() - self.get_start()
      fname += "-" + str(self.get_start()) + "-" + str(duration)

    fname += ".xml"

    return fname

  def get_missed(self):
    """
    get the name of the missed file
    """
    if self.get_inj_file():
      return self.get_output().replace("FOUND", "MISSED")
    else:
      return None

  def finalize(self):
    """
    set the output options
    """
    output = self.get_output()
 
    self.add_var_opt("output", output)
    self.add_var_opt("summary", output.replace("xml", "txt"))

    if self.get_inj_file():
      self.add_var_opt('injection-file', self.get_inj_file())
      self.add_var_opt('missed-injections', self.get_missed() )


class FrJoinNode(InspiralAnalysisNode):
  """
  A FrJoinNode runs an instance of lalapps_frjoin in a Condor DAG
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_frjoin.
    """
    InspiralAnalysisNode.__init__(self,job)

  def set_output(self, outputName):
    """
    Set the output name of the frame file
    @param outputName: name of the injection file created
    """
    self.add_var_opt('output',outputName)
    self.__outputName = outputName
    
  def get_output(self):
    """
    Get the output name of the frame file
    """
    return self.__outputName


class CohBankNode(InspiralAnalysisNode):
  """
  A CohBankNode runs an instance of the coherent code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_coherent_inspiral.
    """
    InspiralAnalysisNode.__init__(self,job)
    self.__bank = None
    self.__ifos = None
    
  def set_bank(self,bank):
    self.add_var_opt('bank-file', bank)
    self.add_input_file(bank)
    self.__bank = bank

  def get_bank(self):
    return self.__bank

  def set_ifos(self,ifos):
    self.add_var_opt('ifos', ifos)
    self.__ifos = ifos
   
  def get_ifos(self):
    return self.__ifos
    
  def get_output(self):
    """
    Returns the file name of output from the coherent bank. 
    """
    
    if not self.get_ifos():
      raise InspiralError, "Ifos have not been set"
    
    basename = self.get_ifos() + '-COHBANK'

    if self.get_user_tag():
      basename += '_' + self.get_user_tag()

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.get_zip_output():
      filename += '.gz'

    self.add_output_file(filename)

    return filename    


class ChiaNode(InspiralAnalysisNode):
  """
  A ChiaNode runs an instance of the coherent_inspiral code in a Condor
  DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of lalapps_coherent_inspiral.
    """
    InspiralAnalysisNode.__init__(self,job)

  def set_bank(self,bank):
    self.add_var_opt('bank-file', bank)
    self.add_input_file(bank)

    
##############################################################################
# Plotting Jobs and Nodes

class PlotInspiralJob(pipeline.CondorDAGJob, pipeline.AnalysisJob):
  """
  A plotinspiral job. The static options are read from the section
  [plotinspiral] in the ini file.  The stdout and stderr from the job
  are directed to the logs directory.  The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='PLOTINSPIRAL'):
    """
    cp = ConfigParser object from which options are read.
    """
    self.__executable = cp.get('condor','plotinspiral')
    self.__universe = cp.get('condor','universe')
    pipeline.CondorDAGJob.__init__(self,self.__universe,self.__executable)
    pipeline.AnalysisJob.__init__(self,cp,False)
    self.tag_base = tag_base
    
    self.add_ini_opts(cp, 'plotinspiral')

    self.set_stdout_file('logs/plotinspiral-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/plotinspiral-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).err')
    self.set_sub_file('plotinspiral.sub')

    self.add_condor_cmd('getenv','True')

class PlotInspiralNode(pipeline.CondorDAGNode, pipeline.AnalysisNode):
  """
  A PlotInspiralNode runs an instance of the plotinspiral code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of plotinspiral.
    """
    pipeline.CondorDAGNode.__init__(self,job)
    pipeline.AnalysisNode.__init__(self)
    self.__usertag = job.get_config('pipeline','user-tag')

  def set_ifo(self, ifo):
    self.add_var_opt("ifo-type", ifo)


  def set_user_tag(self,usertag):
    self.__usertag = usertag
    self.add_var_opt('user-tag',usertag)

  def get_user_tag(self):
    return self.__usertag

  def get_output(self):
    """
    Returns the file name of output from the inspiral code. This must be kept
    synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.__usertag:
      basename += '_' + self.__usertag

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.__zip_output:
      filename += '.gz'

    self.add_output_file(filename)

    return filename

###########################################################################################

class PlotThincaJob(pipeline.CondorDAGJob, pipeline.AnalysisJob):
  """
  A plotthinca job. The static options are read from the section
  [plotthinca] in the ini file.  The stdout and stderr from the job
  are directed to the logs directory.  The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='PLOTTHINCA'):
    """
    cp = ConfigParser object from which options are read.
    """
    self.__executable = cp.get('condor','plotthinca')
    self.__universe = cp.get('condor','universe')
    pipeline.CondorDAGJob.__init__(self,self.__universe,self.__executable)
    pipeline.AnalysisJob.__init__(self,cp,False)
    self.tag_base = tag_base

    for sec in ['plotthinca']:
      self.add_ini_opts(cp,sec)

    self.set_stdout_file('logs/plotthinca-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/plotthinca-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).err')
    self.set_sub_file('plotthinca.sub')

    self.add_condor_cmd('getenv','True')

class PlotThincaNode(pipeline.CondorDAGNode, pipeline.AnalysisNode):
  """
  A PlotThincaNode runs an instance of the plotthinca code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of plotthinca.
    """
    pipeline.CondorDAGNode.__init__(self,job)
    pipeline.AnalysisNode.__init__(self)
    self.__usertag = job.get_config('pipeline','user-tag')

  def set_user_tag(self,usertag):
    self.__usertag = usertag
    self.add_var_opt('user-tag',usertag)

  def get_user_tag(self):
    return self.__usertag

  def get_output(self):
    """
    Returns the file name of output from the inspiral code. This must be kept
    synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.__usertag:
      basename += '_' + self.__usertag

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.__zip_output:
      filename += '.gz'

    self.add_output_file(filename)

    return filename

#######################################################################################

class PlotNumtemplatesJob(pipeline.CondorDAGJob, pipeline.AnalysisJob):
  """
  A plotnumtemplates job. The static options are read from the section
  [plotnumtemplates] in the ini file.  The stdout and stderr from the job
  are directed to the logs directory.  The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='PLOTNUMTEMPLATES'):
    """
    cp = ConfigParser object from which options are read.
    """
    self.__executable = cp.get('condor','plotnumtemplates')
    self.__universe = cp.get('condor','universe')
    pipeline.CondorDAGJob.__init__(self,self.__universe,self.__executable)
    pipeline.AnalysisJob.__init__(self,cp,False)
    self.tag_base = tag_base

    for sec in ['plotnumtemplates']:
      self.add_ini_opts(cp,sec)

    self.set_stdout_file('logs/plotnumtemplates-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/plotnumtemplates-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).err')
    self.set_sub_file('plotnumtemplates.sub')

    self.add_condor_cmd('getenv','True')

class PlotNumtemplatesNode(pipeline.CondorDAGNode, pipeline.AnalysisNode):
  """
  A PlotNumtemplatesNode runs an instance of the plotinspiral code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of plotnumtemplates.
    """
    pipeline.CondorDAGNode.__init__(self,job)
    pipeline.AnalysisNode.__init__(self)
    self.__usertag = job.get_config('pipeline','user-tag')

  def set_user_tag(self,usertag):
    self.__usertag = usertag
    self.add_var_opt('user-tag',usertag)

  def get_user_tag(self):
    return self.__usertag

  def get_output(self):
    """
    Returns the file name of output from the inspiral code. This must be kept
    synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.__usertag:
      basename += '_' + self.__usertag

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.__zip_output:
      filename += '.gz'
    
    self.add_output_file(filename)

    return filename

##############################################################################

class PlotInjnumJob(pipeline.CondorDAGJob, pipeline.AnalysisJob):
  """
  A plotinjnum job. The static options are read from the section
  [plotinjnum] in the ini file.  The stdout and stderr from the job
  are directed to the logs directory.  The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='PLOTINJNUM'):
    """
    cp = ConfigParser object from which options are read.
    """
    self.__executable = cp.get('condor','plotinjnum')
    self.__universe = cp.get('condor','universe')
    pipeline.CondorDAGJob.__init__(self,self.__universe,self.__executable)
    pipeline.AnalysisJob.__init__(self,cp,False)
    self.tag_base = tag_base

    for sec in ['plotinjnum']:
      self.add_ini_opts(cp,sec)

    self.set_stdout_file('logs/plotinjnum-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/plotinjnum-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).err')
    self.set_sub_file('plotinjnum.sub')

    self.add_condor_cmd('getenv','True')

class PlotInjnumNode(pipeline.CondorDAGNode, pipeline.AnalysisNode):
  """
  A PlotInjnumNode runs an instance of the plotinspiral code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of plotinjnum.
    """
    pipeline.CondorDAGNode.__init__(self,job)
    pipeline.AnalysisNode.__init__(self)
    self.__usertag = job.get_config('pipeline','user-tag')

  def set_user_tag(self,usertag):
    self.__usertag = usertag
    self.add_var_opt('user-tag',usertag)

  def get_user_tag(self):
    return self.__usertag

  def get_output(self):
    """
    Returns the file name of output from the inspiral code. This must be kept
    synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.__usertag:
      basename += '_' + self.__usertag

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.__zip_output:
      filename += '.gz'

    self.add_output_file(filename)

    return filename

#############################################################################

class PlotEthincaJob(pipeline.CondorDAGJob, pipeline.AnalysisJob):
  """
  A plotethinca job. The static options are read from the section
  [plotethinca] in the ini file.  The stdout and stderr from the job
  are directed to the logs directory.  The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='PLOTETHINCA'):
    """
    cp = ConfigParser object from which options are read.
    """
    self.__executable = cp.get('condor','plotethinca')
    self.__universe = cp.get('condor','universe')
    pipeline.CondorDAGJob.__init__(self,self.__universe,self.__executable)
    pipeline.AnalysisJob.__init__(self,cp,False)
    self.tag_base = tag_base

    for sec in ['plotethinca']:
      self.add_ini_opts(cp,sec)

    self.set_stdout_file('logs/plotethinca-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/plotethinca-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).err')
    self.set_sub_file('plotethinca.sub')

    self.add_condor_cmd('getenv','True')

class PlotEthincaNode(pipeline.CondorDAGNode, pipeline.AnalysisNode):
  """
  A PlotEthincaNode runs an instance of the plotinspiral code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of plotinjnum.
    """
    pipeline.CondorDAGNode.__init__(self,job)
    pipeline.AnalysisNode.__init__(self)
    self.__usertag = job.get_config('pipeline','user-tag')

  def set_user_tag(self,usertag):
    self.__usertag = usertag
    self.add_var_opt('user-tag',usertag)

  def get_user_tag(self):
    return self.__usertag

  def get_output(self):
    """
    Returns the file name of output from the inspiral code. This must be kept
    synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.__usertag:
      basename += '_' + self.__usertag

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.__zip_output:
      filename += '.gz'
 
    self.add_output_file(filename)

    return filename

#############################################################################

class PlotInspmissedJob(pipeline.CondorDAGJob, pipeline.AnalysisJob):
  """
  A plotinspmissed job. The static options are read from the section
  [plotinspmissed] in the ini file.  The stdout and stderr from the job
  are directed to the logs directory.  The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='PLOTINSPMISSED'):
    """
    cp = ConfigParser object from which options are read.
    """
    self.__executable = cp.get('condor','plotinspmissed')
    self.__universe = cp.get('condor','universe')
    pipeline.CondorDAGJob.__init__(self,self.__universe,self.__executable)
    pipeline.AnalysisJob.__init__(self,cp,False)
    self.tag_base = tag_base

    for sec in ['plotinspmissed']:
      self.add_ini_opts(cp,sec)

    self.set_stdout_file('logs/plotinspmissed-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/plotinspmissed-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).err')
    self.set_sub_file('plotinspmissed.sub')

    self.add_condor_cmd('getenv','True')


class PlotInspmissedNode(pipeline.CondorDAGNode, pipeline.AnalysisNode):
  """
  A PlotInspmissedNode runs an instance of the plotinspiral code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of plotinspmissed.
    """
    pipeline.CondorDAGNode.__init__(self,job)
    pipeline.AnalysisNode.__init__(self)
    self.__usertag = job.get_config('pipeline','user-tag')

  def set_user_tag(self,usertag):
    self.__usertag = usertag
    self.add_var_opt('user-tag',usertag)

  def get_user_tag(self):
    return self.__usertag

  def get_output(self):
    """
    Returns the file name of output from the inspiral code. This must be kept
    synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.__usertag:
      basename += '_' + self.__usertag

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.__zip_output:
      filename += '.gz'

    self.add_output_file(filename)

    return filename

#############################################################################

class PlotInspinjJob(pipeline.CondorDAGJob, pipeline.AnalysisJob):
  """
  A plotinspinj job. The static options are read from the section
  [plotinspinj] in the ini file.  The stdout and stderr from the job
  are directed to the logs directory.  The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='PLOTINSPINJ'):
    """
    cp = ConfigParser object from which options are read.
    """
    self.__executable = cp.get('condor','plotinspinj')
    self.__universe = cp.get('condor','universe')
    pipeline.CondorDAGJob.__init__(self,self.__universe,self.__executable)
    pipeline.AnalysisJob.__init__(self,cp,False)
    self.tag_base = tag_base

    for sec in ['plotinspinj']:
      self.add_ini_opts(cp,sec)

    self.set_stdout_file('logs/plotinspinj-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/plotinspinj-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).err')
    self.set_sub_file('plotinspinj.sub')

    self.add_condor_cmd('getenv','True')

class PlotInspinjNode(pipeline.CondorDAGNode, pipeline.AnalysisNode):
  """
  A PlotInspinjNode runs an instance of the plotinspiral code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of plotinspinj.
    """
    pipeline.CondorDAGNode.__init__(self,job)
    pipeline.AnalysisNode.__init__(self)
    self.__usertag = job.get_config('pipeline','user-tag')

  def set_user_tag(self,usertag):
    self.__usertag = usertag
    self.add_var_opt('user-tag',usertag)

  def get_user_tag(self):
    return self.__usertag

  def get_output(self):
    """
    Returns the file name of output from the inspiral code. This must be kept
    synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.__usertag:
      basename += '_' + self.__usertag

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.__zip_output:
      filename += '.gz'

    self.add_output_file(filename)

    return filename

#############################################################################

class PlotSnrchiJob(pipeline.CondorDAGJob, pipeline.AnalysisJob):
  """
  A plotsnrchi job. The static options are read from the section
  [plotsnrchi] in the ini file.  The stdout and stderr from the job
  are directed to the logs directory.  The path to the executable is
  determined from the ini file.
  """
  def __init__(self,cp,dax=False,tag_base='PLOTSNRCHI'):
    """
    cp = ConfigParser object from which options are read.
    """
    self.__executable = cp.get('condor','plotsnrchi')
    self.__universe = cp.get('condor','universe')
    pipeline.CondorDAGJob.__init__(self,self.__universe,self.__executable)
    pipeline.AnalysisJob.__init__(self,cp,False)
    self.tag_base = tag_base
    
    
    for sec in ['plotsnrchi']:
      if cp.has_section('figure_name'):
         cp.set('figure_name' + tag_base)
      else:
         self.add_ini_opts(cp,sec)

    self.set_stdout_file('logs/plotsnrchi-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).out')
    self.set_stderr_file('logs/plotsnrchi-$(macrogpsstarttime)-$(macrogpsendtime)-$(cluster)-$(process).err')
    self.set_sub_file('plotsnrchi.sub')

    self.add_condor_cmd('getenv','True')

class PlotSnrchiNode(pipeline.CondorDAGNode, pipeline.AnalysisNode):
  """
  A PlotSnrchiNode runs an instance of the plotinspiral code in a Condor DAG.
  """
  def __init__(self,job):
    """
    job = A CondorDAGJob that can run an instance of plotsnrchi.
    """
    pipeline.CondorDAGNode.__init__(self,job)
    pipeline.AnalysisNode.__init__(self)
    self.__usertag = job.get_config('pipeline','user-tag')

  def set_user_tag(self,usertag):
    self.__usertag = usertag
    self.add_var_opt('user-tag',usertag)

  def get_user_tag(self):
    return self.__usertag

  def get_output(self):
    """
    Returns the file name of output from the inspiral code. This must be kept
    synchronized with the name of the output file in inspiral.c.
    """
    if not self.get_start() or not self.get_end() or not self.get_ifo():
      raise InspiralError, "Start time, end time or ifo has not been set"

    tag_base = self.job().tag_base
    basename = self.get_ifo() + '-' + tag_base

    if self.get_ifo_tag():
      basename += '_' + self.get_ifo_tag()
    if self.__usertag:
      basename += '_' + self.__usertag

    filename = basename + '-' + str(self.get_start()) + '-' + \
      str(self.get_end() - self.get_start()) + '.xml'

    if self.__zip_output:
      filename += '.gz'

    self.add_output_file(filename)

    return filename


##############################################################################
# some functions to make life easier later

def overlap_test(interval1, interval2, slide_sec=0):
  """
  Test whether the two intervals could possibly overlap with one of them being
  slid by a maximum time of slide_sec.  Perform three tests:
  1)  Does the start of interval 1 lie within interval 2's range (with the 
    start decremented by slide_sec and the end incremented by slide_sec)
  2)  Does the end of interval 1 lie within interval 2's range (with the start 
    decremented by slide_sec and the end incremented by slide_sec)
  3)  Does interval 1 completely cover (the extended) interval 2, 
    ie is interval_1 start before (interval 2 start - slide_sec) AND 
    interval 1 end after (interval 2 end + slide_sec)
  If any of the above conditions are satisfied then return True, else False.
  """
  start1 = interval1.start()
  end1 = interval1.end()
  left = interval2.start() - slide_sec
  right = interval2.end() + slide_sec
  
  return (start1 >= left and start1 <= right) or \
         (end1 >= left and end1 <= right) or \
         (start1 <= left and end1 >= right)

