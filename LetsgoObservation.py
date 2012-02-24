import numpy as np
from Parameters import Factor
import LetsgoSerializer as ls
from SparseBayes import SparseBayes

sbr_models = {'I:bn':ls.load_model('_calibrated_confidence_score_sbr_bn.model'),\
                  'I:dp':ls.load_model('_calibrated_confidence_score_sbr_dp.model'),\
                  'I:ap':ls.load_model('_calibrated_confidence_score_sbr_ap.model'),\
                  'I:tt':ls.load_model('_calibrated_confidence_score_sbr_tt.model'),\
                  'yes':ls.load_model('_calibrated_confidence_score_sbr_yes.model'),\
                  'no':ls.load_model('_calibrated_confidence_score_sbr_no.model'),\
                  'multi2':ls.load_model('_calibrated_confidence_score_sbr_multi2.model'),\
                  'multi3':ls.load_model('_calibrated_confidence_score_sbr_multi3.model'),\
                  'multi4':ls.load_model('_calibrated_confidence_score_sbr_multi4.model')
                  }


def Calibrate(sbr_models,ua,cs):
    def dist_squared(X,Y):
        nx = X.shape[0]
        ny = Y.shape[0]
        return np.dot(np.atleast_2d(np.sum((X**2),1)).T,np.ones((1,ny))) + \
            np.dot(np.ones((nx,1)),np.atleast_2d(np.sum((Y**2),1))) - 2*np.dot(X,Y.T);

    def basis_vector(X,x,basisWidth):
        BASIS = np.exp(-dist_squared(x,X)/(basisWidth**2))
        return BASIS
    
    sbr_model = None
    if len(ua) == 1:
        try:
            sbr_model = sbr_models[ua[0]]
        except:
#            print 'No SBR model for %s'%ua[0]
            pass
    elif len(ua) == 2:
        sbr_model = sbr_models['multi2']
    elif len(ua) == 3:
        sbr_model = sbr_models['multi3']
    else:
        sbr_model = sbr_models['multi4']
    
    if sbr_model:
        calibrated_cs = np.dot(basis_vector(sbr_model['data_points'],\
                                                 np.array([[cs]]),\
                                                 sbr_model['basis_width']),\
                                    sbr_model['weights'])[0,0]
        if calibrated_cs < 0: 
            calibrated_cs = 0
        return float(calibrated_cs)
    return cs

#def getObsFactor(turn,ceiling=1.0,p=1.5,use_cs=False,cs_weight=0.8):
def getObsFactor(turn,ceiling=1.0,p=1.5,use_cs=False,cs_weight=0.99999):
    
#    if turn['UA'] == ['non-understanding']:
#        eps += 0.1
    fUAtt_Ott = Factor(('UA_tt',))
    ua_types = [['I:bn','I:dp','I:ap','I:tt'],\
          ['I:bn','I:dp','I:ap'],\
          ['I:dp','I:ap','I:tt'],\
          ['I:bn','I:dp','I:tt'],\
          ['I:dp','I:ap'],\
          ['I:dp','I:tt'],\
          ['I:ap','I:tt'],\
          ['I:bn','I:tt'],\
          ['I:bn'],\
          ['I:dp'],\
          ['I:ap'],\
          ['I:tt'],\
          ['yes'],\
          ['no'],\
          ['no','I:bn'],\
          ['no','I:dp'],\
          ['no','I:ap'],\
          ['no','I:tt'],\
          ['non-understanding']]

#    print turn['UA']
#    print turn['CS']

    if use_cs: 
        cs = turn['CS']
#        print turn['UA']
#        print type(cs),cs
        cs = Calibrate(sbr_models,turn['UA'],cs)
#        print type(cs),cs
        
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