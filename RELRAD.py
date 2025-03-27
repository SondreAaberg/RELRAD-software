import pandas as pd

loadPoints = pd.read_excel('Data.xlsx', 'LoadPoints', index_col=0 )
components = pd.read_excel('Data.xlsx', 'Components', index_col=0)
matching = pd.read_excel('Data.xlsx', 'Matching', index_col=0)


#loadPoints [nr, avrg load, peak load, nr of customers]
#components [lambda]
#matching component/lp [r]


#sum lambda and sum (lamda*r)

print(loadPoints)
print(components)
print(matching)

for i in loadPoints:
    print(i)
for j in components:
    print(j)

for i, row in loadPoints.iterrows():
    for j, row in components.iterrows():
        u = matching[i][j]
        if u != 0:
            loadPoints.loc[i, 'lambda'] += components['lambda'][j]
            loadPoints.loc[i, 'U'] += u * components['lambda'][j]
    loadPoints.loc[i, 'r'] = loadPoints['U'][i]/loadPoints['lambda'][i]

print(loadPoints)