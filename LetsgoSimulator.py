import os,copy,ast,traceback,random
from subprocess import *
import Variables
from Parameters import Factor
from Models import SFR, JFR
from Samplers import MultinomialSampler
import LetsgoSerializer as ls
import LetsgoVariables as lv
import LetsgoCorpus as lc
from GlobalConfig import GetConfig

config = GetConfig()

class GoalGenerator(object):
    def __init__(self,data=None,init=False,prep=False):
        if init:
            if data == None:
                print 'Error: needs data'
                return
            corpus = lc.Corpus(data,prep=prep)
            self.goal_table = None
            self.goal_table = corpus.goal_table()
            tot = sum(self.goal_table.values())
            for k, v in self.goal_table.items(): self.goal_table[k] = float(v)/tot
            ls.store_model(self.goal_table,'_goal_table.model')
            ls.store_model(corpus.val_list(),'_value_list.model')
        else:
            self.goal_table = ls.load_model('_goal_table.model')
        self.sampler = MultinomialSampler(self.goal_table)
            
    def goal(self):
        goal_str = self.sampler.sample()
        goal = ast.literal_eval(goal_str)
        return goal

    def show_goal_table(self):
        for key,value in sorted(self.goal_table.iteritems(),key=lambda(k,v):(v,k)):
            print "%s: %s" % (key,value)
        
class TerminationSimulator(object):
    def __init__(self):
        pass
    
    def dialog_init(self,goal):
        self.goal = goal
        self.turn_n = 0
        self.turns = []

    def add_turn(self,sys_act,usr_act,cs):
        sys_act = sys_act.replace('G_','')
        self.turns.append({'SA':[sys_act],'UA':usr_act,'CS':cs})
        print self.turns
        
    def is_termination(self):
        if len(self.turns) == 0:
            return False

        windowSize = 5
        ICs = []
        NONUs = []
        sysFields = []
        valueSetDict = {'bn':set([]),'dp':set([]),'ap':set([]),'tt':set([])}
#            confidenceScores = {'bn':[],'dp':[],'ap':[],'tt':[]}
        confidenceScores = []
        cooperativePairs = []
        
        os.unlink('tm_model\\termination_test')
        test_file = open('tm_model\\termination_test','w')
        
        # Incorrect confirmations

        for t, turn in enumerate(self.turns):
#                print turn
            try:
                act,field,val = turn['SA'][0].split(':')
                if act == 'C' and val != self.goal['G_'+field]:
                    ICs.append('o')
                else:
                    ICs.append('x')
            except:
                ICs.append('x')

            if turn['UA'][0] == 'non-understanding':
                turn['CS'] = 0
                NONUs.append('o')
            else:
                NONUs.append('x')

            sysFields.append(turn['SA'][0].split(':')[1])
            
            for usrAction in turn['UA']:
                try:
                    act,field,val = usrAction.split(':')
                    valueSetDict[field].add(val)
                except:
                    pass
            
            confidenceScores.append(turn['CS'])
#                print confidenceScores
            
            if turn['SA'][0].find('C') > -1:
                if set(['yes','no']).isdisjoint(set(turn['UA'])):
                    cooperativePairs.append('x')
                else:
                    cooperativePairs.append('o')
            else:
                field = turn['SA'][0].split(':')[1]
                if filter(lambda x:x.find(field) > -1,turn['UA']) == []:
                    cooperativePairs.append('x')
                else:
                    cooperativePairs.append('o')
                    
            effectiveWindowSize = t + 1 if t + 1 < windowSize else windowSize
            # Number of turns
            features = ['NT:%f'%(1.0*(t+1))]
#                features = ['NT:%f'%(1.0*(t+1 - 13)/10)]
            # Ratio of incorrect confirmations
            features.append('RIC:%f'%(1.0*len(filter(lambda x:x == 'o',ICs))/(t+1)))
            # Ratio of incorrect confirmations over a window
            features.append('RICW:%f'%(1.0*len(filter(lambda x:x == 'o',ICs[-effectiveWindowSize:]))/effectiveWindowSize))
            # Ratio of non-understanding
            features.append('RNONU:%f'%(1.0*len(filter(lambda x:x == 'o',NONUs))/(t+1)))
            # Ratio of non-understanding over a window
            features.append('RNONUW:%f'%(1.0*len(filter(lambda x:x == 'o',NONUs[-effectiveWindowSize:]))/effectiveWindowSize))
            # Ratio of relevant system turns for each concept
            # Ratio of relevant system turns for each concept over a window
            features.append('RRT_bn:%f'%(1.0*len(filter(lambda x:x == 'bn',sysFields))/(t+1)))
            features.append('RRTW_bn:%f'%(1.0*len(filter(lambda x:x == 'bn',sysFields[-effectiveWindowSize:]))/effectiveWindowSize))
            features.append('RRT_dp:%f'%(1.0*len(filter(lambda x:x == 'dp',sysFields))/(t+1)))
            features.append('RRTW_dp:%f'%(1.0*len(filter(lambda x:x == 'dp',sysFields[-effectiveWindowSize:]))/effectiveWindowSize))
            features.append('RRT_ap:%f'%(1.0*len(filter(lambda x:x == 'ap',sysFields))/(t+1)))
            features.append('RRTW_ap:%f'%(1.0*len(filter(lambda x:x == 'ap',sysFields[-effectiveWindowSize:]))/effectiveWindowSize))
            features.append('RRT_tt:%f'%(1.0*len(filter(lambda x:x == 'tt',sysFields))/(t+1)))
            features.append('RRTW_tt:%f'%(1.0*len(filter(lambda x:x == 'tt',sysFields[-effectiveWindowSize:]))/effectiveWindowSize))
            # Number of values mentioned for each concept
            features.append('NV_bn:%d'%(len(valueSetDict['bn'])))
            features.append('NV_dp:%d'%(len(valueSetDict['dp'])))
            features.append('NV_ap:%d'%(len(valueSetDict['ap'])))
            features.append('NV_tt:%d'%(len(valueSetDict['tt'])))
            # Maximum confidence for each concept
#                features.append('MCS_bn:%d'%())
#                features.append('MCS_dp:%d'%())
#                features.append('MCS_ap:%d'%())
#                features.append('MCS_tt:%d'%())
            # Averaged confidence score
            features.append('ACS:%f'%(sum(confidenceScores)/(t+1)))
            # Averaged confidence score over a window
            features.append('ACSW:%f'%(sum(confidenceScores[-effectiveWindowSize:])/effectiveWindowSize))
            # Ratio of cooperative turns
            # Ratio of cooperative turns over a window
            features.append('COP:%f'%(1.0*len(filter(lambda x:x == 'o',cooperativePairs))/(t+1)))
            features.append('COPW:%f'%(1.0*len(filter(lambda x:x == 'o',cooperativePairs[-effectiveWindowSize:]))/effectiveWindowSize))
            
            
            featureString = ' '.join(features) + '\t' + '1' + '\n'

        print featureString
        
        test_file.write(featureString+'\n')
        test_file.flush()
        test_file.close()
        
        cmdline = 'bin\\crf_test.exe -p 1 tm_model\\termination_model tm_model\\termination_test tm_model\\termination_result > tm_model\\test_log'
        child = Popen(cmdline,shell=True,stdout=PIPE)
        child.wait()
        
        result = open('tm_model\\termination_result','r')
        term_prob = float(result.readline())
        line = result.readline()
        print line
        print line.split()[-1]
        if line.split()[-1] == '0':
            term_prob = 1 - term_prob
            
        print term_prob
        
        if random.random() < term_prob:
            print 'Hang up!'
            return True
        else:
            print 'Continue'
            return False
    
class IntentionSimulator(object):
    def __init__(self):
        self.domain = Variables.Domain()
        self.fHt_UAtt_Htt = ls.load_model('_factor_Ht_UAtt_Htt.model')

    def dialog_init(self,goal):
        self.goal = goal
        self.dialog_factors = []
        self.condition = {'H_bn_0':'x','H_dp_0':'x','H_ap_0':'x','H_tt_0':'x'}
        self.turn_n = 0
        self.domain.clear_domain()
        self.domain.add_domain_variables(new_domain_variables={'H_bn_t':lv.H_bn,'H_dp_t':lv.H_dp,'H_ap_t':lv.H_ap,\
                                      'H_tt_t':lv.H_tt,'UA_tt':lv.UA,'H_bn_tt':lv.H_bn,\
                                      'H_dp_tt':lv.H_dp,'H_ap_tt':lv.H_ap,'H_tt_tt':lv.H_tt,\
                                      'H_bn_0':lv.H_bn,'H_dp_0':lv.H_dp,'H_ap_0':lv.H_ap,\
                                      'H_tt_0':lv.H_tt})
#        Variables.clear_default_domain()
#        Variables.set_default_domain({'H_bn_t':lv.H_bn,'H_dp_t':lv.H_dp,'H_ap_t':lv.H_ap,\
#                                      'H_tt_t':lv.H_tt,'UA_tt':lv.UA,'H_bn_tt':lv.H_bn,\
#                                      'H_dp_tt':lv.H_dp,'H_ap_tt':lv.H_ap,'H_tt_tt':lv.H_tt,\
#                                      'H_bn_0':lv.H_bn,'H_dp_0':lv.H_dp,'H_ap_0':lv.H_ap,\
#                                      'H_tt_0':lv.H_tt})
                
    def get_intention(self,sys_act,approx=False):
        print 'get_intention'
        print approx
        t = self.turn_n
        tmp_fHt_UAtt_Htt = Factor(variables=('H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,'H_tt_%s'%t,\
                                   'UA_%s'%(t+1),'H_bn_%s'%(t+1),'H_dp_%s'%(t+1),\
                                   'H_ap_%s'%(t+1),'H_tt_%s'%(t+1)),\
                                  domain=self.domain,\
                new_domain_variables={'UA_%s'%(t+1):lv.UA,'H_bn_%s'%(t+1):lv.H_bn,\
                                      'H_dp_%s'%(t+1):lv.H_dp,'H_ap_%s'%(t+1):lv.H_ap,\
                                      'H_tt_%s'%(t+1):lv.H_tt})
#        tmp_fHt_UAtt_Htt = Factor(('H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,'H_tt_%s'%t,\
#                                   'UA_%s'%(t+1),'H_bn_%s'%(t+1),'H_dp_%s'%(t+1),\
#                                   'H_ap_%s'%(t+1),'H_tt_%s'%(t+1)),\
#                new_domain_variables={'UA_%s'%(t+1):lv.UA,'H_bn_%s'%(t+1):lv.H_bn,\
#                                      'H_dp_%s'%(t+1):lv.H_dp,'H_ap_%s'%(t+1):lv.H_ap,\
#                                      'H_tt_%s'%(t+1):lv.H_tt})
        tmp_fHt_UAtt_Htt[:] = self.fHt_UAtt_Htt[:]
        tmp_fGbn_Ht_SAtt_UAtt = Factor(('H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,'H_tt_%s'%t,'UA_%s'%(t+1)),\
                                       domain=self.domain)
        try:
            tmp_fGbn_Ht_SAtt_UAtt[:] = \
            ls.load_model(('_factor_%s_%s.model'%(self.goal['G_bn'],sys_act)).replace(':','-'))[:]
        except:
            print ('Error:cannot find _factor_%s_%s.model'%(self.goal['G_bn'],sys_act)).replace(':','-')
            exit()
        factor = tmp_fHt_UAtt_Htt * tmp_fGbn_Ht_SAtt_UAtt
        self.dialog_factors.append(factor.copy())

        if approx and t > 1:
            print 'approx'
            self.approx_hist.clear_domain()
            self.dialog_factors[-1].common_domain(self.approx_hist)
            jfr = JFR(SFR(copy.deepcopy([self.approx_hist] + self.dialog_factors[-2:])))
            jfr.condition({'UA_%s'%t:self.condition['UA_%s'%t]})
        else:
            jfr = JFR(SFR(copy.deepcopy(self.dialog_factors)))
            jfr.condition(self.condition)
        jfr.calibrate()

        if approx and t > 0:
            rf = jfr.factors_containing_variable('UA_%s'%t)
            self.approx_hist = copy.deepcopy(rf[0]).marginalise_onto(['H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,\
                                                           'H_tt_%s'%t]).normalised()
#        rf = jfr.factors_containing_variable('UA_%s'%(t+1))
#        print copy.deepcopy(rf[0]).marginalise_onto(['H_bn_%s'%(t+1),'H_dp_%s'%(t+1),'H_ap_%s'%(t+1),\
#                                                           'H_tt_%s'%(t+1)]).normalised()
        ua = jfr.var_marginal('UA_%s'%(t+1))
        ua_pt = dict(zip(map(lambda x:x[0],ua.insts()),ua[:]))
        self.condition['UA_%s'%(t+1)] = [MultinomialSampler(ua_pt).sample()]

        self.turn_n += 1
        return ua_pt,self.condition['UA_%s'%(t+1)]

class ErrorSimulator(object):
    def __init__(self):
        self.val_list = ls.load_model('_value_list.model')
        self.cm = {'bn':ls.load_model('_confusion_matrix_bn.model'),\
                   'dp':ls.load_model('_confusion_matrix_p.model'),\
                   'ap':ls.load_model('_confusion_matrix_p.model'),\
                   'tt':ls.load_model('_confusion_matrix_tt.model')}
        self.cm_ua_template = []
        self.co_cs = []
        self.inco_cs = []
        self.q_class_max = 4
        for c in range(self.q_class_max):
            self.cm_ua_template.append(ls.load_model('_confusion_matrix_ua_class_%d.model'%c))
            self.co_cs.append(ls.load_model('_correct_confidence_score_prob_dist_class_%d.model'%c))
            self.inco_cs.append(ls.load_model('_incorrect_confidence_score_prob_dist_class_%d.model'%c))
        self.q_class_sampler = MultinomialSampler(ls.load_model('_quality_class.model'))
        
    def dialog_init(self,q_class=-1):
        if q_class == -1:
            q_class = self.q_class_sampler.sample()
        print 'Error quality class %d'%q_class
        self.c_cm_ua_template = self.cm_ua_template[q_class]
        self.c_co_cs = self.co_cs[q_class]
        self.c_inco_cs = self.inco_cs[q_class]

    def get_act(self,ua_ins,goal):
        import random
        
#        err_ua = []
#        try:
#            err_ua_table = self.c_cm_ua_template[','.join(sorted(ua_ins.keys()))]
#            err_ua_templates = MultinomialSampler(err_ua_table).sample().split(',')
#        except KeyError:
#            print traceback.format_exc()
#            print 'Error template backup'
#            err_ua_templates = ['non-understanding']
#            for k, key in enumerate(ua_ins.keys()):
#                if not ua_ins[key] == '':
#                    err_ua_table = self.c_cm_ua_template[key]
#                    err_ua_templates = MultinomialSampler(err_ua_table).sample().split(',')
#                    break
#        cs = 0.0;inc_inco = False
#        for err_ua_template in err_ua_templates:
#            try:
#                act,field,val = err_ua_template.split(':')
#                print act, field, val
#                print goal['G_'+field]
#                if val == 'o' and not goal['G_'+field] == '':
#                    err_val = goal['G_'+field]
#                    cs = MultinomialSampler(self.c_co_cs[field]).sample()
#                elif val == 'x' and not goal['G_'+field] == '':
#                    try:  
#                        err_val = MultinomialSampler(self.cm[field][goal['G_'+field]]).sample()
#                    except KeyError:
#                        err_val = random.sample(self.val_list[field],1)[0]
#                        print 'chose random error'
#                    cs = MultinomialSampler(self.c_inco_cs[field]).sample()
#                    inc_inco = True
#                else:
#                    err_val = random.sample(self.val_list[field],1)[0]
#                    print 'chose random error'
#                    cs = MultinomialSampler(self.c_inco_cs[field]).sample()
#                    inc_inco = True
#            except ValueError:
#                print traceback.format_exc()
#                err_val = err_ua_template
#                if err_val in ua_ins and err_val in ['yes','no']:
#                    cs = MultinomialSampler(self.c_co_cs[err_val]).sample()
#                else:
#                    try:
#                        inc_inco = True
#                        cs = MultinomialSampler(self.c_inco_cs[err_val]).sample()
#                    except KeyError,UnboundLocalError:
#                        print traceback.format_exc()
#            err_ua.append(':'.join(err_ua_template.split(':')[:-1]+[err_val]))
#        try:
#            if len(err_ua) > 1:
#                if inc_inco:
#                    cs = MultinomialSampler(self.c_inco_cs['multi%d'%len(err_ua)]).sample()
#                else:
#                    cs = MultinomialSampler(self.c_co_cs['multi%d'%len(err_ua)]).sample()
#        except:
#            print traceback.format_exc()
#            if inc_inco:
#                cs = MultinomialSampler(self.c_inco_cs['total']).sample()
#            else:
#                cs = MultinomialSampler(self.c_co_cs['total']).sample()
                
        err_ua = []
        if ','.join(sorted(ua_ins.keys())) in self.c_cm_ua_template:
            err_ua_table = self.c_cm_ua_template[','.join(sorted(ua_ins.keys()))]
            err_ua_templates = MultinomialSampler(err_ua_table).sample().split(',')
        else:
            no_template_key = ','.join(sorted(ua_ins.keys()))
            print 'no c_cm_ua_template key: ' + ','.join(sorted(ua_ins.keys()))
            print 'Error template backup'
            candidates = ['I:bn','I:tt','I:ap','I:dp']
            random.shuffle(candidates)
            for candidate in candidates:
                if candidate in ua_ins:
                    del ua_ins[candidate]
                    if ','.join(sorted(ua_ins.keys())) in self.c_cm_ua_template:
                        err_ua_table = self.c_cm_ua_template[','.join(sorted(ua_ins.keys()))]
                        err_ua_templates = MultinomialSampler(err_ua_table).sample().split(',')
                        print 'backup from %s to %s'%(no_template_key,','.join(sorted(ua_ins.keys())))
                        break
            else:
                print 'backup fail'
                err_ua_templates = ['non-understanding']
        
        if len(err_ua_templates) > 1 and 'non-understanding' in err_ua_templates:
            print 'another action with non-understanding in err_ua_templates'
            print ua_ins
            print err_ua_templates
            print traceback.format_exc()
            exit()
        if ua_ins == {'non-understanding':'non-understanding'} and err_ua_templates != ['non-understanding']:
            print 'non-understanding maps to another action'
            print err_ua_templates
            err_ua_templates = ['non-understanding']
            
        # realize errors by sampling from a entity-level confusion matrix
        # generate confidence score
        cs = 0.0;inc_inco = False
        print 'err_ua_templates: ' + str(err_ua_templates)
        for err_ua_template in err_ua_templates:
            print 'err_ua_template: ' + str(err_ua_template)
            if not isinstance(err_ua_template,str):
                print 'Invalid type: ' + str(err_ua_template)
                print traceback.format_exc()
                exit()
            if len(err_ua_template.split(':')) == 3:
                act,field,val = err_ua_template.split(':')
                if val == 'o' and goal['G_'+field] != '':
                    err_val = goal['G_'+field]
                    cs = MultinomialSampler(self.c_co_cs[field]).sample()
#                    actCounts[field]['correct'] += 1
                elif val == 'x' and goal['G_'+field] != '':
                    if goal['G_'+field] in self.cm[field]:  
                        err_val = MultinomialSampler(self.cm[field][goal['G_'+field]]).sample()
#                            except KeyError: # smoothing confusion matrix for values 
                    else: # smoothing confusion matrix for values 
                        print 'keyerror field: ' + field
                        print 'keyerror goal: ' + goal['G_'+field]
                        err_val = random.sample(self.val_list[field],1)[0]
                        print 'chose random error #1'
                    cs = MultinomialSampler(self.c_inco_cs[field]).sample()
                    inc_inco = True
#                    actCounts[field]['incorrect'] += 1
                else: # no valid goal value for this field, generate a random value
                    err_val = random.sample(self.val_list[field],1)[0]
                    print 'chose random error #2'
                    cs = MultinomialSampler(self.c_inco_cs[field]).sample()
                    inc_inco = True
                    if val == 'o':
#                        actCounts[field]['nogoal_correct'] += 1
                        err_val = 'CORRECT_' + err_val
                    elif val == 'x':
                        pass
#                        actCounts[field]['nogoal_incorrect'] += 1

            else: # for yes,no,non-understanding
                err_val = err_ua_template
                if err_val == 'non-understanding':
                    cs = 1.0
                elif err_val in ['yes','no']:
                    if err_val in ua_ins:
                        if err_val in self.c_co_cs:
                            cs = MultinomialSampler(self.c_co_cs[err_val]).sample()
                            if cs == 'OOI':
                                print 'not available value key %s'%err_val
                                cs = MultinomialSampler(self.c_co_cs['single']).sample()
                        else:
                            print 'not available correct confidence key %s'%err_val
                            cs = MultinomialSampler(self.c_co_cs['single']).sample()
                    else:
                        if err_val in self.c_inco_cs:
                            cs = MultinomialSampler(self.c_inco_cs[err_val]).sample()
                            if cs == 'OOI':
                                print 'not available value key %s'%err_val
                                cs = MultinomialSampler(self.c_inco_cs['single']).sample()
                        else:
                            print 'not available incorrect confidence key %s'%err_val
                            cs = MultinomialSampler(self.c_inco_cs['single']).sample()
                        inc_inco = True
                else:
                    print 'unknown action: ' + err_val
                    print traceback.format_exc()
                    exit()
            err_ua.append(':'.join(err_ua_template.split(':')[:-1]+[err_val]))

        if len(err_ua) > 1:
            if inc_inco:
                if 'multi%d'%len(err_ua) in self.c_inco_cs:
                    cs = MultinomialSampler(self.c_inco_cs['multi%d'%len(err_ua)]).sample()
                else:
                    cs = MultinomialSampler(self.c_inco_cs['total']).sample()
            else:
                if 'multi%d'%len(err_ua) in self.c_co_cs:
                    cs = MultinomialSampler(self.c_co_cs['multi%d'%len(err_ua)]).sample()
                else:
                    cs = MultinomialSampler(self.c_co_cs['total']).sample()
                
        return err_ua,cs
    
class UserSimulator(object):
    def __init__(self):
        self.goal_gen = GoalGenerator()
        self.term_sim = TerminationSimulator()
        self.int_sim = IntentionSimulator()
        self.err_sim = ErrorSimulator()
        
    def goal_ins2abs(self,goal):
        if goal['G_bn']:
            goal['G_bn'] = 'o'
        else:
            goal['G_bn'] = 'x'
        return goal

    def sys_act_ins2abs(self,sys_act):
        try:
            act,field,value = sys_act.split(':')
            if config.getboolean('UserSimulation','extendedSystemActionSet'):
                if self.goal[field] == value:
                    sys_act = 'C:%s:o'%(field.split('_')[1])
                else:
                    sys_act = 'C:%s:x'%(field.split('_')[1])
            else:
                if self.goal[field] == value:
                    sys_act = 'C:o'
                else:
                    sys_act = 'C:x'
        except ValueError:
            pass
        print sys_act
        return sys_act

    def usr_act_abs2ins(self,usr_act):
        ua_ins = {}
        for act in usr_act[0].split(','):
            if act == 'I:bn': ua_ins['I:bn'] = self.goal['G_bn']
            elif act == 'I:dp': ua_ins['I:dp'] = self.goal['G_dp']
            elif act == 'I:ap': ua_ins['I:ap'] = self.goal['G_ap']
            elif act == 'I:tt': ua_ins['I:tt'] = self.goal['G_tt']
            else: ua_ins[act] = act
        return ua_ins
    
    def dialog_init(self,q_class=-1):
        self.goal = self.goal_gen.goal()
        print self.goal
        self.term_sim.dialog_init(self.goal)
        self.int_sim.dialog_init(self.goal_ins2abs(copy.deepcopy(self.goal)))
        self.err_sim.dialog_init(q_class)
    
    def get_usr_act(self,sys_act,approx=False):
        if self.term_sim.is_termination():
            return ['hangup'],1.0
        ua_pt,ua = self.int_sim.get_intention(self.sys_act_ins2abs(sys_act),approx)
        ua_ins = self.usr_act_abs2ins(ua)
        print ua_ins
        noisy_ua,cs = self.err_sim.get_act(ua_ins,self.goal)
        self.term_sim.add_turn(sys_act,noisy_ua,cs)
        return noisy_ua,cs        
    