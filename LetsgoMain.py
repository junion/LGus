
def preprocess():
    import LetsgoCorpus as lc
    corpus = lc.Corpus('E:/Data/2011/training')
    corpus.preprocess()
#    corpus2 = lc.Corpus('G:/data/LetsGoPublic2/20070616/',prep=True)
#    for dialog in corpus2.dialogs():
#        print dialog.goal,dialog.turns
    
def training():
    import LetsgoLearner as ll

    int_learner = ll.LetsgoIntentionModelLearner('E:/Data/2011/training',prep=True)
    int_learner.learn()
    
    err_learner = ll.LetsgoErrorModelLearner('E:/Data/2011/training',prep=True)
    err_learner.learn()

def batch_simulation():
    import LetsgoCorpus as lc
    import LetsgoSimulator as ls

    corpus = lc.Corpus('E:/Data/2011/training',prep=True)
    simulator = ls.IntentionSimulator()
    
    for dialog in corpus.dialogs():
        simulator.dialog_init(dialog.abs_goal)
        for turn in dialog.abs_turns:
            ua_pt,intention = simulator.get_intention(turn['SA'][0])
            print ua_pt
            print intention

def goal_table():
    import LetsgoSimulator as ls
    
    gg = ls.GoalGenerator(data='E:/Data/2011/training',init=True,prep=True)
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

    corpus = lc.Corpus('E:/Data/2011/training',prep=True)
    
    l = [];avg_cs = []
    for dialog in corpus.dialogs():
        if len(dialog.turns) > 45:
            continue
        l.append(len(dialog.turns))
        avg_cs.append(reduce(operator.add,map(lambda x:x['CS'],dialog.turns))/l[-1])
    (ar,br) = polyfit(l,avg_cs,1)
    csr = polyval([ar,br],l)
    plt.plot(l,avg_cs,'g.',alpha=0.75)
    plt.plot(l,csr,'r.-',alpha=0.75)
    plt.axis([0,50,0,1.0])
    plt.xlabel('Dialog length (turn)')
    plt.ylabel('Confidence score')
    plt.title('Dialog length vs. Confidence score')
    plt.grid(True)
    plt.show()

def show_obs_sbr():
    import numpy as np
    import matplotlib.pyplot as plt
    from copy import deepcopy
    import statistics 
    import LetsgoSerializer as ls
    from SparseBayes import SparseBayes
    from GlobalConfig import InitConfig,GetConfig

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
        
        print len(co)
        print len(inco)
        
#        n,bins,patches = plt.hist([co,inco],bins=np.arange(0.0,1.1,0.1),\
#                                  normed=0,color=['green','yellow'],\
#                                  label=['Correct','Incorrect'],alpha=0.75)
    
        try:
            h_co = statistics.bandwidth(np.array(co),weight=None,kernel='Gaussian')
            print h_co
            y_co,x_co = statistics.pdf(np.array(co),kernel='Gaussian',n=1000)
            print len(x_co)
            h_inco = statistics.bandwidth(np.array(inco),weight=None,kernel='Gaussian')
            print h_inco
            y_inco,x_inco = statistics.pdf(np.array(inco),kernel='Gaussian',n=1000)
            print len(x_inco)
            
            y_co += 1e-10
            y_inco = y_inco*(float(len(inco))/len(co)) + 1e-10
    
            y_co_max = np.max(y_co)
            print y_co_max
            y_inco_max = np.max(y_inco)
            print y_inco_max
            y_max = max([y_co_max,y_inco_max])
            print y_max         
            plt.plot(x_co,y_co/y_max,'g.-',alpha=0.75)
            plt.plot(x_inco,y_inco/y_max,'r.-',alpha=0.75)
            
            y = y_co/(y_co + y_inco)
            plt.plot(x_co,y,'b--',alpha=0.75)

            m = SparseBayes()
            X = np.atleast_2d(x_co).T
            Y = np.atleast_2d(y).T
            basisWidth=max([h_co,h_inco])
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
            plt.show()
        except (ValueError,RuntimeError) as e:
            print e
#            pass



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
      
if __name__ == "__main__":
#    preprocess()
#    training()
#    goal_table()
#    batch_simulation()

#    interactive_simulation()
#    show_cs()
#    show_dialog_len()
    show_obs_sbr()