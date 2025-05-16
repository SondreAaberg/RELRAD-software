import pandas as pd
import MonteCarloSimulation as mc
import RELRAD as rr
import copy
from concurrent.futures import ThreadPoolExecutor



#RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214.xlsx')
#MonteCarlo('RBMC p214.xlsx', 5000, 'MonteCarloResultsRBMCp214.xlsx')
'''
mc.MonteCarlo('BUS 4.xlsx', 'MonteCarloResultsBUS4.xlsx', beta=0.02, DSEBF = False)
rr.RELRAD('BUS 4.xlsx', 'RELRADResultsBUS4.xlsx', DSEBF = False)
mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResultsRBMCp214.xlsx', beta=0.02, DSEBF = False)
rr.RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214.xlsx', DSEBF = False)
mc.MonteCarlo('BUS 2.xlsx', 'MonteCarloResultsBUS2.xlsx', beta=0.02, DSEBF = False)
rr.RELRAD('BUS 2.xlsx', 'RELRADResultsBUS2.xlsx', DSEBF = False)
mc.MonteCarlo('BUS 6.xlsx', 'MonteCarloResultsBUS6.xlsx', beta=0.02, DSEBF = False)
rr.RELRAD('BUS 6.xlsx', 'RELRADResultsBUS6.xlsx', DSEBF = False)
mc.MonteCarlo('SimpleTest.xlsx', 'MonteCarloResultsSimpleTest.xlsx', beta=0.02, DSEBF = False, DERS=False)
rr.RELRAD('SimpleTest.xlsx', 'RELRADResultsSimpleTest.xlsx', DSEBF = False, DERS=False)
'''

#mc.MonteCarlo('BUS 6 Sub2 mod.xlsx', 'MonteCarloResultsBUS6Sub2M.xlsx', beta=0.02, DSEBF = False, LoadCurve=False, DERS=False)
#mc.MonteCarlo('BUS 6 Sub2 mod.xlsx', 'MonteCarloResultsBUS6Sub2MLoadCurve.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERS=False)
mc.MonteCarlo('BUS 6 Sub2 mod.xlsx', 'MonteCarloResultsBUS6Sub2MDERS.xlsx', beta=0.02, DSEBF = False, LoadCurve=False, DERS=True)
mc.MonteCarlo('BUS 6 Sub2 mod.xlsx', 'MonteCarloResultsBUS6Sub2MLoadCurveDERS.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERS=True)
mc.MonteCarlo('BUS 6 Sub2 mod.xlsx', 'MonteCarloResultsBUS6Sub2MDERSCurve.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERScurve=True, DERS=True)


#rr.RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214DERS_BESS.xlsx', DSEBF = False, DERS = True)
#rr.RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214_DERSCase3.xlsx', DSEBF = False, DERS = True)


#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_BaseCase.xlsx', beta=0.02, DSEBF = False, LoadCurve=False, DERS=False)
#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_LoadCurve.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERS=False)
#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_DERS.xlsx', beta=0.02, DSEBF = False, LoadCurve=False, DERS=True)
#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_LoadCurveDERS.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERS=True)
#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_DERSCurve.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERScurve=True, DERS=True)


#rr.RELRAD('BUS 6.xlsx', 'RELRADResultsBUS6.xlsx', DSEBF = False)
