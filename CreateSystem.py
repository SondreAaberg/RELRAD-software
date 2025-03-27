def fixbuses(buses, sections):
    for i, row in buses.iterrows():
        up = 0
        down = []
        for j, row2 in sections.iterrows():
            if sections['Upstream Bus'][j] == i:
                down.append(j)
            if sections['Downstream Bus'][j] == i:
                up = j
        buses['Upstream Section'][i] = up
        buses['Downstream Sections'][i] = down
        buses['Connected Sections'][i] = down.copy()
        buses['Connected Sections'][i].append(up)
    return buses


def calcFailRates(sections, components):
    for i, row in sections.iterrows():
        secComponents = {}
        secComponents['line'] = {'type': sections['Cable Type'][i], 'length': sections['Length'][i], 'lambda': components['lambda'][sections['Cable Type'][i]] * sections['Length'][i], 'r': components['r'][sections['Cable Type'][i]], 's': components['s'][sections['Cable Type'][i]]}
        if sections['Nr Transformers'][i]:
            secComponents['transformer'] = {'type': sections['Transformer Type'][i], 'lambda': components['lambda'][sections['Transformer Type'][i]] * sections['Nr Transformers'][i], 'r': components['r'][sections['Transformer Type'][i]], 's': components['s'][sections['Transformer Type'][i]]}
        #if sections['Nr Breaker'][i]:
            #sections.iloc[i,'lambda'] += components['lambda'][sections['Breaker Type'][i]] * sections['Nr Breaker'][i]
        sections['s'][i] = components['s'][sections['Cable Type'][i]]
        sections['Components'][i] = secComponents
    return sections