import sys,time,math,operator
from subprocess import *
#import Variables
#from Parameters import Factor
#from Models import SFR, JFR, CPT
#import Utils
import LetsgoCorpus as lc
#import LetsgoSerializer as ls
#import LetsgoVariables as lv
#import LetsgoObservation as lo
import numpy as np

class LetsgoTerminationModelLearner(object):
    
    def __init__(self,data=None,prep=False):
        self.data = data
        self.prep = prep

    def learn(self,method='ME',windowSize=5,exePath='./'):
#        print 'Parameter learning start...'
        start_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

        num_success = 0
        total_length_success = 0
        success_length_dict = {}
        num_fail = 0
        total_length_fail = 0
        fail_length_dict = {}
        num_dialog = 0
        total_length = 0
        total_length_dict = {}
        
        training_file = open('tm_model\\termination_training','w')
        for d, dialog in enumerate(lc.Corpus(self.data,prep=self.prep).dialogs()):
            if len(dialog.turns) > 40:
                continue
            
            if dialog.dialog_result == 'fail':
                num_fail += 1
                total_length_fail += len(dialog.turns)
                try:
                    fail_length_dict[len(dialog.turns)] += 1
                except:
                    fail_length_dict[len(dialog.turns)] = 1
            else:
                num_success += 1
                total_length_success += len(dialog.turns)
                try:
                    success_length_dict[len(dialog.turns)] += 1
                except:
                    success_length_dict[len(dialog.turns)] = 1
            
            num_dialog += 1
            total_length += len(dialog.turns)
            if len(dialog.turns) not in total_length_dict:
                total_length_dict[len(dialog.turns)] = 1
            else:  
                total_length_dict[len(dialog.turns)] += 1
                
#            NIC = 0
#            
#            NICW = 0
#            
#            NTFC_bn = 0
#            NTFCW_bn = 0
#            NTFC_dp = 0
#            NTFCW_dp = 0
#            NTFC_ap = 0
#            NTFCW_ap = 0
#            NTFC_tt = 0
#            NTFCW_tt = 0
#            
#            NV_bn = 0
#            NV_dp = 0
#            NV_ap = 0
#            NV_tt = 0
#            
#            MCS_bn = 0
#            MCS_dp = 0
#            MCS_ap = 0
#            MCS_tt = 0
#            
#            ACSW = 0

            # Incorrect confirmations
            ICs = []
            NONUs = []
            sysFields = []
            valueSetDict = {'bn':set([]),'dp':set([]),'ap':set([]),'tt':set([])}
#            confidenceScores = {'bn':[],'dp':[],'ap':[],'tt':[]}
            confidenceScores = []
            cooperativePairs = []

            for t, turn in enumerate(dialog.turns):
#                print turn
                try:
                    act,field,val = dialog.abs_turns[t]['SA'][0].split(':')
                    if act == 'C' and val == 'x':
                        ICs.append('o')
                    else:
                        ICs.append('x')
                except:
                    ICs.append('x')

                if dialog.abs_turns[t]['UA'][0] == 'non-understanding':
                    turn['CS'] = 0
                    NONUs.append('o')
                else:
                    NONUs.append('x')

                sysFields.append(dialog.abs_turns[t]['SA'][0].split(':')[1])
                
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
                
                
                featureString = ' '.join(features) + '\t' + ('1' if t + 1 == len(dialog.turns) and dialog.dialog_result == 'fail' else '0') + '\n'
#                for idx,feature in enumerate(features):
#                    features[idx] = '%d:%s'%((idx+1),feature.split(':')[1])
#                featureString = ('+1' if t + 1 == len(dialog.turns) and dialog.dialog_result == 'fail' else '-1') + ' ' + ' '.join(features)
    
#                print featureString
                training_file.write(featureString+'\n')

        training_file.close()
        
        print 'Number of successes: %d, avg length: %f'%(num_success,1.0*total_length_success/num_success)
        print success_length_dict
        print 'Number of fails: %d, avg length: %f'%(num_fail,1.0*total_length_fail/num_fail)
        print fail_length_dict
        print 'Number of dialogs: %d, avg length: %f'%(num_dialog,1.0*total_length/num_dialog)
        print total_length_dict
        lengthList = []
        for key in total_length_dict:
            lengthList.extend([key]*total_length_dict[key])
        print 'Dialog length average: %f (+/- %f)'%(np.average(lengthList),np.std(lengthList))
        lengthList = []
        for key in success_length_dict:
            lengthList.extend([key]*success_length_dict[key])
        print 'Success dialog length average: %f (+/- %f)'%(np.average(lengthList),np.std(lengthList))
        lengthList = []
        for key in fail_length_dict:
            lengthList.extend([key]*fail_length_dict[key])
        print 'Fail dialog average: %f (+/- %f)'%(np.average(lengthList),np.std(lengthList))
#        cmdline = './svm-predict test_feature ged.model output'
        cmdline = 'bin\\crf_learn.exe tm_model\\termination_template tm_model\\termination_training tm_model\\termination_model > tm_model\\training_log'
        Popen(cmdline,shell=True,stdout=PIPE).stdout
        
        end_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        
        print 'Start time: %s'%start_time
        print 'End time: %s'%end_time

    def eval(self):
        pass
    
