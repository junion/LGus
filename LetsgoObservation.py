from Parameters import Factor

def getObsFactor(turn,ceiling=1.0,p=1.5,use_cs=False,cs_weight=0.8):
#    if turn['UA'] == ['non-understanding']:
#        eps += 0.1
    fUAtt_Ott = Factor(('UA_tt',))
    ua_types = [['I:bn','I:dp','I:ap','I:tt'],\
          ['I:bn','I:dp','I:ap'],\
          ['I:dp','I:ap','I:tt'],\
          ['I:bn','I:dp','I:tt'],\
          ['I:dp','I:ap'],\
          ['I:bn','I:tt'],\
          ['I:bn'],\
          ['I:dp'],\
          ['I:ap'],\
          ['I:tt'],\
          ['yes'],\
          ['no'],\
          ['non-understanding']]

#    print turn['UA']
#    print turn['CS']

    if use_cs: cs = turn['CS']
    else: cs = 0.99
    cs = cs*cs_weight
    eps = (1.0 - cs)/len(ua_types)
    for ua in ua_types:
        fUAtt_Ott[{'UA_tt':','.join(sorted(ua))}] = \
        min(\
            cs*(float(len(set(ua).intersection(set(turn['UA']))))/len(set(ua).union(set(turn['UA']))))**p,\
            ceiling)\
             + eps
#        print set(ua).intersection(set(turn['UA']))
#        print set(ua).union(set(turn['UA']))
#        print float(len(set(ua).intersection(set(turn['UA']))))/len(set(ua).union(set(turn['UA'])))

#    fUAtt_Ott[{'UA_tt':'I:bn,I:dp,I:ap,I:tt'}] = min(turn['CS']*(len(set(['I:bn','I:dp','I:ap','I:tt']).intersection(set(turn['UA'])))/len(set(['I:bn','I:dp','I:ap','I:tt']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'I:bn,I:dp,I:ap'}] = min(turn['CS']*(len(set(['I:bn','I:dp','I:ap']).intersection(set(turn['UA'])))/len(set(['I:bn','I:dp','I:ap']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'I:dp,I:ap,I:tt'}] = min(turn['CS']*(len(set(['I:dp','I:ap','I:tt']).intersection(set(turn['UA'])))/len(set(['I:dp','I:ap','I:tt']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'I:bn,I:dp,I:tt'}] = min(turn['CS']*(len(set(['I:bn','I:dp','I:tt']).intersection(set(turn['UA'])))/len(set(['I:bn','I:dp','I:tt']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'I:dp,I:ap'}] = min(turn['CS']*(len(set(['I:dp','I:ap']).intersection(set(turn['UA'])))/len(set(['I:dp','I:ap']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'I:bn,I:tt'}] = min(turn['CS']*(len(set(['I:bn','I:tt']).intersection(set(turn['UA'])))/len(set(['I:bn','I:tt']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'I:bn'}] = min(turn['CS']*(len(set(['I:bn']).intersection(set(turn['UA'])))/len(set(['I:bn']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'I:dp'}] = min(turn['CS']*(len(set(['I:dp']).intersection(set(turn['UA'])))/len(set(['I:dp']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'I:ap'}] = min(turn['CS']*(len(set(['I:ap']).intersection(set(turn['UA'])))/len(set(['I:ap']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'I:tt'}] = min(turn['CS']*(len(set(['I:tt']).intersection(set(turn['UA'])))/len(set(['I:tt']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'yes'}] = min(turn['CS']*(len(set(['yes']).intersection(set(turn['UA'])))/len(set(['yes']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'no'}] = min(turn['CS']*(len(set(['no']).intersection(set(turn['UA'])))/len(set(['no']).union(set(turn['UA']))))**p,ceiling) + eps
#    fUAtt_Ott[{'UA_tt':'non-understanding'}] = min(turn['CS']*(len(set(['non-understanding']).intersection(set(turn['UA'])))/len(set(['non-understanding']).union(set(turn['UA']))))**p,ceiling) + eps

#    print fUAtt_Ott
    return fUAtt_Ott