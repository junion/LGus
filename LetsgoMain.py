
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
    preprocess()
    training()
    goal_table()
#    batch_simulation()

#    interactive_simulation()
    show_cs()
#    show_dialog_len()