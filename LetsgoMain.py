from GlobalConfig import InitConfig,GetConfig

InitConfig()
config = GetConfig()
config.read(['LGus.conf'])

def preprocess():
    import LetsgoCorpus as lc
    corpus = lc.Corpus('D:/Data/training')
    corpus.preprocess()
    
#    import tmpCorpus as tc
#    corpus = tc.Corpus('D:/Data/training')
#    corpus.preprocess()
#    corpus2 = lc.Corpus('G:/data/LetsGoPublic2/20070616/',prep=True)
#    for dialog in corpus2.dialogs():
#        print dialog.goal,dialog.turns
    
def intention_model_training():
    import LetsgoLearner as ll

    int_learner = ll.LetsgoIntentionModelLearner('D:/Data/training',method='EM',prep=True)
    int_learner.learn()
    
def error_model_training():
    import LetsgoLearner as ll

    err_learner = ll.LetsgoErrorModelLearner('D:/Data/training',method='Sampling',prep=True)
    err_learner.learn()

def batch_simulation():
    import LetsgoCorpus as lc
    import LetsgoSimulator as ls

    corpus = lc.Corpus('D:/Data/training',prep=True)
    simulator = ls.IntentionSimulator()
    
    for dialog in corpus.dialogs():
        simulator.dialog_init(dialog.abs_goal)
        for turn in dialog.abs_turns:
            ua_pt,intention = simulator.get_intention(turn['SA'][0])
            print ua_pt
            print intention

def goal_table():
    import LetsgoSimulator as ls
    
    gg = ls.GoalGenerator(data='D:/Data/training',init=True,prep=True)
#    gg.show_goal_table()
    print gg.goal()
 
def interactive_simulation():
    import LetsgoSimulator as ls
    
    simulator = ls.UserSimulator()
    simulator.dialog_init()
    
    while True:
        sys_act = raw_input("Enter system action ('q' to quit): ")
        print sys_act
        if sys_act == 'q' or sys_act == 'I:bus': break
        print simulator.get_usr_act(sys_act)

def show_dialog_len():
    import numpy as np
    from scipy import polyfit,polyval
    import matplotlib.pyplot as plt
    import LetsgoCorpus as lc
    import operator

    corpus = lc.Corpus('D:/Data/training',prep=True)
    
    l = [];avg_cs = []
    for dialog in corpus.dialogs():
        if len(dialog.turns) > 40:
            continue
        l.append(len(dialog.turns))
        avg_cs.append(reduce(operator.add,map(lambda x:x['CS'],dialog.turns))/l[-1])
    (ar,br) = polyfit(l,avg_cs,1)
    csr = polyval([ar,br],l)
    plt.plot(l,avg_cs,'g.',alpha=0.75)
    plt.plot(l,csr,'r-',alpha=0.75,linewidth=2)
    plt.axis([0,50,0,1.0])
    plt.xlabel('Dialog length (turn)')
    plt.ylabel('Confidence score')
    plt.title('Dialog length vs. Confidence score')
    plt.grid(True)
    plt.savefig('img/'+'Dialog length vs Confidence score'+'.png')
#    plt.show()
    plt.clf()

def show_obs_sbr():
    import numpy as np
    import matplotlib.pyplot as plt
    from copy import deepcopy
    import statistics 
    import LetsgoSerializer as ls
    from SparseBayes import SparseBayes


    dimension = 1
#    basisWidth = 0.05
#    basisWidth = basisWidth**(1/dimension)
        
    def dist_squared(X,Y):
        import numpy as np
        nx = X.shape[0]
        ny = Y.shape[0]
        
        return np.dot(np.atleast_2d(np.sum((X**2),1)).T,np.ones((1,ny))) + \
            np.dot(np.ones((nx,1)),np.atleast_2d(np.sum((Y**2),1))) - 2*np.dot(X,Y.T);
    
    def basis_func(X,basisWidth):
        import numpy as np
        C = X.copy()
        BASIS = np.exp(-dist_squared(X,C)/(basisWidth**2))
        return BASIS

    def basis_vector(X,x,basisWidth):
        import numpy as np
        BASIS = np.exp(-dist_squared(x,X)/(basisWidth**2))
        return BASIS
    
    total_co_cs = None
    total_inco_cs = None
    for c in range(7):
        co_cs = ls.load_model('_correct_confidence_score_class_%d.model'%c)
        inco_cs = ls.load_model('_incorrect_confidence_score_class_%d.model'%c)

        if total_co_cs == None:
            total_co_cs = deepcopy(co_cs)
            total_inco_cs = deepcopy(inco_cs)
        else:
            for k in co_cs.keys():
                total_co_cs[k].extend(co_cs[k])
                total_inco_cs[k].extend(inco_cs[k])
    
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
        co = total_co_cs[k]
        inco = total_inco_cs[k]
        
        print 'length of correct: ',len(co)
        print 'length of incorrect: ',len(inco)
        
#        n,bins,patches = plt.hist([co,inco],bins=np.arange(0.0,1.1,0.1),\
#                                  normed=0,color=['green','yellow'],\
#                                  label=['Correct','Incorrect'],alpha=0.75)
    
        try:
            x_co = np.arange(0,1.001,0.001)
            x_inco = np.arange(0,1.001,0.001)
            h_co = statistics.bandwidth(np.array(co),weight=None,kernel='Gaussian')
            print 'bandwidth of correct: ',h_co
#            y_co,x_co = statistics.pdf(np.array(co),kernel='Gaussian',n=1000)
            y_co = statistics.pdf(np.array(co),x=x_co,kernel='Gaussian')
            print 'length of correct: ',len(x_co)
            h_inco = statistics.bandwidth(np.array(inco),weight=None,kernel='Gaussian')
            print 'bandwidth of incorrect: ',h_inco
#            y_inco,x_inco = statistics.pdf(np.array(inco),kernel='Gaussian',n=1000)
            y_inco = statistics.pdf(np.array(inco),x=x_inco,kernel='Gaussian')
            print 'length of incorrect: ',len(x_inco)
            
            y_co += 1e-10
            y_inco = y_inco*(float(len(inco))/len(co)) + 1e-10
    
            y_co_max = np.max(y_co)
            print 'max of correct: ',y_co_max
            y_inco_max = np.max(y_inco)
            print 'max of incorrect: ',y_inco_max
            y_max = max([y_co_max,y_inco_max])
            print 'max of total: ',y_max         
            plt.plot(x_co,y_co/y_max,'g.-',alpha=0.75)
            plt.plot(x_inco,y_inco/y_max,'r.-',alpha=0.75)
            print x_co
            print x_inco
            y = y_co/(y_co + y_inco)
            plt.plot(x_co,y,'b--',alpha=0.75)

            m = SparseBayes()
            X = np.atleast_2d(x_co).T
            Y = np.atleast_2d(y).T
            basisWidth=min([h_co,h_inco])
            BASIS = basis_func(X,basisWidth)
            try:   
                Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count = \
                m.learn(X,Y,lambda x: basis_func(x,basisWidth))
                ls.store_model({'data_points':X[Relevant],'weights':Mu,'basis_width':basisWidth},\
                               '_calibrated_confidence_score_sbr_%s.model'%k)
            except RuntimeError as e:
                print e
            w_infer = np.zeros((BASIS.shape[1],1))
            w_infer[Relevant] = Mu 
            
            Yh = np.dot(BASIS[:,Relevant],Mu)
            e = Yh - Y
            ED = np.dot(e.T,e)
            
            print 'ED: %f'%ED
            
            print np.dot(basis_vector(X[Relevant],np.ones((1,1))/2,basisWidth),Mu)
            
            
            plt.plot(X.ravel(),Yh.ravel(),'yo-',alpha=0.75)

    #        plt.legend(loc='upper center')
            plt.xlabel('Confidence Score')
            plt.ylabel('Count')
            plt.title(title[k])
    #        if k == 'multi5':
    #            plt.axis([0,1,0,1.2])
    #        elif k == 'multi4':
    #            plt.axis([0,1,0,10])
            plt.grid(True)
            plt.savefig(title[k]+'.png')
#            plt.show()
            plt.clf()
        except (ValueError,RuntimeError) as e:
            print e

def make_obs_sbr_with_correction():
    import numpy as np
    import matplotlib.pyplot as plt
    from copy import deepcopy
    import statistics 
    import LetsgoSerializer as ls
    from SparseBayes import SparseBayes
    import LetsgoLearner as ll

#    err_learner = ll.LetsgoErrorModelLearner('E:/Data/Recent',prep=True)
#    err_learner.learn(True)


    InitConfig()
    config = GetConfig()
    config.read(['LGus.conf'])


    dimension = 1
#    basisWidth = 0.05
#    basisWidth = basisWidth**(1/dimension)
        
    def dist_squared(X,Y):
        import numpy as np
        nx = X.shape[0]
        ny = Y.shape[0]
        
        return np.dot(np.atleast_2d(np.sum((X**2),1)).T,np.ones((1,ny))) + \
            np.dot(np.ones((nx,1)),np.atleast_2d(np.sum((Y**2),1))) - 2*np.dot(X,Y.T);
    
    def basis_func(X,basisWidth):
        import numpy as np
        C = X.copy()
        BASIS = np.exp(-dist_squared(X,C)/(basisWidth**2))
        return BASIS

    def basis_vector(X,x,basisWidth):
        import numpy as np
        BASIS = np.exp(-dist_squared(x,X)/(basisWidth**2))
        return BASIS
    
    total_co_cs = None
    total_inco_cs = None
    for c in range(7):
        co_cs = ls.load_model('_correct_confidence_score_class_%d.model'%c)
        inco_cs = ls.load_model('_incorrect_confidence_score_class_%d.model'%c)

        if total_co_cs == None:
            total_co_cs = deepcopy(co_cs)
            total_inco_cs = deepcopy(inco_cs)
        else:
            for k in co_cs.keys():
                total_co_cs[k].extend(co_cs[k])
                total_inco_cs[k].extend(inco_cs[k])
    
    #    plt.subplot(121)   
    title = {'multi':'Total of multiple actions',\
             'multi2': 'Two actions',\
             'multi3': 'Three actions',\
             'multi4': 'Four actions',\
             'multi5': 'Five actions',\
             'total': 'Global',\
             'yes': 'Affirm',\
             'no': 'Deny',\
             'correction': 'Correction',\
             'bn': 'Bus number',\
             'dp': 'Departure place',\
             'ap': 'Arrival place',\
             'tt': 'Travel time',\
             'single': 'Total of single actions'
             }
    for k in total_co_cs.keys():
        if not k in ['yes','no','correction','bn','dp','ap','tt','multi2','multi3','multi4','multi5']:
            continue
        co = total_co_cs[k]
        inco = total_inco_cs[k]
        
        print 'length of correct: ',len(co)
        print 'length of incorrect: ',len(inco)
        
#        n,bins,patches = plt.hist([co,inco],bins=np.arange(0.0,1.1,0.1),\
#                                  normed=0,color=['green','yellow'],\
#                                  label=['Correct','Incorrect'],alpha=0.75)
    
        try:
            x_co = np.arange(0,1.001,0.001)
            x_inco = np.arange(0,1.001,0.001)
            h_co = statistics.bandwidth(np.array(co),weight=None,kernel='Gaussian')
            print 'bandwidth of correct: ',h_co
#            y_co,x_co = statistics.pdf(np.array(co),kernel='Gaussian',n=1000)
            y_co = statistics.pdf(np.array(co),x=x_co,kernel='Gaussian')
            print 'length of correct: ',len(x_co)
            h_inco = statistics.bandwidth(np.array(inco),weight=None,kernel='Gaussian')
            print 'bandwidth of incorrect: ',h_inco
#            y_inco,x_inco = statistics.pdf(np.array(inco),kernel='Gaussian',n=1000)
            y_inco = statistics.pdf(np.array(inco),x=x_inco,kernel='Gaussian')
            print 'length of incorrect: ',len(x_inco)
            
            y_co += 1e-10
            y_inco = y_inco*(float(len(inco))/len(co)) + 1e-10
    
            y_co_max = np.max(y_co)
            print 'max of correct: ',y_co_max
            y_inco_max = np.max(y_inco)
            print 'max of incorrect: ',y_inco_max
            y_max = max([y_co_max,y_inco_max])
            print 'max of total: ',y_max         
            plt.plot(x_co,y_co/y_max,'g.-',alpha=0.75)
            plt.plot(x_inco,y_inco/y_max,'r.-',alpha=0.75)
            print x_co
            print x_inco
            y = y_co/(y_co + y_inco)
            plt.plot(x_co,y,'b--',alpha=0.75)

            m = SparseBayes()
            X = np.atleast_2d(x_co).T
            Y = np.atleast_2d(y).T
            basisWidth=min([h_co,h_inco])
            BASIS = basis_func(X,basisWidth)
            try:   
                Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count = \
                m.learn(X,Y,lambda x: basis_func(x,basisWidth))
                ls.store_model({'data_points':X[Relevant],'weights':Mu,'basis_width':basisWidth},\
                               '_calibrated_confidence_score_sbr_%s.model'%k)
            except RuntimeError as e:
                print e
            w_infer = np.zeros((BASIS.shape[1],1))
            w_infer[Relevant] = Mu 
            
            Yh = np.dot(BASIS[:,Relevant],Mu)
            e = Yh - Y
            ED = np.dot(e.T,e)
            
            print 'ED: %f'%ED
            
            print np.dot(basis_vector(X[Relevant],np.ones((1,1))/2,basisWidth),Mu)
            
            
            plt.plot(X.ravel(),Yh.ravel(),'yo-',alpha=0.75)

    #        plt.legend(loc='upper center')
            plt.xlabel('Confidence Score')
            plt.ylabel('Count')
            plt.title(title[k])
    #        if k == 'multi5':
    #            plt.axis([0,1,0,1.2])
    #        elif k == 'multi4':
    #            plt.axis([0,1,0,10])
            plt.grid(True)
            plt.savefig(title[k]+'.png')
#            plt.show()
            plt.clf()
        except (ValueError,RuntimeError) as e:
            print e

def show_cs():
    import numpy as np
    import matplotlib.pyplot as plt
    import LetsgoSerializer as ls

    for c in range(7):
        co_cs = ls.load_model('_correct_confidence_score_class_%d.model'%c)
        inco_cs = ls.load_model('_incorrect_confidence_score_class_%d.model'%c)
    
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
        for k in co_cs.keys():
            co = co_cs[k]
            inco = inco_cs[k]
            
            n,bins,patches = plt.hist([co,inco],bins=np.arange(0.0,1.1,0.1),\
                                      normed=False,color=['green','yellow'],\
                                      label=['Correct','Incorrect'],alpha=0.75)
        
            plt.legend(loc='upper center')
            plt.xlabel('Confidence Score')
            plt.ylabel('Count')
            plt.title(title[k])
            if k == 'multi5':
                plt.axis([0,1,0,1.2])
            elif k == 'multi4':
                plt.axis([0,1,0,10])
            plt.grid(True)
            plt.show()

def extract_usr_model():
    import Variables
    from Parameters import Factor
    import LetsgoCorpus as lc
    import LetsgoSerializer as ls
    import LetsgoVariables as lv
    
    Variables.clear_default_domain()
    Variables.set_default_domain({'H_bn_t':lv.H_bn,'H_dp_t':lv.H_dp,'H_ap_t':lv.H_ap,\
                                  'H_tt_t':lv.H_tt,'UA_tt':lv.UA,'H_bn_tt':lv.H_bn,\
                                  'H_dp_tt':lv.H_dp,'H_ap_tt':lv.H_ap,'H_tt_tt':lv.H_tt})

    # estimate the ratio of dialogs w/ bn and dialogs w/o bn in the goal
    #
     
    try:
        fGbnO_Ht_SAttCO_UAtt = ls.load_model('_factor_o_C-o.model').marginalise_onto(['UA_tt']).normalised()
        fGbnX_Ht_SAttCO_UAtt = ls.load_model('_factor_x_C-o.model').marginalise_onto(['UA_tt']).normalised()
        fGbn_Ht_SAttCO_UAtt = (fGbnO_Ht_SAttCO_UAtt + fGbnX_Ht_SAttCO_UAtt).normalised()
    except:
        print ('Error:cannot find model')
        exit()

    try:
        fGbnO_Ht_SAttCX_UAtt = ls.load_model('_factor_o_C-x.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnO_Ht_SAtt_UAttX
        fGbnX_Ht_SAttCX_UAtt = ls.load_model('_factor_x_C-x.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnX_Ht_SAtt_UAttX
        fGbn_Ht_SAttCX_UAtt = (fGbnO_Ht_SAttCX_UAtt + fGbnX_Ht_SAttCX_UAtt).normalised()
#        print fGbn_Ht_SAtt_UAttX
    except:
        print ('Error:cannot find model')
        exit()

    try:
        fGbnO_Ht_SAttBN_UAtt = ls.load_model('_factor_o_R-bn.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnO_Ht_SAttBN_UAtt
        fGbnX_Ht_SAttBN_UAtt = ls.load_model('_factor_x_R-bn.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnX_Ht_SAttBN_UAtt
        fGbn_Ht_SAttBN_UAtt = (fGbnO_Ht_SAttBN_UAtt + fGbnX_Ht_SAttBN_UAtt).normalised()
#        print fGbn_Ht_SAttBN_UAtt
    except:
        print ('Error:cannot find model')
        exit()

    try:
        fGbnO_Ht_SAttDP_UAtt = ls.load_model('_factor_o_R-dp.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnO_Ht_SAttDP_UAtt
        fGbnX_Ht_SAttDP_UAtt = ls.load_model('_factor_x_R-dp.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnX_Ht_SAttDP_UAtt
        fGbn_Ht_SAttDP_UAtt = (fGbnO_Ht_SAttDP_UAtt + fGbnX_Ht_SAttDP_UAtt).normalised()
#        print fGbn_Ht_SAttDP_UAtt
    except:
        print ('Error:cannot find model')
        exit()

    try:
        fGbnO_Ht_SAttAP_UAtt = ls.load_model('_factor_o_R-ap.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnO_Ht_SAttAP_UAtt
        fGbnX_Ht_SAttAP_UAtt = ls.load_model('_factor_x_R-ap.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnX_Ht_SAttAP_UAtt
        fGbn_Ht_SAttAP_UAtt = (fGbnO_Ht_SAttAP_UAtt + fGbnX_Ht_SAttAP_UAtt).normalised()
#        print fGbn_Ht_SAttAP_UAtt
    except:
        print ('Error:cannot find model')
        exit()

    try:
        fGbnO_Ht_SAttTT_UAtt = ls.load_model('_factor_o_R-tt.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnO_Ht_SAttTT_UAtt
        fGbnX_Ht_SAttTT_UAtt = ls.load_model('_factor_x_R-tt.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnX_Ht_SAttTT_UAtt
        fGbn_Ht_SAttTT_UAtt = (fGbnO_Ht_SAttTT_UAtt + fGbnX_Ht_SAttTT_UAtt).normalised()
#        print fGbn_Ht_SAttTT_UAtt
    except:
        print ('Error:cannot find model')
        exit()

    try:
        fGbnO_Ht_SAttOP_UAtt = ls.load_model('_factor_o_R-open.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnO_Ht_SAttOP_UAtt
        fGbnX_Ht_SAttOP_UAtt = ls.load_model('_factor_x_R-open.model').marginalise_onto(['UA_tt']).normalised()
#        print fGbnX_Ht_SAttOP_UAtt
        fGbn_Ht_SAttOP_UAtt = (fGbnO_Ht_SAttOP_UAtt + fGbnX_Ht_SAttOP_UAtt).normalised()
#        print fGbn_Ht_SAttOP_UAtt
    except:
        print ('Error:cannot find model')
        exit()

    um = {}
    um['C-o'] = fGbn_Ht_SAttCO_UAtt.insts_data_dict()
    um['C-x'] = fGbn_Ht_SAttCX_UAtt.insts_data_dict()
    um['R-bn'] = fGbn_Ht_SAttBN_UAtt.insts_data_dict()
    um['R-dp'] = fGbn_Ht_SAttDP_UAtt.insts_data_dict()
    um['R-ap'] = fGbn_Ht_SAttAP_UAtt.insts_data_dict()
    um['R-tt'] = fGbn_Ht_SAttTT_UAtt.insts_data_dict()
    um['R-open'] = fGbn_Ht_SAttOP_UAtt.insts_data_dict()
    
    print um
    
    print 'Writing parameters...'
        
    ls.store_model(um,'_user_action.model')
    
    print 'Done'

def corpus_stats():
    import LetsgoSimEval as lse

    evaluator = lse.LetsgoSimulationEvaluator('D:/Data/training',prep=True)
    evaluator.reference_stat()
    evaluator.show_conf_score(infer=False)

def sim_eval():
    import LetsgoSimEval as lse

    evaluator = lse.LetsgoSimulationEvaluator('D:/Data/training',prep=True)
#    evaluator.simulation()
#    evaluator.simulated_stat()
    evaluator.show_conf_score()
#    evaluator.evaluate_fscore()
#    evaluator.evaluate_fscore(False)
        
def termination_model_training():
    import LetsgoTerminationModel as lt
    
    learner = lt.LetsgoTerminationModelLearner('D:/Data/training',prep=True)
    learner.learn()

def test_preprocess():
    import LetsgoCorpus as lc
    corpus = lc.Corpus('D:/Data/test',model='model/_Test_Corpus.model')
    corpus.preprocess()

def test_corpus_stats():
    import LetsgoSimEval as lse

    evaluator = lse.LetsgoSimulationEvaluator('D:/Data/test',prep=True,model='model/_Test_Corpus.model')
    evaluator.reference_stat()
    evaluator.show_conf_score(infer=False)

def test_sim_eval():
    import LetsgoSimEval as lse

    evaluator = lse.LetsgoSimulationEvaluator('D:/Data/test',prep=True,model='model/_Test_Corpus.model',second_model='model/Simulated_Test_Corpus.model')
    evaluator.simulation()
#    evaluator.simulated_stat()
#    evaluator.show_conf_score()
#    evaluator.evaluate_fscore()
#    evaluator.evaluate_fscore(False)

#def show_paired_conf_score ():
#    import LetsgoSimEval as lse
#    import matplotlib.pyplot as p
#
#    fig = p.figure(figsize=(8,6*1.3))
#
#    ax = fig.add_subplot(2,1,1)
#    evaluator = lse.LetsgoSimulationEvaluator('D:/Data/training',prep=True)
#    evaluator.get_conf_score_figure(ax,field='total')
#    ax.legend(loc='upper left')
#    ax.set_ylabel('Density')
#    p.grid(True)
#
#    ax2 = fig.add_subplot(2,1,2)
#    evaluator = lse.LetsgoSimulationEvaluator('D:/Data/test',prep=True,model='model/_Test_Corpus.model')
#    evaluator.get_conf_score_figure(ax2,'_Simulated_Test_Corpus.model',field='total')
#    ax2.set_xlabel('Confidence Score')
#    ax2.set_ylabel('Density')
#    ax2.legend(loc='upper left')
#    p.grid(True)
#
#    p.savefig('img/cs.png')
#    p.clf()

def show_paired_conf_score ():
    import LetsgoSimEval as lse
    import matplotlib.pyplot as p
    import matplotlib.font_manager as fm
    
#    evaluator = lse.LetsgoSimulationEvaluator('D:/Data/training',prep=True)
#    fig = p.figure(figsize=(13,6*1.3))
#    ax = fig.add_subplot(2,3,1)
#    evaluator.get_conf_score_figure(ax,field='yes')
#    prop = fm.FontProperties(size=12)
#    ax.legend(loc='upper left',prop=prop)    
#    ax.set_ylabel('Density')
#    ax.set_xlabel('Affirm')
#    p.grid(True)
#    ax2 = fig.add_subplot(2,3,2)
#    evaluator.get_conf_score_figure(ax2,field='no')
#    ax2.set_xlabel('Deny')
#    p.grid(True)
#    ax3 = fig.add_subplot(2,3,3)
#    evaluator.get_conf_score_figure(ax3,field='bn')
#    ax3.set_xlabel('Route')
#    p.grid(True)
#    ax4 = fig.add_subplot(2,3,4)
#    evaluator.get_conf_score_figure(ax4,field='dp')
#    ax4.set_ylabel('Density')
#    ax4.set_xlabel('Source')
#    p.grid(True)
#    ax5 = fig.add_subplot(2,3,5)
#    evaluator.get_conf_score_figure(ax5,field='ap')
#    ax5.set_xlabel('Destination')
#    p.grid(True)
#    ax6 = fig.add_subplot(2,3,6)
#    evaluator.get_conf_score_figure(ax6,field='tt')
#    ax6.set_xlabel('Time')
#    p.grid(True)
#
#    p.savefig('img/train_cs_concept.png')
#    p.clf()
#    
    fig = p.figure(figsize=(13,6*1.3))
    ax = fig.add_subplot(2,3,1)
    evaluator = lse.LetsgoSimulationEvaluator('D:/Data/test',prep=True,model='model/_Test_Corpus.model',second_model='model/_Simulated_Test_Corpus.model')
    evaluator.get_conf_score_figure(ax,field='yes')
    prop = fm.FontProperties(size=12)
    ax.legend(loc='upper left',prop=prop)    
    ax.set_ylabel('Density')
    ax.set_xlabel('Affirm')
    p.grid(True)
    ax2 = fig.add_subplot(2,3,2)
    evaluator.get_conf_score_figure(ax2,field='no')
    ax2.set_xlabel('Deny')
    p.grid(True)
    ax3 = fig.add_subplot(2,3,3)
    evaluator.get_conf_score_figure(ax3,field='bn')
    ax3.set_xlabel('Route')
    p.grid(True)
    ax4 = fig.add_subplot(2,3,4)
    evaluator.get_conf_score_figure(ax4,field='dp')
    ax4.set_ylabel('Density')
    ax4.set_xlabel('Source')
    p.grid(True)
    ax5 = fig.add_subplot(2,3,5)
    evaluator.get_conf_score_figure(ax5,field='ap')
    ax5.set_xlabel('Destination')
    p.grid(True)
    ax6 = fig.add_subplot(2,3,6)
    evaluator.get_conf_score_figure(ax6,field='tt')
    ax6.set_xlabel('Time')
    p.grid(True)

    p.savefig('img/test_cs_concept.png')
    p.clf()

    
if __name__ == "__main__":
#    preprocess()
#    corpus_stats()
#    goal_table()
#    intention_model_training()
#    error_model_training()
#    sim_eval()
#    termination_model_training()

#    test_preprocess()
#    test_corpus_stats()
#    test_sim_eval()

    show_paired_conf_score()


#    show_obs_sbr()
#    extract_usr_model()
#    make_obs_sbr_with_correction()
#    show_dialog_len()
#    batch_simulation()
#    interactive_simulation()
#    show_cs()
