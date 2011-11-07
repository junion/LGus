
import os,copy

class Dialog:
    '''
    Class Dialog
    @param filename: string argument
    '''
    def __init__(self,filename,max_turn_num=40):
        self.id = filename
        self.goal = {'G_bn':'','G_dp':'','G_ap':'','G_tt':''}
        self.turns = []
        self.dialog_failure = True
        self.max_turn_num = max_turn_num
        
        try:
            file = open(filename,'r')
        except:
            print 'File open error: %s'%filename
            return None
        look_for_value = 'wait'
        look_for_goal = 'wait'
        look_for_ua = 'wait'
        potential_field = 'none'
        for line in file:
            line = line.strip()
#            print line
#            '''
#            Turn extraction
#            '''
            if line.find('Success') > -1 and line.find('Departure') > -1:
                potential_field = 'dp'
            elif line.find('Success') > -1 and line.find('Arrival') > -1:
                potential_field = 'ap'
            elif line.find('{request how_may_i_help_you}') == 0:
                turn = {'SA':['R:open']}
#                print line
            elif line.find('{request query.route') == 0 or \
            line.find('{request query.line') == 0:
                turn = {'SA':['R:bn']}
#                print line
            elif line.find('{request query.departure_place') == 0 or\
            line.find('{request departure_neighborhood') == 0 or\
            line.find('{request departure_stop_in_neighborhood') == 0:
                turn = {'SA':['R:dp']}
#                print line
            elif line.find('{request query.arrival_place') == 0 or\
            line.find('{request arrival_neighborhood') == 0 or\
            line.find('{request arrival_stop_in_neighborhood') == 0:
                turn = {'SA':['R:ap']}
#                print line
            elif line.find('{request query.travel_time') == 0 or\
            line.find('{request query.exact_travel_time') == 0:
                turn = {'SA':['R:tt']}
#                print line
            elif line.find('{explicit_confirm') == 0:
                if line.find('route') > -1:
                    turn = {'SA':['C:bn:%s'%line.split('"')[1]]}
#                    print line
                elif line.find('departure_place') > -1:
                    look_for_value = 'dp'
                elif line.find('arrival_place') > -1:
                    look_for_value = 'ap'
                elif line.find('neighborhood') > -1:
                    look_for_value = potential_field
                    potential_field = 'none'
                elif line.find('travel_time') > -1:
                    look_for_value = 'tt'
            elif look_for_value in ['dp','ap'] and line.find('name') == 0:
                turn = {'SA':['C:%s:%s'%(look_for_value,line.split('\t')[1])]}
                look_for_value = 'wait'
#                print line
            elif look_for_value == 'tt' and line.find('value') == 0:
                turn = {'SA':['C:tt:%s'%line.split('\t')[1]]}
#                print line
            elif look_for_value == 'tt' and line.find('now') == 0 and line.split('\t')[1] == 'true':
                turn = {'SA':['C:tt:now']}
#                print line
            elif look_for_value == 'tt' and line.find('}') == 0:
                look_for_value = 'wait'
#                print line
            elif line.find('New user input') > -1:
                look_for_ua = 'begin'
                try:
                    turn['UA'] = []
                except:
                    turn = {'SA':['O:-'],'UA':[]}
#                print turn
            elif line.find('[h4_confidence]') > -1 or line.find('[confidence]') > -1:
                turn['CS'] = float(line.split('=')[1])
            elif not look_for_ua == 'wait' and line.find('Last turn: non-understanding') > -1:                
                turn['UA'] = ['non-understanding']
                look_for_ua = 'wait'
#                print line
            elif not look_for_ua == 'wait' and line.find('name') == 0 and line.find('|') < 0:
#                print line
                place = line.split('\t')[1]
            elif not look_for_ua == 'wait' and line.find('value') == 0:
#                print line
                time = line.split('\t')[1]
            elif not look_for_ua == 'wait' and line.find('now') == 0 and line.split('\t')[1] == 'true':
#                print line
                time = 'now'
#            elif not look_for_ua == 'wait' and line.find('period_spec') == 0:
#                print line                
#                try:
#                    if not time == 'now':
#                        time += line.split('\t')[1]
#                except:
#                    pass
            elif not look_for_ua == 'wait' and line.find('bound to concept') > -1:                
                if line.find('[yes]') > -1:
                    turn['UA'].append('yes')
#                    print line
                elif line.find('[no]') > -1:
                    turn['UA'].append('no')
#                    print line
                elif line.find('route') > -1:
#                    turn['UA'].append('I:bn')
                    turn['UA'].append('I:bn:%s'%line.split('(')[2].split('|')[0])
#                    print line
                elif line.find('DeparturePlace') > -1:
#                    turn['UA'].append('I:dp')
                    try:
                        if not place == '':
                            turn['UA'].append('I:dp:%s'%place);place = ''
                    except:
                        pass
#                    print line
                elif line.find('ArrivalPlace') > -1:
#                    turn['UA'].append('I:ap')
                    try:
                        if not place == '':
                            turn['UA'].append('I:ap:%s'%place);place = ''
                    except:
                        pass
#                    print line
                elif line.find('TravelTime') > -1:
#                    turn['UA'].append('I:tt')
                    try:
                        if not time == '':
                            turn['UA'].append('I:tt:%s'%time);time = ''
                    except:
                        pass
#                    print line
            elif not look_for_ua == 'wait' and line.find('Concepts Binding Phase completed') > -1:
#                print line
                if turn['UA'] == []:
                    turn['UA'] = ['non-understanding']
#                print turn['UA']
                self.turns.append(copy.deepcopy(turn)); del turn
                look_for_ua = 'wait'
#            '''
#            Goal extraction
#            '''
            elif line.find('Executing dialog agent /LetsGoPublic/PerformTask/ProcessQuery/ExecuteBackendCall') > -1:
                look_for_goal = 'begin'
            elif not look_for_goal == 'wait' and line.find('route_number') > -1:
                self.goal['G_bn'] = line.split('\t')[1]
#                print line
#                print self.goal
            elif not look_for_goal == 'wait' and line.find('departure_place') > -1:
                look_for_goal = 'dp'
            elif not look_for_goal == 'wait' and line.find('arrival_place') > -1:
                look_for_goal = 'ap'
            elif not look_for_goal == 'wait' and line.find('travel_time') > -1:
                look_for_goal = 'tt'
            elif not look_for_goal == 'wait' and line.find('departure_stops') > -1:
                look_for_goal = 'dp'
            elif not look_for_goal == 'wait' and line.find('arrival_stops') > -1:
                look_for_goal = 'ap'
            elif look_for_goal == 'dp' and line.find('name') == 0 and self.goal['G_dp'] == '':
                self.goal['G_dp'] = line.split('\t')[1]
#                print line
#                print self.goal
            elif look_for_goal == 'ap' and line.find('name') == 0 and self.goal['G_ap'] == '':
                self.goal['G_ap'] = line.split('\t')[1]
#                print line
#                print self.goal
            elif look_for_goal == 'tt' and line.find('now') == 0:
                if line.split('\t')[1] == 'true':
                    self.goal['G_tt'] = 'now'
#                print line
#                print self.goal
            elif look_for_goal == 'tt' and line.find('value') == 0:# and not self.goal['G_tt'] == 'now':
                self.goal['G_tt'] += line.split('\t')[1]
#                print line
#                print self.goal
            elif not look_for_goal == 'wait' and line.find('result') > -1:
                self.dialog_failure = False
#                print 'end'
                break
#            elif self.dialog_failure and line.find('Core terminated successfully') > -1:
#                break
        
        if len(self.turns) > self.max_turn_num:
            self.dialog_failure = True
            print filename + ' is %d turns long'%len(self.turns)
                
        if self.dialog_failure:
            file.close()
            return

#        '''
#        Abstraction
#        '''
        neighbors_monuments = ['THE AIRPORT','AIRPORT','CARNEGIE MUSEUM','CARNEGIE LIBRARY',\
                               'JEWISH COMMUNITY CENTER','CARNEGIE MELLON','CARNEGIE MELLON UNIVERSITY',\
                               'CMU','UNIVERSITY OF PITTSBURGH','PITT','CATHEDRAL OF LEARNING','SCHENLEY PARK',\
                               "KAUFMANN'S",'U S STEEL BUILDING','GATEWAY CENTER','ROBINSON TOWN CENTER',\
                               'IKEA','DOWNTOWN','DOWNTOWN PITTSBURGH','MCKEESPORT','GREENFIELD',\
                               'HAZELWOODHOMESTEAD','OAKLAND','SHADYSIDE','SQUIRREL HILL','SWISSVALE','BLOOMFIELD']
        
        self.abs_goal = copy.deepcopy(self.goal)
        self.abs_turns = copy.deepcopy(self.turns)
        for t, turn in enumerate(self.abs_turns):
            if turn['SA'][0].find('C:') == 0: 
                act,field,value = turn['SA'][0].split(':')
#                print self.goal[field] + ' vs. ' + value
                if self.goal['G_'+field].find(value) > -1:
                    turn['SA'][0] = 'C:o'
#                    print 'Correct'
                elif self.goal['G_'+field] not in neighbors_monuments and value in neighbors_monuments:
                    turn['SA'][0] = 'C:-'
#                    print 'Dont know'
                else:
                    turn['SA'][0] = 'C:x'
#                    print 'Incorrect'

            acts = []
            for act in turn['UA']:

#                if (act == 'yes' or act == 'no'):
#                    if self.abs_turns[t]['SA'][0] == 'C:o':
#                        acts.append('yes')
#                    else:
#                        acts.append('no')
#                elif act.find(':') > -1:
#                    acts.append(':'.join(act.split(':')[:-1]))

                if act.find(':') > -1:
                    acts.append(':'.join(act.split(':')[:-1]))
                else:
                    acts.append(act)
            turn['UA'] = acts
        if self.abs_goal['G_bn'] == '':
            self.abs_goal['G_bn'] = 'x'
        else:
            self.abs_goal['G_bn'] = 'o'
        file.close()
        
class Corpus:
    '''
    Class Corpus
    @param paths: string or list of string argument to specify folders that contain corpus files 
    '''
    def __init__(self,paths,ext='dialog.log',prep=False,model='model/_Corpus.model'):
        self.prep = prep
        self.model = model
        
        if prep: return
        
        if isinstance(paths,str):
            self.paths = [paths]
        else:
            self.paths = paths
        
    def dialogs(self):
        if self.prep:
            import pickle,string
            f = open(self.model,'rb')
            for s in f:
                yield pickle.loads(string.replace(s,'!@#$%','\n'))
            f.close()
            return
        for path in self.paths:
            if os.path.isdir(path):
                for root,dirs,files in os.walk(path):
                    for filename in files:
                        if filename.endswith('dialog.log'):
                            print filename
                            filename = os.path.join(root,filename)
                            dialog = Dialog(filename)
                            if dialog.dialog_failure:
                                print 'dialog fail: %s'%filename
                                continue
                            else:
                                yield dialog

    def goal_table(self):
        goal_table = {}
        for dialog in self.dialogs():
            try:
                goal_table[str(dialog.goal)] += 1
            except:
                goal_table[str(dialog.goal)] = 1
        return goal_table

    def val_list(self):
        val_list = {'bn':[],'dp':[],'ap':[],'tt':[]}
        for dialog in self.dialogs():
            for k in dialog.goal.keys():
                if dialog.goal[k]:
                    val_list[k.split('_')[-1]].append(dialog.goal[k])
        for k in val_list:
            val_list[k] = set(val_list[k])
        return val_list
    
    def preprocess(self):
        import pickle,string
        
        f = open(self.model,'wb')
        for dialog in self.dialogs():
            s = pickle.dumps(dialog)
            f.write(string.replace(s,'\n','!@#$%')+'\n')
        f.close()
        
