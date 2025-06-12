import pandas as pd
import MonteCarloSimulation as mc
import RELRAD as rr
import copy
from concurrent.futures import ThreadPoolExecutor

'''
RELRAD-software, general software for reliability studies of radial power systems
    Copyright (C) 2025  Sondre Modalsli Aaberg

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


# Main file, run either mc.MonteCarlo or rr.RELRAD here



#Examples:

#rr.RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214.xlsx')
#rr.RELRAD('Myhre 6Bus System.xlsx', 'RELRADResultsMyhre6Bus.xlsx', DSEBF = False, DERS = False)
#mc.MonteCarlo('Myhre 6Bus System.xlsx', 'MonteCarloResultsMyhre6Bus.xlsx', beta=0.02, DSEBF = False, LoadCurve=False, DERS=False)

#mc.MonteCarlo('BUS 2.xlsx', 'MonteCarloResultsBUS2.xlsx', beta=0.05, DSEBF = False)
#rr.RELRAD('BUS 2.xlsx', 'RELRADResultsBUS2.xlsx', DSEBF = False, createFIM=True, DERS=False)

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
#mc.MonteCarlo('BUS 6 Sub2 mod.xlsx', 'MonteCarloResultsBUS6Sub2MDERS.xlsx', beta=0.02, DSEBF = False, LoadCurve=False, DERS=True)
#mc.MonteCarlo('BUS 6 Sub2 mod.xlsx', 'MonteCarloResultsBUS6Sub2MLoadCurveDERS.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERS=True)
#mc.MonteCarlo('BUS 6 Sub2 mod.xlsx', 'MonteCarloResultsBUS6Sub2MDERSCurve.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERScurve=True, DERS=True)


#rr.RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214DERS_BESS.xlsx', DSEBF = False, DERS = True)
#rr.RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214_DERSCase3.xlsx', DSEBF = False, DERS = True)


#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_BaseCase.xlsx', beta=0.02, DSEBF = False, LoadCurve=False, DERS=False)
#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_LoadCurve.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERS=False)
#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_DERS.xlsx', beta=0.02, DSEBF = False, LoadCurve=False, DERS=True)
#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_LoadCurveDERS.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERS=True)
#mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResults_p214_DERSCurve.xlsx', beta=0.02, DSEBF = False, LoadCurve=True, DERScurve=True, DERS=True)

#rr.RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214.xlsx', DSEBF = False, DERS = False)
#rr.RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214DERS.xlsx', DSEBF = False, DERS = True)


#rr.RELRAD('BUS 6.xlsx', 'RELRADResultsBUS6.xlsx', DSEBF = False)



#rr.RELRAD('BUS 5 RELSAD MOD.xlsx', 'RELRADResultsBUS5.xlsx', DSEBF = False, DERS=False)
#mc.MonteCarlo('BUS 5 RELSAD MOD.xlsx', 'MonteCarloResultsBUS5.xlsx', beta=0.05, DSEBF = False, LoadCurve=False, DERS=False)
