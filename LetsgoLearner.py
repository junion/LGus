import time,math,operator
import Variables
from Parameters import Factor
from Models import SFR, JFR, CPT
import Utils
import LetsgoCorpus as lc
import LetsgoSerializer as ls
import LetsgoVariables as lv
import LetsgoObservation as lo

class LetsgoIntentionModelLearner(object):
    
    def __init__(self,data=None,method='EM',iter=20,tol=0.01,inc=False,prep=False):
        self.data = data
        self.method = method
        self.iter = iter
        self.tol = tol
        self.inc = inc
        self.learners = {'EM':self.EM_learn}
        self.prep = prep
        
    def _reset_param(self):
        Variables.clear_default_domain()
        Variables.set_default_domain({'H_bn_t':lv.H_bn,'H_dp_t':lv.H_dp,'H_ap_t':lv.H_ap,\
                                      'H_tt_t':lv.H_tt,'UA_tt':lv.UA,'H_bn_tt':lv.H_bn,\
                                      'H_dp_tt':lv.H_dp,'H_ap_tt':lv.H_ap,'H_tt_tt':lv.H_tt,\
                                      'H_bn_0':lv.H_bn,'H_dp_0':lv.H_dp,'H_ap_0':lv.H_ap,'H_tt_0':lv.H_tt})

        fH_bn_t_UAtt_H_bn_tt = Factor(('H_bn_t','UA_tt','H_bn_tt'))
        fH_bn_t_UAtt_H_bn_tt.zero()
        for inst in Utils.inst_filling({'H_bn_t':lv.H_bn,'UA_tt':lv.UA,'H_bn_tt':lv.H_bn}):
            if (('bn' in inst['UA_tt'] or inst['H_bn_t'] == 'o') and inst['H_bn_tt'] == 'o') or\
            (('bn' not in inst['UA_tt'] and inst['H_bn_t'] == 'x') and inst['H_bn_tt'] == 'x'):
                fH_bn_t_UAtt_H_bn_tt[inst] = 1
        fH_dp_t_UAtt_H_dp_tt = Factor(('H_dp_t','UA_tt','H_dp_tt'))
        fH_dp_t_UAtt_H_dp_tt.zero()
        for inst in Utils.inst_filling({'H_dp_t':lv.H_dp,'UA_tt':lv.UA,'H_dp_tt':lv.H_dp}):
            if (('dp' in inst['UA_tt'] or inst['H_dp_t'] == 'o') and inst['H_dp_tt'] == 'o') or\
            (('dp' not in inst['UA_tt'] and inst['H_dp_t'] == 'x') and inst['H_dp_tt'] == 'x'):
                fH_dp_t_UAtt_H_dp_tt[inst] = 1
        fH_ap_t_UAtt_H_ap_tt = Factor(('H_ap_t','UA_tt','H_ap_tt'))
        fH_ap_t_UAtt_H_ap_tt.zero()
        for inst in Utils.inst_filling({'H_ap_t':lv.H_ap,'UA_tt':lv.UA,'H_ap_tt':lv.H_ap}):
            if (('ap' in inst['UA_tt'] or inst['H_ap_t'] == 'o') and inst['H_ap_tt'] == 'o') or\
            (('ap' not in inst['UA_tt'] and inst['H_ap_t'] == 'x') and inst['H_ap_tt'] == 'x'):
                fH_ap_t_UAtt_H_ap_tt[inst] = 1
        fH_tt_t_UAtt_H_tt_tt = Factor(('H_tt_t','UA_tt','H_tt_tt'))
        fH_tt_t_UAtt_H_tt_tt.zero()
        for inst in Utils.inst_filling({'H_tt_t':lv.H_tt,'UA_tt':lv.UA,'H_tt_tt':lv.H_tt}):
            if (('tt' in inst['UA_tt'] or inst['H_tt_t'] == 'o') and inst['H_tt_tt'] == 'o') or\
            (('tt' not in inst['UA_tt'] and inst['H_tt_t'] == 'x') and inst['H_tt_tt'] == 'x'):
                fH_tt_t_UAtt_H_tt_tt[inst] = 1
        fHt_UAtt_Htt = fH_bn_t_UAtt_H_bn_tt * fH_dp_t_UAtt_H_dp_tt * fH_ap_t_UAtt_H_ap_tt * fH_tt_t_UAtt_H_tt_tt
        ls.store_model(fHt_UAtt_Htt,'_factor_Ht_UAtt_Htt.model')
        
        fGbn_Ht_SAtt_UAtt = CPT(Factor(('H_bn_t','H_dp_t','H_ap_t','H_tt_t','UA_tt')),child='UA_tt',cpt_force=True)
        factor_template = {'G_bn':lv.G_bn,'SA':lv.SA}
        for factor in Utils.inst_filling(factor_template):
            ls.store_model(fGbn_Ht_SAtt_UAtt,('_factor_%s_%s.model'%(factor['G_bn'],factor['SA'])).replace(':','-'))
        del fGbn_Ht_SAtt_UAtt

    def learn(self):
        try:
            self.learners[self.method]()
        except:
            'Does not support %s'%self.method
        
    def EM_learn(self):
        print 'Parameter learning start...'
        start_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        
        if not self.inc:
            self._reset_param()
        else:
            Variables.clear_default_domain()
            Variables.set_default_domain({'H_bn_t':lv.H_bn,'H_dp_t':lv.H_dp,'H_ap_t':lv.H_ap,\
                                          'H_tt_t':lv.H_tt,'UA_tt':lv.UA,'H_bn_tt':lv.H_bn,\
                                          'H_dp_tt':lv.H_dp,'H_ap_tt':lv.H_ap,'H_tt_tt':lv.H_tt,\
                                          'H_bn_0':lv.H_bn,'H_dp_0':lv.H_dp,'H_ap_0':lv.H_ap,\
                                          'H_tt_0':lv.H_tt})

        fHt_UAtt_Htt = ls.load_model('_factor_Ht_UAtt_Htt.model')
        
        prevloglik = -1000000000000000
        loglik = 0.0
        for i in range(self.iter):
            print 'Iterate %d'%i
            ess = {}
            factor_template = {'G_bn':lv.G_bn,'SA':lv.SA}
            for factor in Utils.inst_filling(factor_template):
                ess[('_factor_%s_%s.model'%(factor['G_bn'],factor['SA'])).replace(':','-')] = \
                Factor(('H_bn_t','H_dp_t','H_ap_t','H_tt_t','UA_tt'))
                ess[('_factor_%s_%s.model'%(factor['G_bn'],factor['SA'])).replace(':','-')][:] = \
                [0.0000000000000001] * len(ess[('_factor_%s_%s.model'%(factor['G_bn'],factor['SA'])).replace(':','-')][:])

            for d, dialog in enumerate(lc.Corpus(self.data,prep=self.prep).dialogs()):
                if len(dialog.turns) > 40:
                    continue
                
                print 'processing dialog #%d...'%d
            
                Variables.change_variable('H_bn_0',lv.H_bn)
                Variables.change_variable('H_dp_0',lv.H_dp)
                Variables.change_variable('H_ap_0',lv.H_ap)
                Variables.change_variable('H_tt_0',lv.H_tt)
            
                dialog_factors = []
                for t, turn in enumerate(dialog.abs_turns):
                    tmp_fHt_UAtt_Htt = Factor(('H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,'H_tt_%s'%t,\
                                               'UA_%s'%(t+1),'H_bn_%s'%(t+1),'H_dp_%s'%(t+1),\
                                               'H_ap_%s'%(t+1),'H_tt_%s'%(t+1)),
                            new_domain_variables={'UA_%s'%(t+1):lv.UA,'H_bn_%s'%(t+1):lv.H_bn,\
                                                  'H_dp_%s'%(t+1):lv.H_dp,'H_ap_%s'%(t+1):lv.H_ap,\
                                                  'H_tt_%s'%(t+1):lv.H_tt})
                    tmp_fHt_UAtt_Htt[:] = fHt_UAtt_Htt[:]
            #            tmp_fHt_UAtt_Htt = fHt_UAtt_Htt.copy_rename({'H_bn_t':'H_bn_%s'%i,'H_dp_t':'H_dp_%s'%i,'H_ap_t':'H_ap_%s'%i,'H_tt_t':'H_tt_%s'%i,'UA_tt':'UA_%s'%(i+1),'H_bn_tt':'H_bn_%s'%(i+1),'H_dp_tt':'H_dp_%s'%(i+1),'H_ap_tt':'H_ap_%s'%(i+1),'H_tt_tt':'H_tt_%s'%(i+1)})            
                    tmp_fGbn_Ht_SAtt_UAtt = Factor(('H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,'H_tt_%s'%t,'UA_%s'%(t+1)))
            #            tmp_fGbn_Ht_SAtt_UAtt = Factor(('H_bn_%s'%i,'H_dp_%s'%i,'H_ap_%s'%i,'H_tt_%s'%i,'UA_%s'%(i+1)),new_domain_variables={'UA_%s'%(i+1):UA,'H_bn_%s'%i:H_bn,'H_dp_%s'%i:H_dp,'H_ap_%s'%i:H_ap,'H_tt_%s'%i:H_tt})
                    try:
                        tmp_fGbn_Ht_SAtt_UAtt[:] = \
                        ls.load_model(('_factor_%s_%s.model'%(dialog.abs_goal['G_bn'],turn['SA'][0])).replace(':','-'))[:]
                    except:
                        print ('Error:cannot find _factor_%s_%s.model'%(dialog.abs_goal['G_bn'],turn['SA'][0])).replace(':','-')
                        exit()
                    tmp_fUAtt_Ott = Factor(('UA_%s'%(t+1),))
                    tmp_fUAtt_Ott[:] = lo.getObsFactor(turn,use_cs=True)[:]
                    factor = tmp_fHt_UAtt_Htt * tmp_fGbn_Ht_SAtt_UAtt * tmp_fUAtt_Ott
                    dialog_factors.append(factor.copy(copy_domain=True))
                
                jfr = JFR(SFR(dialog_factors))
                jfr.condition({'H_bn_0':'x','H_dp_0':'x','H_ap_0':'x','H_tt_0':'x'})
                jfr.calibrate()
                
                for t, turn in enumerate(dialog.abs_turns):
                    rf = jfr.factors_containing_variable('UA_%s'%(t+1))
                    from operator import add
                    if t == 0:
                        for inst in Utils.inst_filling({'H_bn_t':['x'],'H_dp_t':['x'],\
                                                        'H_ap_t':['x'],'H_tt_t':['x'],'UA_tt':lv.UA}):
                            ess[('_factor_%s_%s.model'%(dialog.abs_goal['G_bn'],turn['SA'][0])).replace(':','-')][inst] += \
                            rf[0].copy().marginalise_onto(['UA_1']).normalised()[{'UA_1':inst['UA_tt']}]
                        loglik += math.log(rf[0].copy().z())
                        print 'dialog loglik: %e'%loglik
                    else:  
                        ess[('_factor_%s_%s.model'%(dialog.abs_goal['G_bn'],turn['SA'][0])).replace(':','-')][:] =\
                        map(add,ess[('_factor_%s_%s.model'%(dialog.abs_goal['G_bn'],turn['SA'][0])).replace(':','-')][:],\
                            rf[0].copy().marginalise_onto(['H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,\
                                                           'H_tt_%s'%t,'UA_%s'%(t+1)]).normalised()[:])
                    
            print 'Writing parameters...'
            factor_template = {'G_bn':lv.G_bn,'SA':lv.SA}
            for factor in Utils.inst_filling(factor_template):
                factor = ('_factor_%s_%s.model'%(factor['G_bn'],factor['SA'])).replace(':','-')
                ls.store_model(CPT(ess[factor],child='UA_tt',cpt_force=True),factor)
            
            relgain = ((loglik - prevloglik)/math.fabs(prevloglik))
            print 'prevloglik: %e'%prevloglik
            print 'loglik: %e'%loglik
            print 'relgain: %e'%relgain
        
            if relgain < self.tol:
                break
            
            prevloglik = loglik
            loglik = 0.0
        
        print 'Parameter learning done'    
        
        end_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        
        print 'Start time: %s'%start_time
        print 'End time: %s'%end_time


class LetsgoErrorModelLearner(object):
    def __init__(self,data,prep=False):
        self.data = data
        self.cm_bn = {}
        self.cm_p = {}
        self.cm_tt = {}
        self.cm_ua_template = [{} for c in range(7)]
        self.q_class = {0:0,1:0,2:0,3:0,4:0,5:0,6:0}
        self.co_cs = [{'total':[],'single':[],'bn':[],'dp':[],'ap':[],'tt':[],'yes':[],'no':[],'correction':[],\
                      'multi':[],'multi2':[],'multi3':[],'multi4':[],'multi5':[]} for c in range(7)]
        self.inco_cs = [{'total':[],'single':[],'bn':[],'dp':[],'ap':[],'tt':[],'yes':[],'no':[],'correction':[],\
                      'multi':[],'multi2':[],'multi3':[],'multi4':[],'multi5':[]} for c in range(7)]
        self.prep = prep
    
    def learn(self,make_correction_model=False):
        Variables.clear_default_domain()
        Variables.set_default_domain({'H_bn_t':lv.H_bn,'H_dp_t':lv.H_dp,'H_ap_t':lv.H_ap,\
                                      'H_tt_t':lv.H_tt,'UA_tt':lv.UA,'H_bn_tt':lv.H_bn,\
                                      'H_dp_tt':lv.H_dp,'H_ap_tt':lv.H_ap,'H_tt_tt':lv.H_tt,\
                                      'H_bn_0':lv.H_bn,'H_dp_0':lv.H_dp,'H_ap_0':lv.H_ap,\
                                      'H_tt_0':lv.H_tt})

        fHt_UAtt_Htt = ls.load_model('_factor_Ht_UAtt_Htt.model')

        for d, dialog in enumerate(lc.Corpus(self.data,prep=self.prep).dialogs()):
            if len(dialog.turns) > 40:
                continue
            
            c = ((len(dialog.turns)-1)/5)-1
            if c < 0: c = 0
            self.q_class[c] += 1
            
            cm_ua_template = self.cm_ua_template[c]
            co_cs = self.co_cs[c]
            inco_cs = self.inco_cs[c]
            
#            MAP decoding
#            print 'processing dialog #%d(%s)...'%(d,dialog.id)
            Variables.change_variable('H_bn_0',lv.H_bn)
            Variables.change_variable('H_dp_0',lv.H_dp)
            Variables.change_variable('H_ap_0',lv.H_ap)
            Variables.change_variable('H_tt_0',lv.H_tt)
        
            dialog_factors = []
            for t, turn in enumerate(dialog.abs_turns):
                tmp_fHt_UAtt_Htt = Factor(('H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,'H_tt_%s'%t,\
                                           'UA_%s'%(t+1),'H_bn_%s'%(t+1),'H_dp_%s'%(t+1),\
                                           'H_ap_%s'%(t+1),'H_tt_%s'%(t+1)),
                        new_domain_variables={'UA_%s'%(t+1):lv.UA,'H_bn_%s'%(t+1):lv.H_bn,\
                                              'H_dp_%s'%(t+1):lv.H_dp,'H_ap_%s'%(t+1):lv.H_ap,\
                                              'H_tt_%s'%(t+1):lv.H_tt})
                tmp_fHt_UAtt_Htt[:] = fHt_UAtt_Htt[:]
        #            tmp_fHt_UAtt_Htt = fHt_UAtt_Htt.copy_rename({'H_bn_t':'H_bn_%s'%i,'H_dp_t':'H_dp_%s'%i,'H_ap_t':'H_ap_%s'%i,'H_tt_t':'H_tt_%s'%i,'UA_tt':'UA_%s'%(i+1),'H_bn_tt':'H_bn_%s'%(i+1),'H_dp_tt':'H_dp_%s'%(i+1),'H_ap_tt':'H_ap_%s'%(i+1),'H_tt_tt':'H_tt_%s'%(i+1)})            
                tmp_fGbn_Ht_SAtt_UAtt = Factor(('H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,'H_tt_%s'%t,'UA_%s'%(t+1)))
        #            tmp_fGbn_Ht_SAtt_UAtt = Factor(('H_bn_%s'%i,'H_dp_%s'%i,'H_ap_%s'%i,'H_tt_%s'%i,'UA_%s'%(i+1)),new_domain_variables={'UA_%s'%(i+1):UA,'H_bn_%s'%i:H_bn,'H_dp_%s'%i:H_dp,'H_ap_%s'%i:H_ap,'H_tt_%s'%i:H_tt})
                try:
                    tmp_fGbn_Ht_SAtt_UAtt[:] = \
                    ls.load_model(('_factor_%s_%s.model'%(dialog.abs_goal['G_bn'],turn['SA'][0])).replace(':','-'))[:]
                except:
                    print ('Error:cannot find _factor_%s_%s.model'%(dialog.abs_goal['G_bn'],turn['SA'][0])).replace(':','-')
                    exit()
                tmp_fUAtt_Ott = Factor(('UA_%s'%(t+1),))
                tmp_fUAtt_Ott[:] = lo.getObsFactor(turn,use_cs=True)[:]
                factor = tmp_fHt_UAtt_Htt * tmp_fGbn_Ht_SAtt_UAtt * tmp_fUAtt_Ott
                dialog_factors.append(factor.copy(copy_domain=True))
            
            jfr = JFR(SFR(dialog_factors))
            jfr.condition({'H_bn_0':'x','H_dp_0':'x','H_ap_0':'x','H_tt_0':'x'})
            jfr.map_calibrate()

#            Populate error table using inferred and observed actions
            for t, turn in enumerate(dialog.turns):
                rf = jfr.factors_containing_variable('UA_%s'%(t+1))
                max_ua = max(zip(rf[0].insts(),rf[0][:]),key=operator.itemgetter(1))[0][-1]
                if max_ua == 'yes' and 'no' in turn['UA'] or\
                max_ua == 'no' and 'yes' in turn['UA']:
                    print 'turn %d(%s): '%(t,turn) + max_ua + ' vs.' + ','.join(turn['UA'])
                obs_ua_template = []
                for act in turn['UA']:
                    if act.find('I:bn') == 0:# and max_ua.find('I:bn') > -1 and not dialog.goal['G_bn'] == '':
                        if dialog.goal['G_bn'] == act.split(':')[-1]: obs_ua_template.append('I:bn:o')
                        else: 
                            obs_ua_template.append('I:bn:x')
                            try:
                                self.cm_bn[dialog.goal['G_bn']][act.split(':')[-1]] += 1
                            except:
                                try: self.cm_bn[dialog.goal['G_bn']][act.split(':')[-1]] = 1
                                except: self.cm_bn[dialog.goal['G_bn']] = {act.split(':')[-1]:1}
                    elif act.find('I:dp') == 0:# and max_ua.find('I:dp') > -1 and not dialog.goal['G_dp'] == '':
                        if dialog.goal['G_dp'] == act.split(':')[-1]: obs_ua_template.append('I:dp:o')
                        else: 
                            obs_ua_template.append('I:dp:x')
                            try:
                                self.cm_p[dialog.goal['G_dp']][act.split(':')[-1]] += 1
                            except:
                                try: self.cm_p[dialog.goal['G_dp']][act.split(':')[-1]] = 1
                                except: self.cm_p[dialog.goal['G_dp']] = {act.split(':')[-1]:1}
                    elif act.find('I:ap') == 0:# and max_ua.find('I:ap') > -1 and not dialog.goal['G_ap'] == '':
                        if dialog.goal['G_ap'] == act.split(':')[-1]: obs_ua_template.append('I:ap:o')
                        else: 
                            obs_ua_template.append('I:ap:x')
                            try:
                                self.cm_p[dialog.goal['G_ap']][act.split(':')[-1]] += 1
                            except:
                                try: self.cm_p[dialog.goal['G_ap']][act.split(':')[-1]] = 1
                                except: self.cm_p[dialog.goal['G_ap']] = {act.split(':')[-1]:1}
                    elif act.find('I:tt') == 0:# and max_ua.find('I:tt') > -1 and not dialog.goal['G_tt'] == '':
                        if dialog.goal['G_tt'] == act.split(':')[-1]: obs_ua_template.append('I:tt:o')
                        else: 
                            obs_ua_template.append('I:tt:x')
                            try:
                                self.cm_tt[dialog.goal['G_tt']][act.split(':')[-1]] += 1
                            except:
                                try: self.cm_tt[dialog.goal['G_tt']][act.split(':')[-1]] = 1
                                except: self.cm_tt[dialog.goal['G_tt']] = {act.split(':')[-1]:1}
#                    elif act.find('I:') == 0:
#                        obs_ua_template.append(':'.join(act.split(':')[:-1])) 
                    else:
                        obs_ua_template.append(act)
#                if ','.join(sorted(obs_ua_template)).find('yes,') > -1 or\
#                ','.join(sorted(obs_ua_template)).find(',yes') > -1 or\
#                ','.join(sorted(obs_ua_template)).find('no,') > -1 or\
#                ','.join(sorted(obs_ua_template)).find(',no') > -1:
#                    print 'Check'
#                    print dialog.id
#                    print t
#                    print ','.join(sorted(obs_ua_template))
                
                try:
                    cm_ua_template[max_ua][','.join(sorted(obs_ua_template))] += 1
                except:
                    try: cm_ua_template[max_ua][','.join(sorted(obs_ua_template))] = 1
                    except: cm_ua_template[max_ua] = {','.join(sorted(obs_ua_template)):1}
                
                if len(obs_ua_template) == 1:
                    try:
                        dummy,field,val = obs_ua_template[0].split(':')
                        if val == 'o':
                            co_cs[field].append(turn['CS'])
                        else:
                            inco_cs[field].append(turn['CS'])
                    except:
                        if obs_ua_template[0] == 'yes':
                            if dialog.abs_turns[t]['SA'][0] == 'C:o':
                                co_cs['yes'].append(turn['CS'])
                            elif dialog.abs_turns[t]['SA'][0] == 'C:x':
                                inco_cs['yes'].append(turn['CS'])
                                print 'goal: %s'%dialog.goal
                                print 'turn: %d(%s) of dialog: %s'%(t,turn,dialog.id)
                        elif obs_ua_template[0] == 'no':
                            if dialog.abs_turns[t]['SA'][0] == 'C:x':
                                co_cs['no'].append(turn['CS'])
                            elif dialog.abs_turns[t]['SA'][0] == 'C:o':
                                inco_cs['no'].append(turn['CS'])
                else:
                    try:
                        if make_correction_model and len(obs_ua_template) == 2 and 'no' in obs_ua_template:
                            if ','.join(obs_ua_template).find(':x') > -1:
                                inco_cs['correction'].append(turn['CS'])
                            else:
                                co_cs['correction'%len(obs_ua_template)].append(turn['CS'])
                        else:    
                            if ','.join(obs_ua_template).find(':x') > -1:
                                inco_cs['multi%d'%len(obs_ua_template)].append(turn['CS'])
                            else:
                                co_cs['multi%d'%len(obs_ua_template)].append(turn['CS'])
                    except:
                        print len(obs_ua_template)

        for c in range(7):
            cm_ua_template = self.cm_ua_template[c]
            co_cs = self.co_cs[c]
            inco_cs = self.inco_cs[c]

            co_cs['single'] = co_cs['bn'] + co_cs['dp'] + co_cs['ap'] +\
             co_cs['tt'] + co_cs['yes'] + co_cs['no'] 
            inco_cs['single'] = inco_cs['bn'] + inco_cs['dp'] + inco_cs['ap'] +\
             inco_cs['tt'] + inco_cs['yes'] + inco_cs['no'] 
    
            for n in range(2,6,1):
                co_cs['multi'] += co_cs['multi%d'%n]
                inco_cs['multi'] += inco_cs['multi%d'%n]
    
            co_cs['total'] = co_cs['single'] + co_cs['multi']
            inco_cs['total'] = inco_cs['single'] + inco_cs['multi']
             
        print 'Writing parameters...'
        def make_dist(ft):
            tot = sum(ft.values())
            for k, v in ft.items(): ft[k] = float(v)/tot
            return ft

        def make_dists(cm):
            for key in cm.keys():
                cm[key] = make_dist(cm[key])
            return cm

        def generate_cs_pd(cs):
            cs_pd = {}
            for key in cs.keys():
                cs_pd[key] = {}
                for val in cs[key]:
                    try:
                        cs_pd[key][int(val/0.01)/float(100)] += 1
                    except:
                        cs_pd[key][int(val/0.01)/float(100)] = 1
            return make_dists(cs_pd)
            
        ls.store_model(make_dists(self.cm_bn),'_confusion_matrix_bn.model')
        ls.store_model(make_dists(self.cm_p),'_confusion_matrix_p.model')
        ls.store_model(make_dists(self.cm_tt),'_confusion_matrix_tt.model')
        ls.store_model(make_dist(self.q_class),'_quality_class.model')
        for c in range(7): 
            ls.store_model(make_dists(self.cm_ua_template[c]),'_confusion_matrix_ua_class_%d.model'%c)
            ls.store_model(self.co_cs[c],'_correct_confidence_score_class_%d.model'%c)
            ls.store_model(self.inco_cs[c],'_incorrect_confidence_score_class_%d.model'%c)
            ls.store_model(generate_cs_pd(self.co_cs[c]),'_correct_confidence_score_prob_dist_class_%d.model'%c)
            ls.store_model(generate_cs_pd(self.inco_cs[c]),'_incorrect_confidence_score_prob_dist_class_%d.model'%c)
#        print generate_cs_pd(self.co_cs)['dp']

#        print self.cm_bn
#        print self.cm_p
#        print self.cm_tt
#        print self.cm_ua_template
#
#        