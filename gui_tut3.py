from netpyne import specs, sim
import sys; reload(sys)

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.sizeX = 100 # x-dimension (horizontal length) size in um
netParams.sizeY = 500 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 100 # z-dimension (horizontal length) size in um
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLengthConst = 150.0 # length constant for conn probability (um)

## Population parameters
netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 10, 'yRange': [50,150], 'cellModel': 'HH'}
netParams.popParams['I2'] = {'cellType': 'I', 'numCells': 10, 'yRange': [50,150], 'cellModel': 'HH'}
netParams.popParams['E4'] = {'cellType': 'E', 'numCells': 10, 'yRange': [150,300], 'cellModel': 'HH'}
netParams.popParams['I4'] = {'cellType': 'I', 'numCells': 10, 'yRange': [150,300], 'cellModel': 'HH'}
netParams.popParams['E5'] = {'cellType': 'E', 'numCells': 10, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}
netParams.popParams['I5'] = {'cellType': 'I', 'numCells': 10, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}

## Cell property rules
netParams.loadCellParamsRule(label='CellRule', fileName='cells/IT2_reduced_rxd_cellParams.json')
netParams.cellParams['CellRule']['conds'] = {'cellType': ['E','I']}

## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 40, 'noise': 0.3}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'weight': 8.0, 'sec': 'soma', 'delay': 'max(1, normal(5,2))', 'synMech': 'exc'}

## Cell connectivity rules
netParams.connParams['E->all'] = {
  'preConds': {'cellType': 'E'}, 'postConds': {'y': [100,1000]},  #  E -> all (100-1000 um)
  'probability': 0.1 ,                  # probability of connection
  'weight': '5.0*post_ynorm',         # synaptic weight 
  'delay': 'dist_3D/propVelocity',      # transmission delay (ms) 
  'synMech': 'exc'}                     # synaptic mechanism 

netParams.connParams['I->E'] = {
  'preConds': {'cellType': 'I'}, 'postConds': {'pop': ['E2','E4','E5']},       #  I -> E
  'probability': '0.4*exp(-dist_3D/probLengthConst)',   # probability of connection
  'weight': 1.0,                                      # synaptic weight 
  'delay': 'dist_3D/propVelocity',                      # transmission delay (ms) 
  'synMech': 'inh'}                                     # synaptic mechanism 


# Simulation configuration
simConfig = specs.SimConfig()       # object of class SimConfig to store simulation configuration
simConfig.duration = 1.0*1e3        # Duration of the simulation, in ms
simConfig.hParams['v_init'] = -65   # set v_init to -65 mV
simConfig.dt = 0.1                  # Internal integration timestep to use
simConfig.verbose = False            # Show detailed messages 
simConfig.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'net_lfp'   # Set file output name
simConfig.printRunTime = True     # print run time at interval (in sec) specified here (eg. 0.1)
simConfig.recordTraces = {'V_soma':{'sec': 'soma','loc': 0.5,'var': 'v'},
                          'cai_soma': {'sec': 'soma', 'loc':0.5, 'var': 'cai'},
                          'cao_soma': {'sec': 'soma', 'loc':0.5, 'var': 'cao'},
                          'ik_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'ik'},
                          'ica_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'ica'}}
                          #'ki_soma': {'sec': 'soma', 'loc':0.5, 'var': 'ki'}}
                          # 'ko_soma': {'sec': 'soma', 'loc':0.5, 'var': 'ko'},
                          # ,}

                          # 'cai_soma': {'sec': 'soma', 'loc':0.5, 'var': 'cai'},
                          # 
                          # 'ip3_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'ip3i'},
                          # } 


# simConfig.recordLFP = [[-15, y, 1.0*netParams.sizeZ] for y in range(netParams.sizeY/5, netParams.sizeY, netParams.sizeY/5)]

simConfig.analysis['plotTraces']={'include': [0]}
simConfig.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True, 'saveFig':True, 'figSize': (9,3)}      # Plot a raster
# simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'NFFT': 256, 'noverlap': 48, 'nperseg': 64, 'saveFig': True} 

# sim.createSimulateAnalyze()

#### BELOW THIS LINE SHOULD BE DONE IN JUPYTER NB #####

testing = 1
if testing:
    from time import time
    # --------------------------------
    # Instantiate network
    # --------------------------------
    sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
    sim.net.createPops()                  # instantiate network populations
    sim.net.createCells()                 # instantiate network cells based on defined populations
    sim.net.connectCells()                # create connections between cells based on params
    sim.net.addStims()                    # add external stimulation to cells (IClamps etc)

    startTime = time()
    import gui_rxd

    # --------------------------------
    # Simulate and analyze network
    # --------------------------------
    sim.setupRecording()             # setup variables to record for each cell (spikes, V traces, etc)
    sim.simulate()
    print time() - startTime
    sim.analyze()

    gui_rxd.plotExtracellularConcentration(species=gui_rxd.ca)
    #gui_rxd.plotExtracellularConcentration(species=gui_rxd.k)
      
