import copy,random,ast,traceback,operator
import pprint
import Variables
from Parameters import Factor
from Models import SFR, JFR, CPT
from Samplers import MultinomialSampler
import Utils
import LetsgoCorpus as lc
import LetsgoVariables as lv
import LetsgoObservation as lo
import LetsgoSerializer as ls

class LetsgoSimulationEvaluator(object):
    
    def __init__(self,data=None,prep=False,model='model/_Corpus.model'):
        self.data = data
        self.prep = prep
        self.model = model
        
        self.refActCounts = {'bn':{'correct':0,'incorrect':0},
                             'dp':{'correct':0,'incorrect':0},
                             'ap':{'correct':0,'incorrect':0},
                             'tt':{'correct':0,'incorrect':0},
                             'yes':{'correct':0,'incorrect':0},
                             'no':{'correct':0,'incorrect':0},
                             'non-understanding':0}
        self.refTurnLength = {}
        self.inferActCounts = {'bn':{'correct':0,'incorrect':0},
                             'dp':{'correct':0,'incorrect':0},
                             'ap':{'correct':0,'incorrect':0},
                             'tt':{'correct':0,'incorrect':0},
                             'yes':{'correct':0,'incorrect':0},
                             'no':{'correct':0,'incorrect':0},
                             'non-understanding':0}
        self.inferTurnLength = {}

        self.fHt_UAtt_Htt = ls.load_model('_factor_Ht_UAtt_Htt.model')
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

    def evaluate_fscore(self,abstract=True):
        refNumOfActs = 0
        inferNumOfActs = 0
        posRefNumOfActs = 0
        posInferNumOfActs = 0
        
        simDialogs = ls.load_model('_Simulated_Corpus.model')
        # loop over dialogs
        for d, dialog in enumerate(lc.Corpus(self.data,prep=self.prep,model=self.model).dialogs()):

            if len(dialog.turns) > 40:
                continue
            
            simDialog = simDialogs[d]
            
            # loop over turns
            for t, turn in enumerate(dialog.turns):
                simTurn = simDialog.turns[t]
                
                refNumOfActs += len(turn['UA'])
                inferNumOfActs += len(simTurn['UA'])
                
                if abstract:
                    refAbsActs = map(lambda x:':'.join(x.split(':')[:-1]),turn['UA'])
                    inferAbsActs = map(lambda x:':'.join(x.split(':')[:-1]),simTurn['UA'])
                else:
                    refAbsActs = []
                    for act in turn['UA']:
                        if act.find('I:bn') == 0:
                            if dialog.goal['G_bn'] == act.split(':')[-1]: 
                                refAbsActs.append('I:bn:o')
                            else: 
                                refAbsActs.append('I:bn:x')
                        elif act.find('I:dp') == 0:
                            if dialog.goal['G_dp'] == act.split(':')[-1]: 
                                refAbsActs.append('I:dp:o')
                            else: 
                                refAbsActs.append('I:dp:x')
                        elif act.find('I:ap') == 0:
                            if dialog.goal['G_ap'] == act.split(':')[-1]: 
                                refAbsActs.append('I:ap:o')
                            else: 
                                refAbsActs.append('I:ap:x')
                        elif act.find('I:tt') == 0:
                            if dialog.goal['G_tt'] == act.split(':')[-1]: 
                                refAbsActs.append('I:tt:o')
                            else: 
                                refAbsActs.append('I:tt:x')
                        else:
                            refAbsActs.append(act)
                                
                    inferAbsActs = []
                    for act in simTurn['UA']:
                        if act.find('I:bn') == 0:
                            if dialog.goal['G_bn'] == act.split(':')[-1] or\
                             act.split(':')[-1].startswith('CORRECT_'): 
                                inferAbsActs.append('I:bn:o')
                            else: 
                                inferAbsActs.append('I:bn:x')
                        elif act.find('I:dp') == 0:
                            if dialog.goal['G_dp'] == act.split(':')[-1] or\
                             act.split(':')[-1].startswith('CORRECT_'): 
                                inferAbsActs.append('I:dp:o')
                            else: 
                                inferAbsActs.append('I:dp:x')
                        elif act.find('I:ap') == 0:
                            if dialog.goal['G_ap'] == act.split(':')[-1] or\
                             act.split(':')[-1].startswith('CORRECT_'): 
                                inferAbsActs.append('I:ap:o')
                            else: 
                                inferAbsActs.append('I:ap:x')
                        elif act.find('I:tt') == 0:
                            if dialog.goal['G_tt'] == act.split(':')[-1] or\
                             act.split(':')[-1].startswith('CORRECT_'): 
                                inferAbsActs.append('I:tt:o')
                            else: 
                                inferAbsActs.append('I:tt:x')
                        else:
                            inferAbsActs.append(act)
                
                for act in refAbsActs:
                    if act in inferAbsActs:
                        posRefNumOfActs += 1
                        inferAbsActs.remove(act)
                
                if abstract:
                    refAbsActs = map(lambda x:':'.join(x.split(':')[:-1]),turn['UA'])
                    inferAbsActs = map(lambda x:':'.join(x.split(':')[:-1]),simTurn['UA'])
                else:
                    refAbsActs = []
                    for act in turn['UA']:
                        if act.find('I:bn') == 0:
                            if dialog.goal['G_bn'] == act.split(':')[-1]: 
                                refAbsActs.append('I:bn:o')
                            else: 
                                refAbsActs.append('I:bn:x')
                        elif act.find('I:dp') == 0:
                            if dialog.goal['G_dp'] == act.split(':')[-1]: 
                                refAbsActs.append('I:dp:o')
                            else: 
                                refAbsActs.append('I:dp:x')
                        elif act.find('I:ap') == 0:
                            if dialog.goal['G_ap'] == act.split(':')[-1]: 
                                refAbsActs.append('I:ap:o')
                            else: 
                                refAbsActs.append('I:ap:x')
                        elif act.find('I:tt') == 0:
                            if dialog.goal['G_tt'] == act.split(':')[-1]: 
                                refAbsActs.append('I:tt:o')
                            else: 
                                refAbsActs.append('I:tt:x')
                        else:
                            refAbsActs.append(act)
                                
                    inferAbsActs = []
                    for act in simTurn['UA']:
                        if act.find('I:bn') == 0:
                            if dialog.goal['G_bn'] == act.split(':')[-1] or\
                             act.split(':')[-1].startswith('CORRECT_'): 
                                inferAbsActs.append('I:bn:o')
                            else: 
                                inferAbsActs.append('I:bn:x')
                        elif act.find('I:dp') == 0:
                            if dialog.goal['G_dp'] == act.split(':')[-1] or\
                             act.split(':')[-1].startswith('CORRECT_'): 
                                inferAbsActs.append('I:dp:o')
                            else: 
                                inferAbsActs.append('I:dp:x')
                        elif act.find('I:ap') == 0:
                            if dialog.goal['G_ap'] == act.split(':')[-1] or\
                             act.split(':')[-1].startswith('CORRECT_'): 
                                inferAbsActs.append('I:ap:o')
                            else: 
                                inferAbsActs.append('I:ap:x')
                        elif act.find('I:tt') == 0:
                            if dialog.goal['G_tt'] == act.split(':')[-1] or\
                             act.split(':')[-1].startswith('CORRECT_'): 
                                inferAbsActs.append('I:tt:o')
                            else: 
                                inferAbsActs.append('I:tt:x')
                        else:
                            inferAbsActs.append(act)
                
                for act in inferAbsActs:
                    if act in refAbsActs:
                        posInferNumOfActs += 1
                        refAbsActs.remove(act)
                        
        precision = 1.0*posInferNumOfActs/inferNumOfActs
        recall = 1.0*posRefNumOfActs/refNumOfActs
        fscore = 2*precision*recall/(precision+recall)
        
        print 'Precision: %g'%precision
        print 'Recall: %g'%recall
        print 'F-score: %g'%fscore
        
    def show_conf_score(self,infer=True):
        import numpy as np
        import matplotlib.pyplot as plt
        from copy import deepcopy
        import statistics 
  
        
        co_cs_collection,inco_cs_collection = self.reference_conf_score()
        total_co_cs = None
        total_inco_cs = None
        for c in range(self.q_class_max):
#            co_cs = ls.load_model('_correct_confidence_score_class_%d.model'%c)
#            inco_cs = ls.load_model('_incorrect_confidence_score_class_%d.model'%c)
            co_cs = co_cs_collection[c]
            inco_cs = inco_cs_collection[c]
            
            if total_co_cs == None:
                total_co_cs = deepcopy(co_cs)
                total_inco_cs = deepcopy(inco_cs)
            else:
                for k in co_cs.keys():
                    total_co_cs[k].extend(co_cs[k])
                    total_inco_cs[k].extend(inco_cs[k])
        
        if infer:
            infer_co_cs_collection,infer_inco_cs_collection = self.simulated_conf_score()
            infer_total_co_cs = None
            infer_total_inco_cs = None
            for c in range(self.q_class_max):
    #            co_cs = ls.load_model('_correct_confidence_score_class_%d.model'%c)
    #            inco_cs = ls.load_model('_incorrect_confidence_score_class_%d.model'%c)
                co_cs = infer_co_cs_collection[c]
                inco_cs = infer_inco_cs_collection[c]
                
                if infer_total_co_cs == None:
                    infer_total_co_cs = deepcopy(co_cs)
                    infer_total_inco_cs = deepcopy(inco_cs)
                else:
                    for k in co_cs.keys():
                        infer_total_co_cs[k].extend(co_cs[k])
                        infer_total_inco_cs[k].extend(inco_cs[k])
        
        #    plt.subplot(121)   
        title = {'multi':'Total of multiple actions',\
                 'multi2': 'Two actions',\
                 'multi3': 'Three actions',\
                 'multi4': 'Four actions',\
                 'multi5': 'Five actions',\
                 'total': 'Global',\
                 'yes': 'Affirm',\
                 'no': 'Deny',\
                 'bn': 'Bus number',\
                 'dp': 'Departure place',\
                 'ap': 'Arrival place',\
                 'tt': 'Travel time',\
                 'single': 'Total of single actions'
                 }
        for k in total_co_cs.keys():
            if not k in ['yes','no','bn','dp','ap','tt','multi2','multi3','multi4','multi5']:
                continue
            print k
            co = total_co_cs[k]
            inco = total_inco_cs[k]

            print 'length of correct: ',len(co)
            print 'length of incorrect: ',len(inco)
            
            if len(co) == 0 or len(inco) == 0:
                continue
            
            if len(co) == 1:
                co *= 2
            if len(inco) == 1:
                inco *= 2
            
            if infer:
                infer_co = infer_total_co_cs[k]
                infer_inco = infer_total_inco_cs[k]

                if len(infer_co) == 0 or len(infer_inco) == 0:
                    continue

                if len(infer_co) == 1:
                    infer_co *= 2
                if len(infer_inco) == 1:
                    infer_inco *= 2
            
            
                print 'length of correct: ',len(infer_co)
                print 'length of incorrect: ',len(infer_inco)
            
        
#            try:
            x_co = np.arange(0,1.001,0.001)
            x_inco = np.arange(0,1.001,0.001)
#                h_co = statistics.bandwidth(np.array(co),weight=None,kernel='Gaussian')
#                print 'bandwidth of correct: ',h_co
#            y_co,x_co = statistics.pdf(np.array(co),kernel='Gaussian',n=1000)
            y_co = statistics.pdf(np.array(co),x=x_co,kernel='Gaussian')
#            print 'length of correct: ',len(x_co)
#                h_inco = statistics.bandwidth(np.array(inco),weight=None,kernel='Gaussian')
#                print 'bandwidth of incorrect: ',h_inco
#            y_inco,x_inco = statistics.pdf(np.array(inco),kernel='Gaussian',n=1000)
            y_inco = statistics.pdf(np.array(inco),x=x_inco,kernel='Gaussian')
#            print 'length of incorrect: ',len(x_inco)
            
            y_co += 1e-10
            y_inco = y_inco*(float(len(inco))/len(co)) + 1e-10
    
            y_co_max = np.max(y_co)
            print 'max of correct: ',y_co_max
            y_inco_max = np.max(y_inco)
            print 'max of incorrect: ',y_inco_max
            y_max = max([y_co_max,y_inco_max])
            print 'max of total: ',y_max         
            plt.plot(x_co,y_co/y_max,'g-',alpha=0.75,linewidth=2)
            plt.plot(x_inco,y_inco/y_max,'r-',alpha=0.75,linewidth=2)
            print x_co
            print x_inco
            if infer:
#                    infer_h_co = statistics.bandwidth(np.array(infer_co),weight=None,kernel='Gaussian')
#                    print 'bandwidth of correct: ',infer_h_co
    #            y_co,x_co = statistics.pdf(np.array(co),kernel='Gaussian',n=1000)
                infer_y_co = statistics.pdf(np.array(infer_co),x=x_co,kernel='Gaussian')
#                print 'length of correct: ',len(x_co)
#                    infer_h_inco = statistics.bandwidth(np.array(infer_inco),weight=None,kernel='Gaussian')
#                    print 'bandwidth of incorrect: ',infer_h_inco
    #            y_inco,x_inco = statistics.pdf(np.array(inco),kernel='Gaussian',n=1000)
                infer_y_inco = statistics.pdf(np.array(infer_inco),x=x_inco,kernel='Gaussian')
#                print 'length of incorrect: ',len(x_inco)
                
                infer_y_co += 1e-10
                infer_y_inco = infer_y_inco*(float(len(infer_inco))/len(infer_co)) + 1e-10
        
                infer_y_co_max = np.max(infer_y_co)
                print 'max of correct: ',infer_y_co_max
                infer_y_inco_max = np.max(infer_y_inco)
                print 'max of incorrect: ',infer_y_inco_max
                infer_y_max = max([infer_y_co_max,infer_y_inco_max])
                print 'max of total: ',infer_y_max         
                plt.plot(x_co,infer_y_co/infer_y_max,'g-.',alpha=0.75,linewidth=2)
                plt.plot(x_inco,infer_y_inco/infer_y_max,'r-.',alpha=0.75,linewidth=2)

#                y = y_co/(y_co + y_inco)
#                plt.plot(x_co,y,'b--',alpha=0.75)
#    
#                m = SparseBayes()
#                X = np.atleast_2d(x_co).T
#                Y = np.atleast_2d(y).T
#                basisWidth=min([h_co,h_inco])
#                BASIS = basis_func(X,basisWidth)
#                try:   
#                    Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count = \
#                    m.learn(X,Y,lambda x: basis_func(x,basisWidth))
#                    ls.store_model({'data_points':X[Relevant],'weights':Mu,'basis_width':basisWidth},\
#                                   '_calibrated_confidence_score_sbr_%s.model'%k)
#                except RuntimeError as e:
#                    print e
#                w_infer = np.zeros((BASIS.shape[1],1))
#                w_infer[Relevant] = Mu 
#                
#                Yh = np.dot(BASIS[:,Relevant],Mu)
#                e = Yh - Y
#                ED = np.dot(e.T,e)
#                
#                print 'ED: %f'%ED
#                
#                print np.dot(basis_vector(X[Relevant],np.ones((1,1))/2,basisWidth),Mu)
#                
#                
#                plt.plot(X.ravel(),Yh.ravel(),'yo-',alpha=0.75)

    #        plt.legend(loc='upper center')
            plt.xlabel('Confidence Score')
            plt.ylabel('Density')
            plt.title(title[k])
    #        if k == 'multi5':
    #            plt.axis([0,1,0,1.2])
    #        elif k == 'multi4':
    #            plt.axis([0,1,0,10])
            plt.grid(True)
            plt.savefig('img/'+title[k]+'.png')
#            plt.show()
            plt.clf()
#            except (ValueError,RuntimeError) as e:
#                print e

    def simulated_conf_score(self):
        co_cs_collection = [{'total':[],'single':[],'bn':[],'dp':[],'ap':[],'tt':[],'yes':[],'no':[],'correction':[],\
                      'multi':[],'multi2':[],'multi3':[],'multi4':[],'multi5':[]} for c in range(self.q_class_max)]
        inco_cs_collection = [{'total':[],'single':[],'bn':[],'dp':[],'ap':[],'tt':[],'yes':[],'no':[],'correction':[],\
                      'multi':[],'multi2':[],'multi3':[],'multi4':[],'multi5':[]} for c in range(self.q_class_max)]

        simDialogs = ls.load_model('_Simulated_Corpus.model')
        # loop over dialogs
        for d, dialog in enumerate(simDialogs):
            if len(dialog.turns) > 40:
                continue

#            c = ((len(dialog.turns)-1)/5)-1
#            if c < 0: c = 0
            avg_cs = reduce(operator.add,map(lambda x:x['CS'],dialog.turns))/len(dialog.turns)
            if avg_cs > 0.7: c = 0
            elif avg_cs > 0.5: c = 1
            elif avg_cs > 0.3: c = 2
            else: c = 3

            co_cs = co_cs_collection[c]
            inco_cs = inco_cs_collection[c]
            
#            print 'processing dialog #%d...'%d
            # loop over turns
            for t, turn in enumerate(dialog.turns):
                obs_ua_template = []
                for act in turn['UA']:
                    if act.find('I:bn') == 0:
                        if dialog.goal['G_bn'] == act.split(':')[-1] or\
                         act.split(':')[-1].startswith('CORRECT_'): 
                            obs_ua_template.append('I:bn:o')
                        else: 
                            obs_ua_template.append('I:bn:x')
                    elif act.find('I:dp') == 0:
                        if dialog.goal['G_dp'] == act.split(':')[-1] or\
                         act.split(':')[-1].startswith('CORRECT_'): 
                            obs_ua_template.append('I:dp:o')
                        else: 
                            obs_ua_template.append('I:dp:x')
                    elif act.find('I:ap') == 0:
                        if dialog.goal['G_ap'] == act.split(':')[-1] or\
                         act.split(':')[-1].startswith('CORRECT_'): 
                            obs_ua_template.append('I:ap:o')
                        else: 
                            obs_ua_template.append('I:ap:x')
                    elif act.find('I:tt') == 0:
                        if dialog.goal['G_tt'] == act.split(':')[-1] or\
                         act.split(':')[-1].startswith('CORRECT_'): 
                            obs_ua_template.append('I:tt:o')
                        else: 
                            obs_ua_template.append('I:tt:x')
#                    elif act == 'yes':
#                        if dialog.abs_turns[t]['SA'][0] == 'C:o':
#                            self.inferActCounts['yes']['correct'] += 1
#                        elif dialog.abs_turns[t]['SA'][0] == 'C:x':
#                            self.inferActCounts['yes']['incorrect'] += 1
#                    elif act == 'no':
#                        if dialog.abs_turns[t]['SA'][0] == 'C:x':
#                            self.inferActCounts['no']['correct'] += 1
#                        elif dialog.abs_turns[t]['SA'][0] == 'C:o':
#                            self.inferActCounts['no']['incorrect'] += 1
#                    elif act == 'non-understanding':
#                        self.inferActCounts['non-understanding'] += 1
                    else:
                        obs_ua_template.append(act)
         
                if len(obs_ua_template) == 1:
#                    try:
                    if len(obs_ua_template[0].split(':')) == 3:
                        dummy,field,val = obs_ua_template[0].split(':')
                        if val == 'o':
                            co_cs[field].append(turn['CS'])
                        else:
                            inco_cs[field].append(turn['CS'])
#                    except:
                    else:
                        if obs_ua_template[0] == 'yes':
                            if dialog.abs_turns[t]['SA'][0] == 'C:o':
                                co_cs['yes'].append(turn['CS'])
                            elif dialog.abs_turns[t]['SA'][0] == 'C:x':
                                inco_cs['yes'].append(turn['CS'])
#                                print 'goal: %s'%dialog.goal
#                                print 'turn: %d(%s) of dialog: %s'%(t,turn,dialog.id)
                        elif obs_ua_template[0] == 'no':
                            if dialog.abs_turns[t]['SA'][0] == 'C:x':
                                co_cs['no'].append(turn['CS'])
                            elif dialog.abs_turns[t]['SA'][0] == 'C:o':
                                inco_cs['no'].append(turn['CS'])
                else:
                    try:
#                        if make_correction_model and len(obs_ua_template) == 2 and 'no' in obs_ua_template:
#                            if ','.join(obs_ua_template).find(':x') > -1:
#                                inco_cs['correction'].append(turn['CS'])
#                            else:
#                                co_cs['correction'%len(obs_ua_template)].append(turn['CS'])
#                        else:    
                        if ','.join(obs_ua_template).find(':x') > -1:
                            inco_cs['multi%d'%len(obs_ua_template)].append(turn['CS'])
                        else:
                            co_cs['multi%d'%len(obs_ua_template)].append(turn['CS'])
                    except:
                        print len(obs_ua_template)

        for c in range(self.q_class_max):
            co_cs = co_cs_collection[c]
            inco_cs = inco_cs_collection[c]

            co_cs['single'] = co_cs['bn'] + co_cs['dp'] + co_cs['ap'] +\
             co_cs['tt'] + co_cs['yes'] + co_cs['no'] 
            inco_cs['single'] = inco_cs['bn'] + inco_cs['dp'] + inco_cs['ap'] +\
             inco_cs['tt'] + inco_cs['yes'] + inco_cs['no'] 
    
            for n in range(2,6,1):
                co_cs['multi'] += co_cs['multi%d'%n]
                inco_cs['multi'] += inco_cs['multi%d'%n]
    
            co_cs['total'] = co_cs['single'] + co_cs['multi']
            inco_cs['total'] = inco_cs['single'] + inco_cs['multi']
        
#        pprint.pprint(co_cs_collection)
#        pprint.pprint(inco_cs_collection)
        return co_cs_collection,inco_cs_collection
#        self._show_obs_sbr(co_cs_collection,inco_cs_collection)

    def simulated_stat(self):
        
        simDialogs = ls.load_model('_Simulated_Corpus.model')
        # loop over dialogs
        for d, dialog in enumerate(simDialogs):
#            if d > 30:
#                break
            
            if len(dialog.turns) > 40:
                continue
            
#            print 'processing dialog #%d...'%d
            # loop over turns
            for t, turn in enumerate(dialog.turns):
                if len(turn['UA']) in self.inferTurnLength:
                    self.inferTurnLength[len(turn['UA'])] += 1
                else:
                    self.inferTurnLength[len(turn['UA'])] = 1
                    
                for act in turn['UA']:
                    print act.split(':')[-1]
                    if act.find('I:bn') == 0:
                        if dialog.goal['G_bn'] == act.split(':')[-1] or\
                         act.split(':')[-1].startswith('CORRECT_'): 
                            self.inferActCounts['bn']['correct'] += 1
                        else: 
                            self.inferActCounts['bn']['incorrect'] += 1
                    elif act.find('I:dp') == 0:
                        if dialog.goal['G_dp'] == act.split(':')[-1] or\
                         act.split(':')[-1].startswith('CORRECT_'): 
                            self.inferActCounts['dp']['correct'] += 1
                        else: 
                            self.inferActCounts['dp']['incorrect'] += 1
                    elif act.find('I:ap') == 0:
                        if dialog.goal['G_ap'] == act.split(':')[-1] or\
                         act.split(':')[-1].startswith('CORRECT_'): 
                            self.inferActCounts['ap']['correct'] += 1
                        else: 
                            self.inferActCounts['ap']['incorrect'] += 1
                    elif act.find('I:tt') == 0:
                        if dialog.goal['G_tt'] == act.split(':')[-1] or\
                         act.split(':')[-1].startswith('CORRECT_'): 
                            self.inferActCounts['tt']['correct'] += 1
                        else: 
                            self.inferActCounts['tt']['incorrect'] += 1
                    elif act == 'yes':
                        if dialog.abs_turns[t]['SA'][0] == 'C:o':
                            self.inferActCounts['yes']['correct'] += 1
                        elif dialog.abs_turns[t]['SA'][0] == 'C:x':
                            self.inferActCounts['yes']['incorrect'] += 1
                    elif act == 'no':
                        if dialog.abs_turns[t]['SA'][0] == 'C:x':
                            self.inferActCounts['no']['correct'] += 1
                        elif dialog.abs_turns[t]['SA'][0] == 'C:o':
                            self.inferActCounts['no']['incorrect'] += 1
                    elif act == 'non-understanding':
                        self.inferActCounts['non-understanding'] += 1
                    else:
                        print act
        
        pprint.pprint(self.inferTurnLength)
        pprint.pprint(self.inferActCounts)
 
            
    def simulation(self):
        simDialogs = []
        nonu2other = 0
        actCounts = {'bn':{'correct':0,'incorrect':0,'nogoal_correct':0,'nogoal_incorrect':0},
                             'dp':{'correct':0,'incorrect':0,'nogoal_correct':0,'nogoal_incorrect':0},
                             'ap':{'correct':0,'incorrect':0,'nogoal_correct':0,'nogoal_incorrect':0},
                             'tt':{'correct':0,'incorrect':0,'nogoal_correct':0,'nogoal_incorrect':0},
                             'yes':{'correct':0,'incorrect':0},
                             'no':{'correct':0,'incorrect':0},
                             'non-understanding':0}
        
        # loop over dialogs
        for d, dialog in enumerate(lc.Corpus(self.data,prep=self.prep,model=self.model).dialogs()):
            simDialog = copy.deepcopy(dialog)
            
#            if d > 30:
#                break
            
            if len(dialog.turns) > 40:
                continue
            
            print 'processing dialog #%d...'%d
            
            domain = Variables.Domain()
            domain.clear_domain()
            domain.add_domain_variables(new_domain_variables={'H_bn_t':lv.H_bn,'H_dp_t':lv.H_dp,'H_ap_t':lv.H_ap,\
                                          'H_tt_t':lv.H_tt,'UA_tt':lv.UA,'H_bn_tt':lv.H_bn,\
                                          'H_dp_tt':lv.H_dp,'H_ap_tt':lv.H_ap,'H_tt_tt':lv.H_tt,\
                                          'H_bn_0':lv.H_bn,'H_dp_0':lv.H_dp,'H_ap_0':lv.H_ap,\
                                          'H_tt_0':lv.H_tt})
            dialog_factors = []
            condition = {'H_bn_0':'x','H_dp_0':'x','H_ap_0':'x','H_tt_0':'x'}


#            q_class = ((len(dialog.turns)-1)/5)-1
#            if q_class < 0: q_class = 0
            avg_cs = reduce(operator.add,map(lambda x:x['CS'],dialog.turns))/len(dialog.turns)
            if avg_cs > 0.7: q_class = 0
            elif avg_cs > 0.5: q_class = 1
            elif avg_cs > 0.3: q_class = 2
            else: q_class = 3

            self.c_cm_ua_template = self.cm_ua_template[q_class]
            self.c_co_cs = self.co_cs[q_class]
            self.c_inco_cs = self.inco_cs[q_class]
            
            # loop over turns
            for t, turn in enumerate(dialog.abs_turns):
                # inference on a next user action given the system/user action sequence.
                tmp_fHt_UAtt_Htt = Factor(variables=('H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,'H_tt_%s'%t,\
                                           'UA_%s'%(t+1),'H_bn_%s'%(t+1),'H_dp_%s'%(t+1),\
                                           'H_ap_%s'%(t+1),'H_tt_%s'%(t+1)),\
                                          domain=domain,\
                        new_domain_variables={'UA_%s'%(t+1):lv.UA,'H_bn_%s'%(t+1):lv.H_bn,\
                                              'H_dp_%s'%(t+1):lv.H_dp,'H_ap_%s'%(t+1):lv.H_ap,\
                                              'H_tt_%s'%(t+1):lv.H_tt})
                tmp_fHt_UAtt_Htt[:] = self.fHt_UAtt_Htt[:]
                tmp_fGbn_Ht_SAtt_UAtt = Factor(('H_bn_%s'%t,'H_dp_%s'%t,'H_ap_%s'%t,'H_tt_%s'%t,'UA_%s'%(t+1)),\
                                               domain=domain)
                try:
                    tmp_fGbn_Ht_SAtt_UAtt[:] = \
                    ls.load_model(('_factor_%s_%s.model'%(dialog.abs_goal['G_bn'],dialog.abs_turns[t]['SA'][0])).replace(':','-'))[:]
                except:
                    print ('Error:cannot find _factor_%s_%s.model'%(dialog.abs_goal['G_bn'],dialog.abs_turns[t]['SA'][0])).replace(':','-')
                    exit()

                if t > 0:
                    tmp_fUAtt_Ott = Factor(('UA_%s'%(t),),domain=domain)
                    tmp_fUAtt_Ott[:] = lo.getObsFactor(dialog.abs_turns[t-1],use_cs=True,domain=domain)[:]
                    dialog_factors[-1] *= tmp_fUAtt_Ott

                factor = tmp_fHt_UAtt_Htt * tmp_fGbn_Ht_SAtt_UAtt
                dialog_factors.append(factor.copy())
        
                jfr = JFR(SFR(copy.deepcopy(dialog_factors)))
                jfr.condition(condition)
                jfr.calibrate()
        
                ua = jfr.var_marginal('UA_%s'%(t+1))

                # sample a user action from the posterior
                ua_pt = dict(zip(map(lambda x:x[0],ua.insts()),ua[:]))
                ua_int = MultinomialSampler(ua_pt).sample()
                
                # instanciate the user action
                ua_ins = {}
                for act in ua_int.split(','):
                    if act == 'I:bn': ua_ins['I:bn'] = dialog.goal['G_bn']
                    elif act == 'I:dp': ua_ins['I:dp'] = dialog.goal['G_dp']
                    elif act == 'I:ap': ua_ins['I:ap'] = dialog.goal['G_ap']
                    elif act == 'I:tt': ua_ins['I:tt'] = dialog.goal['G_tt']
                    else: ua_ins[act] = act
                
                # sample from the distribution of error template given the sample user action
                err_ua = []
#                try:
                if ','.join(sorted(ua_ins.keys())) in self.c_cm_ua_template:
                    err_ua_table = self.c_cm_ua_template[','.join(sorted(ua_ins.keys()))]
                    err_ua_templates = MultinomialSampler(err_ua_table).sample().split(',')
#                except KeyError:
                else:
                    no_template_key = ','.join(sorted(ua_ins.keys()))
                    print 'no c_cm_ua_template q_class %d key: '%q_class + ','.join(sorted(ua_ins.keys()))
#                    print traceback.format_exc()
#                    exit()
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
#                    for k, key in enumerate(ua_ins.keys()):
#                        if not ua_ins[key] == '':
#                            err_ua_table = self.c_cm_ua_template[key]
#                            err_ua_templates = MultinomialSampler(err_ua_table).sample().split(',')
#                            break
                
                if len(err_ua_templates) > 1 and 'non-understanding' in err_ua_templates:
                    print 'another action with non-understanding in err_ua_templates'
                    print ua_ins
                    print err_ua_templates
                    print traceback.format_exc()
                    exit()
                if ua_ins == {'non-understanding':'non-understanding'} and err_ua_templates != ['non-understanding']:
                    print 'non-understanding maps to another action'
                    print err_ua_templates
                    nonu2other += 1
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
#                    try:
                        act,field,val = err_ua_template.split(':')
#                        print act, field, val
#                        dialog.goal['G_'+field]
                        if val == 'o' and dialog.goal['G_'+field] != '':
                            err_val = dialog.goal['G_'+field]
                            cs = MultinomialSampler(self.c_co_cs[field]).sample()
                            actCounts[field]['correct'] += 1
                        elif val == 'x' and dialog.goal['G_'+field] != '':
#                            try:  
                            if dialog.goal['G_'+field] in self.cm[field]:  
                                err_val = MultinomialSampler(self.cm[field][dialog.goal['G_'+field]]).sample()
#                            except KeyError: # smoothing confusion matrix for values 
                            else: # smoothing confusion matrix for values 
                                print 'keyerror field: ' + field
                                print 'keyerror goal: ' + dialog.goal['G_'+field]
                                err_val = random.sample(self.val_list[field],1)[0]
                                print 'chose random error #1'
                            cs = MultinomialSampler(self.c_inco_cs[field]).sample()
                            inc_inco = True
                            actCounts[field]['incorrect'] += 1
                        else: # no valid goal value for this field, generate a random value
                            err_val = random.sample(self.val_list[field],1)[0]
                            print 'chose random error #2'
                            cs = MultinomialSampler(self.c_inco_cs[field]).sample()
                            inc_inco = True
                            if val == 'o':
                                actCounts[field]['nogoal_correct'] += 1
                                err_val = 'CORRECT_' + err_val
                            elif val == 'x':
                                actCounts[field]['nogoal_incorrect'] += 1
#                    except ValueError:  # for yes,no,non-understanding
                    else: # for yes,no,non-understanding
                        err_val = err_ua_template
                        if err_val == 'non-understanding':
                            cs = 1.0
                        elif err_val in ['yes','no']:
                            if err_val in ua_ins:
                                if err_val in self.c_co_cs:
                                    cs = MultinomialSampler(self.c_co_cs[err_val]).sample()
                                    if cs == 'OOI':
                                        print 'not available value class %d, key %s'%(q_class,err_val)
                                        cs = MultinomialSampler(self.c_co_cs['single']).sample()
                                else:
                                    print 'not available correct confidence class %d, key %s'%(q_class,err_val)
                                    cs = MultinomialSampler(self.c_co_cs['single']).sample()
                            else:
                                if err_val in self.c_inco_cs:
                                    cs = MultinomialSampler(self.c_inco_cs[err_val]).sample()
                                    if cs == 'OOI':
                                        print 'not available value class %d, key %s'%(q_class,err_val)
                                        cs = MultinomialSampler(self.c_inco_cs['single']).sample()
                                else:
                                    print 'not available incorrect confidence class %d, key %s'%(q_class,err_val)
                                    cs = MultinomialSampler(self.c_inco_cs['single']).sample()
                                inc_inco = True
                        else:
                            print 'unknown action: ' + err_val
                            print traceback.format_exc()
                            exit()
                    err_ua.append(':'.join(err_ua_template.split(':')[:-1]+[err_val]))
#                try:
#                    if len(err_ua) > 1:
#                        if inc_inco:
#                            cs = MultinomialSampler(self.c_inco_cs['multi%d'%len(err_ua)]).sample()
#                        else:
#                            cs = MultinomialSampler(self.c_co_cs['multi%d'%len(err_ua)]).sample()
#                except:
#                    print inc_inco
#                    print len(err_ua)
#                    print traceback.format_exc()
#                    exit()
#                    if inc_inco:
#                        cs = MultinomialSampler(self.c_inco_cs['total']).sample()
#                    else:
#                        cs = MultinomialSampler(self.c_co_cs['total']).sample()

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
                            
                #err_ua,cs
                simDialog.turns[t]['CS'] = cs
                simDialog.turns[t]['UA'] = copy.deepcopy(err_ua)
            simDialogs.append(simDialog)
        print 'nonu2other: %d'%nonu2other
        pprint.pprint(actCounts)
        ls.store_model(simDialogs,'_Simulated_Corpus.model')        

    def reference_conf_score(self):
        co_cs_collection = [{'total':[],'single':[],'bn':[],'dp':[],'ap':[],'tt':[],'yes':[],'no':[],'correction':[],\
                      'multi':[],'multi2':[],'multi3':[],'multi4':[],'multi5':[]} for c in range(self.q_class_max)]
        inco_cs_collection = [{'total':[],'single':[],'bn':[],'dp':[],'ap':[],'tt':[],'yes':[],'no':[],'correction':[],\
                      'multi':[],'multi2':[],'multi3':[],'multi4':[],'multi5':[]} for c in range(self.q_class_max)]

        # loop over dialogs
        for d, dialog in enumerate(lc.Corpus(self.data,prep=self.prep,model=self.model).dialogs()):
            if len(dialog.turns) > 40:
                continue

#            c = ((len(dialog.turns)-1)/5)-1
#            if c < 0: c = 0
            avg_cs = reduce(operator.add,map(lambda x:x['CS'],dialog.turns))/len(dialog.turns)
            if avg_cs > 0.7: c = 0
            elif avg_cs > 0.5: c = 1
            elif avg_cs > 0.3: c = 2
            else: c = 3

            co_cs = co_cs_collection[c]
            inco_cs = inco_cs_collection[c]
            
#            print 'processing dialog #%d...'%d
            # loop over turns
            for t, turn in enumerate(dialog.turns):
                obs_ua_template = []
                for act in turn['UA']:
                    if act.find('I:bn') == 0:
                        if dialog.goal['G_bn'] == act.split(':')[-1]: 
                            obs_ua_template.append('I:bn:o')
                        else: 
                            obs_ua_template.append('I:bn:x')
                    elif act.find('I:dp') == 0:
                        if dialog.goal['G_dp'] == act.split(':')[-1]: 
                            obs_ua_template.append('I:dp:o')
                        else: 
                            obs_ua_template.append('I:dp:x')
                    elif act.find('I:ap') == 0:
                        if dialog.goal['G_ap'] == act.split(':')[-1]: 
                            obs_ua_template.append('I:ap:o')
                        else: 
                            obs_ua_template.append('I:ap:x')
                    elif act.find('I:tt') == 0:
                        if dialog.goal['G_tt'] == act.split(':')[-1]: 
                            obs_ua_template.append('I:tt:o')
                        else: 
                            obs_ua_template.append('I:tt:x')
#                    elif act == 'yes':
#                        if dialog.abs_turns[t]['SA'][0] == 'C:o':
#                            self.inferActCounts['yes']['correct'] += 1
#                        elif dialog.abs_turns[t]['SA'][0] == 'C:x':
#                            self.inferActCounts['yes']['incorrect'] += 1
#                    elif act == 'no':
#                        if dialog.abs_turns[t]['SA'][0] == 'C:x':
#                            self.inferActCounts['no']['correct'] += 1
#                        elif dialog.abs_turns[t]['SA'][0] == 'C:o':
#                            self.inferActCounts['no']['incorrect'] += 1
#                    elif act == 'non-understanding':
#                        self.inferActCounts['non-understanding'] += 1
                    else:
                        obs_ua_template.append(act)
         
                if len(obs_ua_template) == 1:
#                    try:
                    if len(obs_ua_template[0].split(':')) == 3:
                        dummy,field,val = obs_ua_template[0].split(':')
                        if val == 'o':
                            co_cs[field].append(turn['CS'])
                        else:
                            inco_cs[field].append(turn['CS'])
#                    except:
                    else:
                        if obs_ua_template[0] == 'yes':
                            if dialog.abs_turns[t]['SA'][0] == 'C:o':
                                co_cs['yes'].append(turn['CS'])
                            elif dialog.abs_turns[t]['SA'][0] == 'C:x':
                                inco_cs['yes'].append(turn['CS'])
#                                print 'goal: %s'%dialog.goal
#                                print 'turn: %d(%s) of dialog: %s'%(t,turn,dialog.id)
                        elif obs_ua_template[0] == 'no':
                            if dialog.abs_turns[t]['SA'][0] == 'C:x':
                                co_cs['no'].append(turn['CS'])
                            elif dialog.abs_turns[t]['SA'][0] == 'C:o':
                                inco_cs['no'].append(turn['CS'])
                else:
                    try:
#                        if make_correction_model and len(obs_ua_template) == 2 and 'no' in obs_ua_template:
#                            if ','.join(obs_ua_template).find(':x') > -1:
#                                inco_cs['correction'].append(turn['CS'])
#                            else:
#                                co_cs['correction'%len(obs_ua_template)].append(turn['CS'])
#                        else:    
                        if ','.join(obs_ua_template).find(':x') > -1:
                            inco_cs['multi%d'%len(obs_ua_template)].append(turn['CS'])
                        else:
                            co_cs['multi%d'%len(obs_ua_template)].append(turn['CS'])
                    except:
                        print len(obs_ua_template)

        for c in range(self.q_class_max):
            co_cs = co_cs_collection[c]
            inco_cs = inco_cs_collection[c]

            co_cs['single'] = co_cs['bn'] + co_cs['dp'] + co_cs['ap'] +\
             co_cs['tt'] + co_cs['yes'] + co_cs['no'] 
            inco_cs['single'] = inco_cs['bn'] + inco_cs['dp'] + inco_cs['ap'] +\
             inco_cs['tt'] + inco_cs['yes'] + inco_cs['no'] 
    
            for n in range(2,6,1):
                co_cs['multi'] += co_cs['multi%d'%n]
                inco_cs['multi'] += inco_cs['multi%d'%n]
    
            co_cs['total'] = co_cs['single'] + co_cs['multi']
            inco_cs['total'] = inco_cs['single'] + inco_cs['multi']
        
#        pprint.pprint(co_cs_collection)
#        pprint.pprint(inco_cs_collection)
        return co_cs_collection,inco_cs_collection
#        self._show_obs_sbr(co_cs_collection,inco_cs_collection)
                
    def reference_stat(self):
        # loop over dialogs
        for d, dialog in enumerate(lc.Corpus(self.data,prep=self.prep,model=self.model).dialogs()):
            if len(dialog.turns) > 40:
                continue
            
#            print 'processing dialog #%d...'%d
            # loop over turns
            for t, turn in enumerate(dialog.turns):
                if len(turn['UA']) in self.refTurnLength:
                    self.refTurnLength[len(turn['UA'])] += 1
                else:
                    self.refTurnLength[len(turn['UA'])] = 1
                    
                for act in turn['UA']:
                    if act.find('I:bn') == 0:
                        if dialog.goal['G_bn'] == act.split(':')[-1]: 
                            self.refActCounts['bn']['correct'] += 1
                        else: 
                            self.refActCounts['bn']['incorrect'] += 1
                    elif act.find('I:dp') == 0:
                        if dialog.goal['G_dp'] == act.split(':')[-1]: 
                            self.refActCounts['dp']['correct'] += 1
                        else: 
                            self.refActCounts['dp']['incorrect'] += 1
                    elif act.find('I:ap') == 0:
                        if dialog.goal['G_ap'] == act.split(':')[-1]: 
                            self.refActCounts['ap']['correct'] += 1
                        else: 
                            self.refActCounts['ap']['incorrect'] += 1
                    elif act.find('I:tt') == 0:
                        if dialog.goal['G_tt'] == act.split(':')[-1]: 
                            self.refActCounts['tt']['correct'] += 1
                        else: 
                            self.refActCounts['tt']['incorrect'] += 1
                    elif act == 'yes':
                        if dialog.abs_turns[t]['SA'][0] == 'C:o':
                            self.refActCounts['yes']['correct'] += 1
                        elif dialog.abs_turns[t]['SA'][0] == 'C:x':
                            self.refActCounts['yes']['incorrect'] += 1
                    elif act == 'no':
                        if dialog.abs_turns[t]['SA'][0] == 'C:x':
                            self.refActCounts['no']['correct'] += 1
                        elif dialog.abs_turns[t]['SA'][0] == 'C:o':
                            self.refActCounts['no']['incorrect'] += 1
                    elif act == 'non-understanding':
                        self.refActCounts['non-understanding'] += 1
                    else:
                        print act
        
        pprint.pprint(self.refTurnLength)
        pprint.pprint(self.refActCounts)
                
                
            