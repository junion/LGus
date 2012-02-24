
#import Variables
#import Utils
#from Models import CPT
#from Parameters import Factor
#from LetsgoSerialize import *

G_bn = ('o','x')
#G_dp = ('o')
#G_ap = ('o')
#G_tt = ('o')

UA = ('I:ap,I:bn,I:dp,I:tt',\
      'I:ap,I:bn,I:dp',\
      'I:ap,I:dp,I:tt',\
      'I:bn,I:dp,I:tt',\
      'I:ap,I:dp',\
      'I:dp,I:tt',\
      'I:ap,I:tt',\
      'I:bn,I:tt',\
      'I:bn',\
      'I:dp',\
      'I:ap',\
      'I:tt',\
      'yes',\
      'no',\
      'no,I:bn',\
      'no,I:dp',\
      'no,I:ap',\
      'no,I:tt',\
      'non-understanding'\
      )

SA = ('R:open',\
      'R:bn',\
      'R:dp',\
      'R:ap',\
      'R:tt',\
      'C:bn:o',\
      'C:bn:x',\
      'C:dp:o',\
      'C:dp:x',\
      'C:ap:o',\
      'C:ap:x',\
      'C:tt:o',\
      'C:tt:x',\
      'O:-'\
      )

H_bn = ('x','o')
H_dp = ('x','o')
H_ap = ('x','o')
H_tt = ('x','o')



#
#     
#fGbn_Ht_SAtt_UAtt = CPT(Factor(('H_bn_t','H_dp_t','H_ap_t','H_tt_t','UA_tt')),child='UA_tt',cpt_force=True)
#factor_template = {'G_bn':G_bn,'SA':SA}
#for factor in Utils.inst_filling(factor_template):
#    if not existFactor(('_factor_%s_%s.model'%(factor['G_bn'],factor['SA'])).replace(':','-')):
#        storeFactor(fGbn_Ht_SAtt_UAtt,('_factor_%s_%s.model'%(factor['G_bn'],factor['SA'])).replace(':','-'))
#del fGbn_Ht_SAtt_UAtt
