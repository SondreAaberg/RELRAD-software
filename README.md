# Simple-System-for-Power-System-Reliability-Calculations
Monte Carlo simulation and RELRAD algorithm for radial systems



How to use:

Run the RELRAD functrion for form the RELRAD.py file or the MonteCarlo function from the MonteCarloSimulation file in the Main.py file with the location of input and output data.
All requiered input data must be provided in the format form the format file, or as shown in the provided systems


Options:
    Monte Carlo
        - DSEBF = True/False            Down Stream Effects of Backup Feeder, adds a swithing time to the opposite side of backup feeders between the backupfeeder and the backup feeder and the closest fuse/breaker
        - DERS = True/False             Distributed Energy Resources, enables the use of the provided DERS
        - LoadCurve = True True/False   Enables the use of provided load curve
        - DERScurve = True True/False   Enables the use of provided DERS curve (WIP, this feature cant gather the info from provided file)
    RELRAD:
        - DSEBF = True/False 
        - DERS = False/False


Known issues:
    - It's not possible to have multiple load points or DERS on one bus, if this is needed create new dummy buses connected to the relevant bus with lines with no failure rate.
    - Most of the reliaiblity indeces for each spesific bus are intermediat values, and not reliable