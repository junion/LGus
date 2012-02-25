
import os,copy

def uniqify(seq, idfun=None):  
    # order preserving 
    if idfun is None: 
        def idfun(x): return x 
    seen = {} 
    result = [] 
    for item in seq: 
        marker = idfun(item) 
        # in old Python versions: 
        # if seen.has_key(marker) 
        # but in new ones: 
        if marker in seen: continue 
        seen[marker] = 1 
        result.append(item) 
    return result

class Dialog:
    '''
    Class Dialog
    @param filename: string argument
    '''
    def __init__(self,filename,max_turn_num=40):
        self.id = filename
        self.goal = {'G_bn':'','G_dp':'','G_ap':'','G_tt':''}
        self.turns = []
        self.dialog_result = 'fail'
        self.max_turn_num = max_turn_num
        self.info_buffer = []
        
        try:
            file = open(filename,'r')
        except:
            print 'File open error: %s'%filename
            return None
        
#        look_for_value = 'wait'
#        look_for_goal = 'wait'
#        look_for_ua = 'wait'
        preceding_direction = 'none'
        parsing_state = ''
        for line in file:
            line = line.rstrip()
#            print line
            
            # filter out any dialog which has the following matches
            if line.find('object\tuncovered_place') > -1:
                self.dialog_result = 'uncovered_place'
                break
            if line.find('object\tno_stop_matching') > -1:
                self.dialog_result = 'no_stop_matching'
                break
            if line.find('object\tuncovered_route') > -1:
                self.dialog_result = 'uncovered_route'
                break
            if line.find('object\tdiscontinued_route') > -1:
                self.dialog_result = 'discontinued_route'
                break
            if line.find('[[dtmf_key]]') > -1:
                self.dialog_result = 'dtmf_key'
                break
            if line.find('[[generic.help]]') > -1:
                self.dialog_result = 'help'
                break
            if line.find('[[generic.startover]]') > -1:
                self.dialog_result = 'startover'
                break
            if line.find('object\tquery.exact_travel_time') > -1:
                self.dialog_result = 'exact_travel_time'
                break
            # this only happens in ravenclaw
            if line.find('{request query.route') == 0 or\
            line.find('{request query.line') == 0 or\
            line.find('{request departure_neighborhood') == 0 or\
            line.find('{request departure_stop_in_neighborhood') == 0 or\
            line.find('{request arrival_neighborhood') == 0 or\
            line.find('{request arrival_stop_in_neighborhood') == 0:
                self.dialog_result = 'ravenclaw'
                break
            
            # turn extraction
#            if line.find('Success') > -1 and line.find('Departure') > -1:
#                potential_field = 'dp'
#            elif line.find('Success') > -1 and line.find('Arrival') > -1:
#                potential_field = 'ap'
            # system part
            if line.find('object\thow_to_get_help') > -1:
                turn = {'SA':['R:open']}
            elif line.find('object\thow_may_i_help_you_directed') > -1:
                turn = {'SA':['R:dp']}
                preceding_direction = 'dp'
            elif line.find('object\thow_may_i_help_you') > -1:
                turn = {'SA':['R:open']}
            elif line.find('object\tquery.departure_place') > -1:
                turn = {'SA':['R:dp']}
                preceding_direction = 'dp'
            elif line.find('object\tquery.arrival_place') > -1:
                turn = {'SA':['R:ap']}
                preceding_direction = 'ap'
            elif line.find('object\tquery.travel_time') > -1:
                turn = {'SA':['R:tt']}
            elif line.find('object\t/LetsGoPublic/query.route_number') > -1:
                parsing_state = 'expect_confirm_route_value'
            elif line.find('object\t/LetsGoPublic/query.departure_place') > -1:
                parsing_state = 'expect_confirm_departure_place_value'
                preceding_direction = 'dp'
            elif line.find('object\t/LetsGoPublic/query.arrival_place') > -1:
                parsing_state = 'expect_confirm_arrival_place_value'
                preceding_direction = 'ap'
            elif line.find('object\t/LetsGoPublic/query.travel_time.time') > -1:
                parsing_state = 'expect_confirm_travel_time_value'
                
            elif line.find('object\t/LetsGoPublic/uncovered_place') > -1:
                parsing_state = 'expect_confirm_uncovered_place_value'
            elif line.find('object\t/LetsGoPublic/discontinued_route') > -1:
                parsing_state = 'expect_confirm_discontinued_route_value'
            elif line.find('object\t/LetsGoPublic/uncovered_route') > -1:
                parsing_state = 'expect_confirm_uncovered_route_value'

            elif parsing_state == 'expect_confirm_route_value' and line.find('query.route_number') == 0:
                turn = {'SA':['C:bn:%s'%line.split('\t')[1]]}
                parsing_state = ''
            elif parsing_state == 'expect_confirm_departure_place_value' and line.find('name') == 0:
                turn = {'SA':['C:dp:%s'%line.split('\t')[1]]}
                parsing_state = ''
            elif parsing_state == 'expect_confirm_arrival_place_value' and line.find('name') == 0:
                turn = {'SA':['C:ap:%s'%line.split('\t')[1]]}
                parsing_state = ''
            elif parsing_state == 'expect_confirm_travel_time_value' and line.find('value') == 0:
                turn = {'SA':['C:tt:%s'%line.split('\t')[1]]}
            elif parsing_state == 'expect_confirm_travel_time_value' and line.find('now') == 0 and line.split('\t')[1] == 'true':
                turn = {'SA':['C:tt:now']}

            elif parsing_state == 'expect_confirm_uncovered_place_value' and line.find('name') == 0:
                if preceding_direction == 'dp':
                    turn = {'SA':['C:dp:%s'%line.split('\t')[1]]}
                elif preceding_direction == 'ap':
                    turn = {'SA':['C:ap:%s'%line.split('\t')[1]]}
                else:
                    self.dialog_result = 'ambiguous_confirm_place'
                    break
                parsing_state = ''
            elif parsing_state == 'expect_confirm_discontinued_route_value' and line.find('discontinued_route') == 0:
                turn = {'SA':['C:bn:%s'%line.split('\t')[1]]}
                parsing_state = ''
            elif parsing_state == 'expect_confirm_uncovered_route_value' and line.find('uncovered_route') == 0:
                turn = {'SA':['C:bn:%s'%line.split('\t')[1]]}
                parsing_state = ''
                
            # user part
            elif line.find('New user input') > -1 or line.find(':last_level_touched') > -1:
                parsing_state = 'expect_user_action'
                try:
                    turn['UA'] = []
                except:
                    turn = {'SA':['O:-'],'UA':[]}
#                print turn
            elif line.find('[h4_confidence]') > -1 or line.find('[confidence]') > -1:
                turn['CS'] = float(line.split('=')[1])
            elif line.find(':confidence') > -1:
                turn['CS'] = float(line.split('"')[1].split('"')[0])

            # Place
            elif line.find(':[1_singleplace.stop_name.uncovered_place]') > -1 or\
            line.find(':[1_singleplace.stop_name.covered_place]') > -1:
                if preceding_direction == 'dp':
                    turn['UA'].append('I:dp:%s'%line.split('"')[1].split('"')[0])
                elif preceding_direction == 'ap':
                    turn['UA'].append('I:dp:%s'%line.split('"')[1].split('"')[0])
                else:
                    self.dialog_result = 'ambiguous_place'
                    break
            elif line.find('  [1_singleplace.stop_name.uncovered_place]') > -1 or\
            line.find('  [1_singleplace.stop_name.covered_place]') > -1 or\
            line.find('  [[1_singleplace.stop_name.uncovered_place]]') > -1 or\
            line.find('  [[1_singleplace.stop_name.covered_place]]') > -1:
                if preceding_direction == 'dp':
                    turn['UA'].append('I:dp:%s'%line.split('=')[1].strip())
                elif preceding_direction == 'ap':
                    turn['UA'].append('I:ap:%s'%line.split('=')[1].strip())
                else:
                    self.dialog_result = 'ambiguous_place'
                    break
            elif line.find(':[2_departureplace.stop_name.uncovered_place]') > -1 or\
            line.find(':[2_departureplace.stop_name.covered_place]') > -1:
                turn['UA'].append('I:dp:%s'%line.split('"')[1].split('"')[0])
            elif line.find('  [2_departureplace.stop_name.uncovered_place]') > -1 or\
            line.find('  [2_departureplace.stop_name.covered_place]') > -1 or\
            line.find('  [[2_departureplace.stop_name.uncovered_place]]') > -1 or\
            line.find('  [[2_departureplace.stop_name.covered_place]]') > -1:
                turn['UA'].append('I:dp:%s'%line.split('=')[1].strip())
            elif line.find(':[3_arrivalplace.stop_name.uncovered_place]') > -1 or\
            line.find(':[3_arrivalplace.stop_name.covered_place]') > -1:
                turn['UA'].append('I:ap:%s'%line.split('"')[1].split('"')[0])
            elif line.find('  [3_arrivalplace.stop_name.uncovered_place]') > -1 or\
            line.find('  [3_arrivalplace.stop_name.covered_place]') > -1 or\
            line.find('  [[3_arrivalplace.stop_name.uncovered_place]]') > -1 or\
            line.find('  [[3_arrivalplace.stop_name.covered_place]]') > -1:
                turn['UA'].append('I:ap:%s'%line.split('=')[1].strip())
            
            # Route
            elif line.find(':[0_busnumber.route.0_uncovered_route]') > -1 or\
            line.find(':[0_busnumber.route.0_discontinued_route]') > -1 or\
            line.find(':[0_busnumber.route.0_covered_route]') > -1:
                turn['UA'].append('I:bn:%s'%line.split('"')[1].split('"')[0])
            elif line.find('  [0_busnumber.route.0_uncovered_route]') > -1 or\
            line.find('  [0_busnumber.route.0_discontinued_route]') > -1 or\
            line.find('  [0_busnumber.route.0_covered_route]') > -1 or\
            line.find('  [[0_busnumber.route.0_uncovered_route]]') > -1 or\
            line.find('  [[0_busnumber.route.0_discontinued_route]]') > -1 or\
            line.find('  [[0_busnumber.route.0_covered_route]]') > -1:
                turn['UA'].append('I:bn:%s'%line.split('=')[1].strip())
 
            # Time
            elif line.find(':timeperiod_spec') > -1:
                time = line.split('"')[1].split('"')[0]
                if  time == 'now ':
                    turn['UA'].append('I:tt:%s'%time)
                else:
                    parsing_state = 'expect_travel_time_value'
            elif parsing_state == 'expect_travel_time_value' and line.find(':start_time') > -1:
                turn['UA'].append('I:tt:%s'%line.split('"')[1].split('"')[0])
            elif parsing_state == 'expect_user_action' and line.find('[[4_datetime]]') > -1:
                parsing_state = 'expect_travel_time_value'
            elif parsing_state == 'expect_travel_time_value' and line.find('value') == 0:
                time = line.split('|')[0].split('\t')[1]
            elif parsing_state == 'expect_travel_time_value' and line.find('now') == 0 and line.split('|')[0].split('\t')[1] == 'true':
                time = 'now'
            elif parsing_state == 'expect_travel_time_value' and line.find('bound to concept') > -1 and line.find('query.travel_time') > -1:
                try:
                    turn['UA'].append('I:tt:%s'%time)
                except:
                    self.dialog_result = 'need_exact_time'
                    break
                parsing_state = 'expect_user_action'
            elif line.find(':[4_busafterthatrequest]') > -1 or\
                line.find('  [4_busafterthatrequest]') > -1:                
                turn['UA'].append('I:tt:now')
            
            # Yes/No
            elif line.find('[[generic.yes]]') > -1:
                turn['UA'].append('yes')
                try:
                    act,field,value = turn['SA'][-1].split(':')
                    if act == 'C':
                        self.goal['G_%s'%field] = value
                        print 'UG %s: '%field + value
                except:
                    pass
            elif line.find('[[generic.no]]') > -1:
                turn['UA'].append('no')

            elif (parsing_state == 'expect_user_action' or parsing_state == 'expect_travel_time_value') and\
            (line.find('_UserUtteranceEndHandler: ASRResult') > -1 or\
            line.find('Concepts Binding Phase completed') > -1):
                if turn['UA'] == []:
                    turn['UA'] = ['non-understanding']
                turn['UA'] = uniqify(turn['UA'])
                self.turns.append(copy.deepcopy(turn))
                del turn
                parsing_state = ''

            # backend query
            elif line.find('Make query for schedule') > -1 or\
            line.find('Executing dialog agent /LetsGoPublic/PerformTask/ProcessQuery/ExecuteBackendCall') > -1:
                parsing_state = 'expect_goal_value'
            elif parsing_state == 'expect_goal_value' and  line.find('route_number') > -1:
                self.goal['G_bn'] = line.split('\t')[1]
            elif parsing_state.find('expect_goal') > -1 and line.find('departure_place') > -1:
                parsing_state = 'expect_goal_departure_place_value'
            elif parsing_state.find('expect_goal') > -1 and line.find('arrival_place') > -1:
                parsing_state = 'expect_goal_arrival_place_value'
            elif parsing_state.find('expect_goal') > -1 and line.find('travel_time') > -1:
                parsing_state = 'expect_goal_travel_time_value'
            elif parsing_state.find('expect_goal') > -1 and line.find('departure_stops') > -1:
                parsing_state = 'expect_goal_departure_place_value'
            elif parsing_state.find('expect_goal') > -1 and line.find('arrival_stops') > -1:
                parsing_state = 'expect_goal_arrival_place_value'
            elif parsing_state == 'expect_goal_departure_place_value' and line.find('name') == 0 and self.goal['G_dp'] == '':
                self.goal['G_dp'] = line.split('\t')[1]
            elif parsing_state == 'expect_goal_arrival_place_value' and line.find('name') == 0 and self.goal['G_ap'] == '':
                self.goal['G_ap'] = line.split('\t')[1]
            elif parsing_state == 'expect_goal_travel_time_value' and line.find('now') == 0:
                if line.split('\t')[1] == 'true':
                    self.goal['G_tt'] = 'now'
            elif parsing_state == 'expect_goal_travel_time_value' and line.find('value') == 0:
                self.goal['G_tt'] = line.split('\t')[1]

            # Termination
            elif line.find('[[generic.quit]]') > -1:
                print 'quit'
                break
            elif line.find('object\tresult') > -1:
                self.dialog_result = 'success'
                break
            elif line.find('object\terror') > -1:
                self.dialog_result = 'no ride'
                break
            elif line.find('Dialog thread terminated') > -1 or \
            line.find('Core terminated successfully') > -1:
                print 'terminate'
                break
        
        print 'Dialog result: ' + self.dialog_result

        if len(self.turns) > self.max_turn_num or len(self.turns) < 1:
            self.dialog_result = 'turn_num'
#            print filename + ' is %d turns long'%len(self.turns)

        print 'Dialog result: ' + self.dialog_result
                        
        if self.dialog_result not in ['fail','success']:
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
                    turn['SA'][0] = 'C:%s:o'%field
#                    print 'Correct'
#                elif self.goal['G_'+field] not in neighbors_monuments and value in neighbors_monuments:
#                    turn['SA'][0] = 'C:-'
#                    print 'Dont know'
                else:
                    turn['SA'][0] = 'C:%s:x'%field
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

    def old_init(self,filename,max_turn_num=40):
        self.id = filename
        self.goal = {'G_bn':'','G_dp':'','G_ap':'','G_tt':''}
        self.turns = []
        self.dialog_result = 'fail'
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
            if line.find('object\tuncovered_place') > -1:
                self.dialog_result = 'fail'
                break
            if line.find('object\tno_stop_matching') > -1:
                self.dialog_result = 'fail'
                break
            if line.find('object\tuncovered_route') > -1:
                self.dialog_result = 'fail'
                break
            if line.find('object\tdiscontinued_route') > -1:
                self.dialog_result = 'fail'
                break
            if line.find('[[dtmf_key]]') > -1:
                self.dialog_result = 'fail'
                break
            if line.find('[general_help]') > -1:
                self.dialog_result = 'fail'
                break
            if line.find('[[generic.startover]]') > -1:
                self.dialog_result = 'fail'
                break
            
#            '''
#            Turn extraction
#            '''
            if line.find('Success') > -1 and line.find('Departure') > -1:
                potential_field = 'dp'
            elif line.find('Success') > -1 and line.find('Arrival') > -1:
                potential_field = 'ap'
            elif line.find('object\thow_to_get_help') == 0:
                turn = {'SA':['R:open']}
            elif line.find('object\thow_may_i_help_you_directed') == 0:
                turn = {'SA':['R:dp']}
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
                elif line.find('uncovered_place') > -1:
                    if self.turns[-1]['SA'][0].find('R:dp') > -1:
                        look_for_value = 'dp'
                    elif self.turns[-1]['SA'][0].find('R:ap') > -1:
                        look_for_value = 'ap'
                    else:
                        dialog_result = 'others'
                        break
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
                    try:
                        act,field,value = turn['SA'][0].split(':')
                        if act == 'C':
                            self.goal['G_%s'%field] = value
                            print 'UG %s: '%field + value
                    except:
                        pass
                        
#                    print line
                elif line.find('[no]') > -1:
                    turn['UA'].append('no')
#                    print line
                elif line.find('route') > -1:
#                    turn['UA'].append('I:bn')
                    turn['UA'].append('I:bn:%s'%line.split('(')[2].split('|')[0])
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
                elif line.find('UncoveredPlace') > -1:
                    try:
                        if not place == '':
                            if turn['SA'][0].find('R:dp') > -1 or turn['SA'][0].find('C:dp') > -1:
                                turn['UA'].append('I:dp:%s'%place);place = ''
                            elif turn['SA'][0].find('R:ap') > -1 or turn['SA'][0].find('C:ap') > -1:
                                turn['UA'].append('I:ap:%s'%place);place = ''
                            else:
                                dialog_result = 'others'
                                break
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
            elif not look_for_goal == 'wait' and line.find('object\tresult') > -1:
                self.dialog_result = 'success'
#                print 'end'
                break
            elif not look_for_goal == 'wait' and line.find('object\terror') > -1:
                self.dialog_result = 'error'
#                print 'end'
                break
#            elif self.dialog_failure and line.find('Core terminated successfully') > -1:
#                break
        
        if len(self.turns) > self.max_turn_num or len(self.turns) < 1:
            self.dialog_result = 'others'
#            print filename + ' is %d turns long'%len(self.turns)

        print 'Dialog result: ' + self.dialog_result
                        
        if self.dialog_result == 'others':
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
                    turn['SA'][0] = 'C:%s:o'%field
#                    print 'Correct'
#                elif self.goal['G_'+field] not in neighbors_monuments and value in neighbors_monuments:
#                    turn['SA'][0] = 'C:-'
#                    print 'Dont know'
                else:
                    turn['SA'][0] = 'C:%s:x'%field
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
                            if dialog.dialog_result not in ['fail','success']:
                                print 'Exclude: %s'%filename
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
        
    def dump(self):
        for i,dialog in enumerate(self.dialogs()):
            print dialog.goal
            print dialog.abs_goal
            print dialog.turns
            print dialog.abs_turns
            if i > 15:
                break
