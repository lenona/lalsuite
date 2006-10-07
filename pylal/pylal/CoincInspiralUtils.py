import sys
from glue.ligolw import ligolw
from glue.ligolw import table
from glue.ligolw import lsctables
from glue.ligolw import utils

def uniq(list):
  """
  return a list containing the unique elements 
  from the original list
  """
  l = []
  for m in list:
    if m not in l:
      l.append(m)
  from numarray import asarray
  return asarray(l)


########################################
class coincStatistic:
  """
  This class specifies the statistic to be used when dealing with coincident events.
  It also contains parameter for such cases as the BBH bitten-L statistics.
  """

  __slots__ = ["name","a","b","rsq","bl"]

  def __init__(self, name, a=0, b=0):
    self.name=name
    self.a=a
    self.b=b
    self.rsq=0
    self.bl=0

  def get_bittenl(self, bl, snr ):
    blx=self.a*snr-self.b
    if bl==0:    
      return blx
    else:
      return min(bl, blx)  
    
    
#######################################
class coincInspiralTable:
  """
  Table to hold coincident inspiral triggers.  Coincidences are reconstructed 
  by making use of the event_id contained in the sngl_inspiral table.
  The coinc is a dictionary with entries: G1, H1, H2, L1, event_id, numifos, 
  stat.  
  The stat is set by default to the snrsq: the sum of the squares of the snrs 
  of the individual triggers.
  """
  class row(object):
    __slots__ = ["event_id", "numifos","stat","G1","H1","H2",\
                 "L1","T1","V1","sim","rsq","bl"]
    
    def __init__(self, event_id, numifos = 0, stat = 0 ):
      self.event_id = event_id
      self.numifos = numifos
      self.stat = stat
      self.rsq=0
      self.bl=0
      
    def add_trig(self,trig,statistic):
      
      self.numifos +=1
      if statistic.name == 'effective_snr':
        self.stat = (self.stat**2 + trig.get_effective_snr()**2)**(1./2)      
      elif statistic.name == 'bitten_l':
        snr=trig.snr
        self.rsq= (self.stat**2 + snr**2)**(1./2)
        self.bl=statistic.get_bittenl( self.bl, snr )
        self.stat=min( self.bl, self.rsq )
      else:
        self.stat = (self.stat**2 + getattr(trig,statistic.name)**2)**(1./2)
      
      # sets the data for the single inspiral trigger
      setattr(self,trig.ifo,trig)
      

    def add_sim(self,sim):
      setattr(self,"sim",sim)

  
  def __init__(self, inspTriggers = None, stat = None):
    """
    @param inspTriggers: a metaDataTable containing inspiral triggers 
                         from which to construct coincidences
    @param stat:         an instance of coincStatistic
    """
    self.stat = stat
    self.sngl_table = inspTriggers
    self.sim_table = None
    self.rows = []
    if not inspTriggers:
      return

    # use the supplied method to convert these columns into numarrays
    eventidlist = uniq(inspTriggers.get_column("event_id"))
    for event_id in eventidlist: 
      self.rows.append(self.row(event_id))
    for trig in inspTriggers:
      for coinc in self.rows:
        if coinc.event_id == trig.event_id:
          coinc.add_trig(trig,stat)

    # make sure that there are at least twos ifo in each coinc
    pruned_coincs = coincInspiralTable()
    for coinc in self.rows:
      if coinc.numifos > 1:
        pruned_coincs.rows.append(coinc)

    self.rows = pruned_coincs.rows

  def __len__(self):
    return len(self.rows)
  
  def append(self,row):
    self.rows.append(row)

  def extend(self,rows):
    self.rows.extend(rows)

  def __getitem__(self, i):
    """
    Retrieve the value in this column in row i.
    """
    return self.rows[i]

  def getstat(self):
    stat = []
    for coinc in self.rows:
      stat.append(coinc.stat)
    from numarray import asarray
    return asarray(stat)

  def sort(self):
    """
    Sort the list based on stat value
    """
    stat_list = [ (coinc.stat, coinc) for coinc in self.rows ]
    stat_list.sort()
    stat_list.reverse()
    self.rows = [coinc for (stat,coinc) in stat_list]
    
  def getslide(self, slide_num):
    """
    Return the triggers with a specific slide number.
    @param slide_num: the slide number to recover (contained in the event_id)
    """
    slide_coincs = coincInspiralTable(stat=self.stat)
    slide_coincs.sngl_table = self.sngl_table
    if slide_num < 0:
      slide_num = 5000 - slide_num
    for coinc in self.rows:
      if ( (coinc.event_id % 1000000000) / 100000 ) == slide_num:
        slide_coincs.rows.append(coinc)
     
    return slide_coincs 

  def coincinclude(self, ifolist):
    """
    Return the coincs which have triggers from the ifos in ifolist.
    @param ifolist: a list of ifos 
    """
    selected_coincs = coincInspiralTable(stat=self.stat)
    selected_coincs.sngl_table = self.sngl_table
    for coinc in self:
      keep_trig = True
      for ifo in ifolist:
        if hasattr(coinc,ifo) == False:
          keep_trig = False
          break
            
      if keep_trig == True:
        selected_coincs.append(coinc)
        
    return selected_coincs

  def coinctype(self, ifolist):
    """
    Return the coincs which are from ifos.
    @param ifos: a list of ifos 
    """
    coincs = self.coincinclude(ifolist)
    selected_coincs = coincInspiralTable()
    selected_coincs.sngl_table = self.sngl_table
    for coinc in coincs:
      if coinc.numifos == len(ifolist):
        selected_coincs.append(coinc)
        
    return selected_coincs

    
  def getsngls(self, ifo):
    """
    Return the sngls for a specific ifo.
    @param ifo: ifo for which to retrieve the single inspirals.
    """
    from glue.ligolw import table 
    try: ifoTrigs = table.new_from_template(self.sngl_table)
    except: ifoTrigs = lsctables.New(lsctables.SnglInspiralTable)
    for coinc in self:
      if hasattr(coinc,ifo): 
        ifoTrigs.append(getattr(coinc,ifo))
        
    return ifoTrigs


  def cluster(self, cluster_window):
    """
    Return the clustered triggers, returning the one with the largest stat in 
    each fixed cluster_window
    
    @param cluster_window: length of time over which to cluster (seconds)
    """
    ifolist = ['G1','H1','H2','L1','T1','V1']
    # find times when there is a trigger
    cluster_times = []
    for coinc in self:
      for ifo in ifolist:
        if hasattr(coinc,ifo):
          end_time = getattr(coinc,ifo).end_time
          break
      cluster_times.append(cluster_window * (end_time/cluster_window) )
    cluster_times = uniq(cluster_times)
    
    cluster_triggers = coincInspiralTable(stat = self.stat)
    cluster_triggers.sngl_table = self.sngl_table
    for cluster_time in cluster_times:
      # find all triggers at that time
      cluster = coincInspiralTable()
      for coinc in self:
        for ifo in ifolist:
          if hasattr(coinc,ifo):
            end_time = getattr(coinc,ifo).end_time
            break
        if ((end_time - cluster_time) / cluster_window == 0):   
          cluster.append(coinc)

      # find loudest trigger in time and append
      loudest_stat = 0
      for trigger in cluster:
        if trigger.stat > loudest_stat:
          loudest_trig = trigger
          loudest_stat = trigger.stat

      cluster_triggers.append(loudest_trig)
      
    return cluster_triggers 
  
  def add_sim_inspirals(self,sim_inspiral):
    """
    FIXME: We should really store the sim coincidence info in the event_id
    Method to add simulated injections to a list of coincs

    @param sim_inspiral: a simInspiralTable
    """
    self.sim_table = sim_inspiral
    # check that the number of sims matches the number of coincs:
    if len(self) != len(sim_inspiral):
      print >> sys.stderr, "Number of injections doesn't match number of coincs"
      sys.exit(1)

    for i in range(len(self)):
      self[i].add_sim(sim_inspiral[i])


  def add_missed_sims(self,sim_inspiral):
    """
    Add missed sim inspirals to the list of coincs, set the stat = -1
    @param sim_inspiral: a simInspiralTable
    """
    for sim in sim_inspiral:
      row = coincInspiralTable.row(-1)
      row.add_sim(sim)
      self.append(row)

  def return_sim_inspirals(self,thresh = 0):
    """
    Method to return the sim_inspiral table associated to the coincs.
    If thresh is specified, only return sims from those coincs whose stat
    exceeds thresh.

    @param thresh: the threshold on the statistic
    """
    from glue.ligolw import table 
    simInspirals = table.new_from_template(self.sim_table)
    try: simInspirals = table.new_from_template(sim.sngl_table)
    except: simInspirals = lsctables.New(lsctables.SimInspiralTable)
    for coinc in self:
      if (hasattr(coinc,"sim")) and (coinc.stat >= thresh): 
        simInspirals.append(coinc.sim)
    
    return simInspirals
    
