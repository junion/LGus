import Variables
from Parameters import Factor
from Models import SFR, JFR, CPT

''' Let's Go Random Variables and Values '''

G_bn = ('o','x')
#G_dp = ('o')
#G_ap = ('o')
#G_tt = ('o')

UA = ('I:bn,I:dp,I:ap,I:tt',\
      'I:bn,I:dp,I:ap',\
      'I:dp,I:ap,I:tt',\
      'I:bn,I:dp,I:tt',\
      'I:dp,I:ap',\
      'I:bn,I:tt',\
      'I:bn',\
      'I:dp',\
      'I:ap',\
      'I:tt',\
      'yes',\
      'no',\
      )

SA = ('R:open',\
      'R:bn',\
      'R:dp',\
      'R:ap',\
      'R:tt',\
      'C:o',\
      'C:x',\
      'C:-'\
      'I:bus'\
      )

H_bn = ('x','o')
H_dp = ('x','o')
H_ap = ('x','o')
H_tt = ('x','o')

Variables.clear_default_domain()

''' 
Let's Go Dynamic Graphical Model 

Initial State
Transition Network
Evidences

'''

fH0 = Factor(('H_bn_0','H_dp_0','H_ap_0','H_tt_0'),
            data=[0]*16,\
            new_domain_variables={'H_bn_0':H_bn,'H_dp_0':H_dp,'H_ap_0':H_ap,'H_tt_0':H_tt})
fH0[{'H_bn_0':'x','H_dp_0':'x','H_ap_0':'x','H_tt_0':'x'}] = 1

fH0_UA1_H1 = Factor(('H_bn_0','H_dp_0','H_ap_0','H_tt_0','UA_1','H_bn_1','H_dp_1','H_ap_1','H_tt_1'),
            data=[0]*3072,\
            new_domain_variables={'UA_1':UA,'H_bn_1':H_bn,'H_dp_1':H_dp,'H_ap_1':H_ap,'H_tt_1':H_tt})

def inst_filling(inst_template):
    import itertools
    return (dict(itertools.izip(inst_template, x)) for x in itertools.product(*inst_template.itervalues()))

for inst in inst_filling({'H_bn_0':H_bn,'H_dp_0':H_dp,'H_ap_0':H_ap,'H_tt_0':H_tt,'UA_1':UA,'H_bn_1':H_bn,'H_dp_1':H_dp,'H_ap_1':H_ap,'H_tt_1':H_tt}):
    if ((('bn' in inst['UA_1'] or inst['H_bn_0'] == 'o') and inst['H_bn_1'] == 'o') and\
    (('dp' in inst['UA_1'] or inst['H_dp_0'] == 'o') and inst['H_dp_1'] == 'o') and\
    (('ap' in inst['UA_1'] or inst['H_ap_0'] == 'o') and inst['H_ap_1'] == 'o') and\
    (('tt' in inst['UA_1'] or inst['H_tt_0'] == 'o') and inst['H_tt_1'] == 'o')) or\
    ((('bn' not in inst['UA_1'] and inst['H_bn_0'] == 'x') and inst['H_bn_1'] == 'x') and\
    (('dp' not in inst['UA_1'] and inst['H_dp_0'] == 'x') and inst['H_dp_1'] == 'x') and\
    (('ap' not in inst['UA_1'] and inst['H_ap_0'] == 'x') and inst['H_ap_1'] == 'x') and\
    (('tt' not in inst['UA_1'] and inst['H_tt_0'] == 'x') and inst['H_tt_1'] == 'x')) or\
    ((('bn' not in inst['UA_1'] and inst['H_bn_0'] == 'x') and inst['H_bn_1'] == 'x') and\
    (('dp' in inst['UA_1'] or inst['H_dp_0'] == 'o') and inst['H_dp_1'] == 'o') and\
    (('ap' in inst['UA_1'] or inst['H_ap_0'] == 'o') and inst['H_ap_1'] == 'o') and\
    (('tt' in inst['UA_1'] or inst['H_tt_0'] == 'o') and inst['H_tt_1'] == 'o')) or\
    ((('bn' in inst['UA_1'] or inst['H_bn_0'] == 'o') and inst['H_bn_1'] == 'o') and\
    (('dp' not in inst['UA_1'] and inst['H_dp_0'] == 'x') and inst['H_dp_1'] == 'x') and\
    (('ap' in inst['UA_1'] or inst['H_ap_0'] == 'o') and inst['H_ap_1'] == 'o') and\
    (('tt' in inst['UA_1'] or inst['H_tt_0'] == 'o') and inst['H_tt_1'] == 'o')) or\
    ((('bn' in inst['UA_1'] or inst['H_bn_0'] == 'o') and inst['H_bn_1'] == 'o') and\
    (('dp' in inst['UA_1'] or inst['H_dp_0'] == 'o') and inst['H_dp_1'] == 'o') and\
    (('ap' not in inst['UA_1'] and inst['H_ap_0'] == 'x') and inst['H_ap_1'] == 'x') and\
    (('tt' in inst['UA_1'] or inst['H_tt_0'] == 'o') and inst['H_tt_1'] == 'o')) or\
    ((('bn' in inst['UA_1'] or inst['H_bn_0'] == 'o') and inst['H_bn_1'] == 'o') and\
    (('dp' in inst['UA_1'] or inst['H_dp_0'] == 'o') and inst['H_dp_1'] == 'o') and\
    (('ap' in inst['UA_1'] or inst['H_ap_0'] == 'o') and inst['H_ap_1'] == 'o') and\
    (('tt' not in inst['UA_1'] and inst['H_tt_0'] == 'x') and inst['H_tt_1'] == 'x')) or\
    ((('bn' not in inst['UA_1'] and inst['H_bn_0'] == 'x') and inst['H_bn_1'] == 'x') and\
    (('dp' not in inst['UA_1'] and inst['H_dp_0'] == 'x') and inst['H_dp_1'] == 'x') and\
    (('ap' in inst['UA_1'] or inst['H_ap_0'] == 'o') and inst['H_ap_1'] == 'o') and\
    (('tt' in inst['UA_1'] or inst['H_tt_0'] == 'o') and inst['H_tt_1'] == 'o')) or\
    ((('bn' not in inst['UA_1'] and inst['H_bn_0'] == 'x') and inst['H_bn_1'] == 'x') and\
    (('dp' in inst['UA_1'] or inst['H_dp_0'] == 'o') and inst['H_dp_1'] == 'o') and\
    (('ap' not in inst['UA_1'] and inst['H_ap_0'] == 'x') and inst['H_ap_1'] == 'x') and\
    (('tt' in inst['UA_1'] or inst['H_tt_0'] == 'o') and inst['H_tt_1'] == 'o')) or\
    ((('bn' not in inst['UA_1'] and inst['H_bn_0'] == 'x') and inst['H_bn_1'] == 'x') and\
    (('dp' in inst['UA_1'] or inst['H_dp_0'] == 'o') and inst['H_dp_1'] == 'o') and\
    (('ap' in inst['UA_1'] or inst['H_ap_0'] == 'o') and inst['H_ap_1'] == 'o') and\
    (('tt' not in inst['UA_1'] and inst['H_tt_0'] == 'x') and inst['H_tt_1'] == 'x')) or\
    ((('bn' in inst['UA_1'] or inst['H_bn_0'] == 'o') and inst['H_bn_1'] == 'o') and\
    (('dp' not in inst['UA_1'] and inst['H_dp_0'] == 'x') and inst['H_dp_1'] == 'x') and\
    (('ap' not in inst['UA_1'] and inst['H_ap_0'] == 'x') and inst['H_ap_1'] == 'x') and\
    (('tt' in inst['UA_1'] or inst['H_tt_0'] == 'o') and inst['H_tt_1'] == 'o')) or\
    ((('bn' in inst['UA_1'] or inst['H_bn_0'] == 'o') and inst['H_bn_1'] == 'o') and\
    (('dp' in inst['UA_1'] or inst['H_dp_0'] == 'o') and inst['H_dp_1'] == 'o') and\
    (('ap' not in inst['UA_1'] and inst['H_ap_0'] == 'x') and inst['H_ap_1'] == 'x') and\
    (('tt' not in inst['UA_1'] and inst['H_tt_0'] == 'x') and inst['H_tt_1'] == 'x')) or\
    ((('bn' not in inst['UA_1'] and inst['H_bn_0'] == 'x') and inst['H_bn_1'] == 'x') and\
    (('dp' not in inst['UA_1'] and inst['H_dp_0'] == 'x') and inst['H_dp_1'] == 'x') and\
    (('ap' not in inst['UA_1'] and inst['H_ap_0'] == 'x') and inst['H_ap_1'] == 'x') and\
    (('tt' in inst['UA_1'] or inst['H_tt_0'] == 'o') and inst['H_tt_1'] == 'o')) or\
    ((('bn' not in inst['UA_1'] and inst['H_bn_0'] == 'x') and inst['H_bn_1'] == 'x') and\
    (('dp' not in inst['UA_1'] and inst['H_dp_0'] == 'x') and inst['H_dp_1'] == 'x') and\
    (('ap' in inst['UA_1'] or inst['H_ap_0'] == 'o') and inst['H_ap_1'] == 'o') and\
    (('tt' not in inst['UA_1'] and inst['H_tt_0'] == 'x') and inst['H_tt_1'] == 'x')) or\
    ((('bn' not in inst['UA_1'] and inst['H_bn_0'] == 'x') and inst['H_bn_1'] == 'x') and\
    (('dp' in inst['UA_1'] or inst['H_dp_0'] == 'o') and inst['H_dp_1'] == 'o') and\
    (('ap' not in inst['UA_1'] and inst['H_ap_0'] == 'x') and inst['H_ap_1'] == 'x') and\
    (('tt' not in inst['UA_1'] and inst['H_tt_0'] == 'x') and inst['H_tt_1'] == 'x')) or\
    ((('bn' in inst['UA_1'] or inst['H_bn_0'] == 'o') and inst['H_bn_1'] == 'o') and\
    (('dp' not in inst['UA_1'] and inst['H_dp_0'] == 'x') and inst['H_dp_1'] == 'x') and\
    (('ap' not in inst['UA_1'] and inst['H_ap_0'] == 'x') and inst['H_ap_1'] == 'x') and\
    (('tt' not in inst['UA_1'] and inst['H_tt_0'] == 'x') and inst['H_tt_1'] == 'x')):
        fH0_UA1_H1[inst] = 1


fGbn_H0_SA1_UA1 = Factor(('H_bn_0','H_dp_0','H_ap_0','H_tt_0','UA_1'))

fUA1_O1 = Factor(('UA_1',))
fUA1_O1[{'UA_1':'I:bn,I:dp,I:ap,I:tt'}] = 0.09836/2
fUA1_O1[{'UA_1':'I:bn,I:dp,I:ap'}] = 0.09836*2/3
fUA1_O1[{'UA_1':'I:dp,I:ap,I:tt'}] = 0.09836/3
fUA1_O1[{'UA_1':'I:bn,I:dp,I:tt'}] = 0.09836*2/3
fUA1_O1[{'UA_1':'I:dp,I:ap'}] = 0.09836/2
fUA1_O1[{'UA_1':'I:bn,I:tt'}] = 0.09836/2
fUA1_O1[{'UA_1':'I:bn'}] = 0.09836/2
fUA1_O1[{'UA_1':'I:dp'}] = 0.09836/2
fUA1_O1[{'UA_1':'I:ap'}] = 0
fUA1_O1[{'UA_1':'I:tt'}] = 0
fUA1_O1[{'UA_1':'yes'}] = 0
fUA1_O1[{'UA_1':'no'}] = 0

ft1 = fH0 * fH0_UA1_H1 * fGbn_H0_SA1_UA1 *fUA1_O1


fH1_UA2_H2 = Factor(('H_bn_1','H_dp_1','H_ap_1','H_tt_1','UA_2','H_bn_2','H_dp_2','H_ap_2','H_tt_2'),
            new_domain_variables={'UA_2':UA,'H_bn_2':H_bn,'H_dp_2':H_dp,'H_ap_2':H_ap,'H_tt_2':H_tt})

fH1_UA2_H2[:] = fH0_UA1_H1[:]

fGbn_H1_SA2_UA2 = Factor(('H_bn_1','H_dp_1','H_ap_1','H_tt_1','UA_2'))

fUA2_O2 = Factor(('UA_2',))
fUA2_O2[{'UA_2':'I:bn,I:dp,I:ap,I:tt'}] = 0
fUA2_O2[{'UA_2':'I:bn,I:dp,I:ap'}] = 0
fUA2_O2[{'UA_2':'I:dp,I:ap,I:tt'}] = 0
fUA2_O2[{'UA_2':'I:bn,I:dp,I:tt'}] = 0
fUA2_O2[{'UA_2':'I:dp,I:ap'}] = 0
fUA2_O2[{'UA_2':'I:bn,I:tt'}] = 0
fUA2_O2[{'UA_2':'I:bn'}] = 0
fUA2_O2[{'UA_2':'I:dp'}] = 0
fUA2_O2[{'UA_2':'I:ap'}] = 0
fUA2_O2[{'UA_2':'I:tt'}] = 0
fUA2_O2[{'UA_2':'yes'}] = 0.92404
fUA2_O2[{'UA_2':'no'}] = 0

ft2 = fH1_UA2_H2 * fGbn_H1_SA2_UA2 * fUA2_O2

jfr = JFR(SFR([ft1,ft2]))

#jfr.condition({'UA_1':['I:bn']})
jfr.calibrate()
#print jfr

#print jfr.var_marginal('H_bn_1')
#print jfr.var_marginal('H_bn_2')
#print jfr.var_marginal('UA_1')
#print jfr.var_marginal('UA_2')


rf = jfr.factors_containing_variable('UA_2')
print CPT(rf[0].copy().marginalise_onto(['H_bn_1','H_dp_1','H_ap_1','H_tt_1','UA_2']).normalised(),'UA_2') + CPT(rf[0].copy().marginalise_onto(['H_bn_1','H_dp_1','H_ap_1','H_tt_1','UA_2']).normalised(),'UA_2')


import time
time.sleep(100)