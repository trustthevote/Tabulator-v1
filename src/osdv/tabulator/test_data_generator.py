#!/usr/bin/env python

"""
Developed with Python 2.6.2
Name: test_data_generator.py
Author: Mike Anderson
Created: Jul 30, 2009
Purpose: To generate test data files for the merger and tabulator
"""

from __future__ import with_statement
import random
import yaml
import sys
import copy
import uuid

from xml_serializer import xml_serialize
import audit_header

class ProvideRandomBallots(object):

    """
    Provide random election specs or random ballot counts
    """

    # Takes as its arguments the type of random data to generate
    def __init__(self, args):
        # These variables are used to ensure that if the same random
        #  data is generated in some circumstances, it will not appear
        #  twice in the template.
        self.already_used_streps = []
        self.already_used_dreps = []
        self.already_used_names = []
        self.already_used_cand_idents = []
        self.already_used_dist_names = []
        self.already_used_supreme = False
        self.fname_list = []
        self.lname_list = []

        self.args = args
        self.params = {}
        for arg in self.process_flags():
            self.args.remove(arg)

        self.type = self.args[0]
        if self.type == 'jurisdiction':
        # Generate a sample jurisdiction_slate and output it to the
        #  location specified by the user in the command line, in yaml
        #  and xml formats.
            b = {}

            # Give each file its own audit header, generate data
            a = audit_header.AuditHeader()
            a.set_fields('jurisdiction_slate',
                         'Pito Salas', 'TTV Tabulator TAB02', 
                         'TTV Tabulator 0.1 JUL-1-2008', [])
            b = self.make_juris()
            b['jurisdiction_display_name'] = (self.args[1]\
             [self.args[1].rfind('/') + 1:len(self.args[1])]).encode("ascii")

            # Dump output into a file in yaml format
            with open(''.join([self.args[1],'.yml']), 'w') as stream:
                stream.write(a.serialize_yaml())
                yaml.dump(b, stream)

            # Dump output into a file in XML file
            with open(''.join([self.args[1],'.xml']), 'w') as stream:
                stream.write(a.serialize_xml())
                stream.writelines(xml_serialize(b, 0))

        elif self.type == 'contestlist':
        # Generate a sample election and output it to the location
        #  specified by the user in the command line, in yaml and xml
        #  formats.
            b = {}

            # Give each file its own audit header, generate data
            a = audit_header.AuditHeader()
            a.set_fields('precinct_contestlist',
                         'Pito Salas', 'TTV Tabulator TAB02', 
                         'TTV Tabulator 0.1 JUL-1-2008', [])
            b = self.random_elec()

            # Dump output into a file in yaml format
            with open(''.join([self.args[1],'.yml']), 'w') as stream:
                stream.write(a.serialize_yaml())
                yaml.dump(b, stream)

            # Dump output into a file in XML file
            with open(''.join([self.args[1], '.xml']), 'w') as stream:
                stream.write(a.serialize_xml())
                stream.writelines(xml_serialize(b, 0))

        elif self.type == 'counts':
            r_min = self.params['counts_min']
            r_max = self.params['counts_max']
            
            # Load election specs from given file in yaml format
            with open(''.join([self.args[2],'.yml']), 'r') as stream:
                for i in range(0,8):  # Ignore the audit header
                    stream.readline()
                e = yaml.load(stream)

            # Make the number of random ballot_info records specified by
            #  the user. Use the loaded election specs as a template,
            #  assign the vote counts of each candidate a value between 
            #  0 and 99.
            b_list = []
            for i in range(int(self.args[1])):
                b = {}
                for key in e.keys():
                    if key not in ['contest_list', 'precinct_list',
                     'jurisdiction_display_name']:
                        b[key] = e[key]
                b['contest_list'] = []
                prec_num = random.randint(0, e['number_of_precincts'] - 1)
                b['prec_ident'] = e['precinct_list'][prec_num]['ident']
                if e.has_key('precinct_list'):
                    b['registered_voters'] = \
                     e['precinct_list'][prec_num-1]['registered_voters']
                for j in range(len(e['contest_list'])):
                    # If the template was a jurisdiction_slate, then
                    #  do not include contests that were not generated
                    #  in a district in this precinct.
                    if e.has_key('precinct_list'):
                        valid_contest = False
                        for prec in e['precinct_list']:
                            if prec['ident'] == b['prec_ident']:
                                for dist in prec['district_list']:
                                    if dist['ident'] == \
                                     e['contest_list'][j]['district_ident']:
                                        valid_contest = True
                                        break
                        if not valid_contest:
                            continue
                    b['contest_list'].append(copy.deepcopy(e['contest_list'][j]))
                    cont = b['contest_list'][-1]
                    if not cont.has_key('total_votes'):
                        cont['total_votes'] = 0
                        cont['uncounted_ballots'] = {}
                        cont['uncounted_ballots']['blank_votes'] = 0
                        cont['uncounted_ballots']['over_votes'] = 0
                        cont['voting_method_ident'] = ''.join(['VOTM-',
                         str(random.randint(1,5))])
                    for cand in cont['candidates']:
                        if cand['display_name'] == 'Write-In Votes':
                            cand['count'] = random.randint(r_min, r_max)
                        else:
                            cand['count'] = random.randint(r_min, r_max)
                        cont['total_votes'] += cand['count']
                    cont['uncounted_ballots']['blank_votes'] = \
                     random.randint(r_min,r_max)
                    cont['uncounted_ballots']['over_votes'] = \
                     random.randint(r_min,r_max)

                # Generate a random polling type for this session
                r = random.randint(0,3)
                if r == 0:
                    b['vote_type'] = 'Polling'
                elif r == 1:
                    b['vote_type'] = 'Early Voting'
                elif r == 2:
                    b['vote_type'] = 'Absentee'
                else:
                    b['vote_type'] = 'Other'

                b_list.append(b)

            # Give each file its own audit header
            a = audit_header.AuditHeader()
            a.set_fields('ballot_counter_total',
                         'Pito Salas', 'TTV Tabulator TAB02', 
                         'TTV Tabulator 0.1 JUL-1-2008', [])

            # Dump output into a file in yaml format
            with open(''.join([self.args[3],'.yml']), 'w') as stream:
                stream.write(a.serialize_yaml())
                yaml.dump_all(b_list, stream)

            # Dump output into a file in XML file
            with open(''.join([self.args[3],'.xml']), 'w') as stream:
                stream.write(a.serialize_xml())
                for record in b_list:
                    stream.writelines(xml_serialize(record, 0))
        else:
            raise StandardError('Incorrect data generation type')

    def make_juris(self):
        """
        Make and return a jurisdiction_slate
        """

        b = self.random_elec()

        # Make some precincts
        b['precinct_list'] = []
        b['number_of_precincts'] = self.params['num_precs']
        for i in range(1, b['number_of_precincts'] + 1):
            b['precinct_list'].append({})
            prec = b['precinct_list'][i - 1]
            prec['display_name'] = random.randint(1000,9999)
            prec['ident'] = ''.join(['PREC-',str(i)])
            prec['district_list'] = []
            prec['voting places'] = []
            prec['voting places'].append({})
            prec['voting places'][0]['ballot_counters']=random.randint(1,5)
            prec['voting places'][0]['ident'] = ''.join(['VLPC-',str(i)])
            prec['registered_voters'] = random.randint(900,1100)
            b['registered_voters'] += prec['registered_voters']

        # If the user does not specify either the number of districts
        #  or the number of precincts that should be randomly generated,
        #  use default districts.
        if self.params['num_dists'] == -1 or self.params['num_precs'] == 8:
            # Give the precincts some hardcoded districts
            l = b['precinct_list']
            n1 = 'City of Random'
            n2 = 'Random Creek Drainage District'
            n3 = 'State House District 11'
            n4 = 'State House District 12'
            l[0]['district_list'].append({'display_name':n1, 'ident':'DIST-1'})
            l[0]['district_list'].append({'display_name':n3, 'ident':'DIST-3'})
            l[1]['district_list'].append({'display_name':n1, 'ident':'DIST-1'})
            l[1]['district_list'].append({'display_name':n4, 'ident':'DIST-4'})
            l[2]['district_list'].append({'display_name':n1, 'ident':'DIST-1'})
            l[2]['district_list'].append({'display_name':n2, 'ident':'DIST-2'})
            l[2]['district_list'].append({'display_name':n4, 'ident':'DIST-4'})
            l[3]['district_list'].append({'display_name':n3, 'ident':'DIST-3'})
            l[4]['district_list'].append({'display_name':n2, 'ident':'DIST-2'})
            l[4]['district_list'].append({'display_name':n3, 'ident':'DIST-3'})
            l[5]['district_list'].append({'display_name':n1, 'ident':'DIST-1'})
            l[5]['district_list'].append({'display_name':n2, 'ident':'DIST-2'})
            l[5]['district_list'].append({'display_name':n4, 'ident':'DIST-4'})
            l[6]['district_list'].append({'display_name':n2, 'ident':'DIST-2'})
            l[7]['district_list'].append({'display_name':n4, 'ident':'DIST-4'})
        # Otherwise, generate the number of districts that the user
        #  specified. and assign them to the already generated precincts
        else:
            dist_list = []
            d_names = ['President', 'US Representative', 'House District',
             'Senate District', 'Soil & Water District', 'Harbor District',
             'School District']
            d_names_append10 = ['US Representative District', 'House District',
             'Senate District']
            for i in range(self.params['num_dists']):
                d = {}
                while True:
                    name = random.choice(d_names)
                    if name in d_names_append10:
                        name = '%s %s' % (name, str(random.randint(1, 10)))
                    elif name == 'School District':
                        name = '%s %s' % (name, str(random.randint(1, 5)))
                    if not name in self.already_used_dist_names:
                        self.already_used_dist_names.append(name)
                        break
                d['display_name'] = name
                d['ident'] = ''.join(['DIST-', str(i + 1)])
                dist_list.append(d)
            print self.params['num_dists']
            print dist_list
            for i in range(len(b['precinct_list'])):
                d1 = random.choice(range(self.params['num_dists']))
                while True:
                    d2 = random.choice(range(self.params['num_dists']))
                    while True:
                        d3 = random.choice(range(self.params['num_dists']))
                        if d3 != d2 and d3 != d1:
                            break
                    if d2 != d1:
                        break

                b['precinct_list'][i]['district_list'].append(dist_list[d1])
                b['precinct_list'][i]['district_list'].append(dist_list[d2])
                b['precinct_list'][i]['district_list'].append(dist_list[d3])
        return b

    def random_elec(self):
        """
        Make and return a ballot with initialized data members
        """

        b = {}
        self.cand_num = 1

        # Load a list of first and last names from file
        with open('first_names', 'r') as stream:
            self.fnames = stream.readlines()
        with open('last_names', 'r') as stream:
            self.lnames = stream.readlines()

        # Make the election headliner some random presidential election
        r = random.randint(0,3)
        b['display_name'] = ''.join([str(r*4+2000),' Presidential'])
        b['number_of_precincts'] = 0
        b['registered_voters'] = 0
        
        # Generate some contests
        b['contest_list'] = []
        for i in range(self.params['num_conts']):
            b['contest_list'].append(self.random_contest())            
        return b

    def random_contest(self):
        """
        Make and return a contest object with initialized data members
        """

        cont = {}

        # Generate a few candidates per contest
        cont['candidates'] = []
        r = random.randint(self.params['cands_min'],self.params['cands_max'])
        for i in range(0,r):
            cont['candidates'].append(self.random_candidate(False))
        cont['candidates'].append(self.random_candidate(True))

        # Make sure that a maximum of one supreme court justice contest
        #  is generated.
        if self.already_used_supreme:
            r = random.randint(1,2)
        else:
            r = random.randint(1,3)
        
        # Generate a random type of race
        if r == 1:
            cont['display_name'] = 'Representative in Congress'

            # Generate random values for the dist number until an unused
            #  number is generated. Once this is successful, use the
            #  unused number and add it to a list of used numbers.
            while True:
                r = random.randint(1,9)
                if self.already_used_dreps.count(r) == 0:
                    self.already_used_dreps.append(r)
                    if r == 1:
                        cont['ident'] = 'Rep1stDistrict'
                    elif r == 2:
                        cont['ident'] = 'Rep2ndDistrict'
                    elif r == 3:
                        cont['ident'] = 'Rep3rdDistrict'
                    else:
                        cont['ident'] = ''.join(['Rep',str(r),
                         'thDistrict'])
                    break
        elif r == 2:
            cont['display_name'] = 'State Representative'
            
            # Generate random values for the House number until an
            #  unused number is generated. Once this is successful, use
            #  the unused number and add it to a list of used numbers.
            while True:
                r = random.randint(1,9)
                if self.already_used_streps.count(r) == 0:
                    self.already_used_streps.append(r)
                    if r == 1:
                        cont['ident'] = 'StateRep1stHouse'
                    elif r == 2:
                        cont['ident'] = 'StateRep2ndHouse'
                    elif r == 3:
                        cont['ident'] = 'StateRep3rdHouse'
                    else:
                        cont['ident'] = ''.join(['StateRep',str(r),
                         'thHouse'])
                    break
        else:
            cont['display_name'] = 'Supreme Court Justice'
            cont['ident'] = 'JustSupCrt'
            self.already_used_supreme = True
    
        cont['district_ident'] = ''.join(['DIST-',str(random.randint(1,4))])
        return cont

    def random_candidate(self, write_in):
        """
        Make and return a candidate object with initialized data
         members
        """
        
        cand = {}
        
        # If the "candidate" to be generated is just a placeholder for
        #  write-in candidates, then use some hardcoded field values
        if write_in:
            cand['display_name'] = "Write-In Votes"
            cand['ident'] = 'CAND-000'
            cand['party_ident'] = 'PART-0'
        else:
            cand['display_name'] = self.random_fullname()
            while True:
                r = random.randint(100,999)
                if self.already_used_cand_idents.count(r) == 0:
                    self.already_used_cand_idents.append(r)
                    cand['ident'] = ''.join(['CAND-',str(r)])
                    break
            cand['party_ident'] = ''.join(['PART-',str(random.randint(1,9))])
        
        return cand

    def random_fullname(self):
        """
        Make and return a random full name string
        """
        
        # Generate a first and last name combination
        fname = self.fnames[random.randint(0, len(self.fnames) - 1)].strip()
        lname = self.lnames[random.randint(0, len(self.lnames) - 1)].strip()
        fullname = ' '.join([fname,lname])
        
        if self.already_used_names.count(fullname) == 0:
            self.already_used_names.append(fullname)
            return fullname
        else:
            return(self.random_fullname())

    def process_flags(self):
        """
        Process and tag for removal test data generation flags from
         argument list, and set defaults if no flags are given for a
         specific parameter.
        """
        
        remove_me = []
        for arg in self.args:
            if arg == '-1':
                self.params['counts_min'] = 1
                self.params['counts_max'] = 1
                remove_me.append(arg)
            elif arg[0] == '+':
                self.params['counts_min'] = 0
                self.params['counts_max'] = int(arg[1:])
                remove_me.append(arg)
            elif arg[:2] == '-C':
                self.params['num_conts'] = int(arg[2:])
                remove_me.append(arg)
            elif arg[:3] == '-cl':
                self.params['cands_min'] = int(arg[3:])
                remove_me.append(arg)
            elif arg[:3] == '-cu':
                self.params['cands_max'] = int(arg[3:])
                remove_me.append(arg)
            elif arg[:2] == '-c':
                self.params['cands_min'] = int(arg[2:])
                self.params['cands_max'] = int(arg[2:])
                remove_me.append(arg)
            elif arg[:2] == '-d':
                self.params['num_dists'] = int(arg[2:])
                remove_me.append(arg)
            elif arg[:2] == '-p':
                self.params['num_precs'] = int(arg[2:])
                remove_me.append(arg)
        
        if not self.params.has_key('counts_min'):
            self.params['counts_min'] = 0
        if not self.params.has_key('counts_max'):
            self.params['counts_max'] = 100
        if not self.params.has_key('num_conts'):
            self.params['num_conts'] = 10
        if not self.params.has_key('cands_min'):
            self.params['cands_min'] = 2
        if not self.params.has_key('cands_max'):
            self.params['cands_max'] = 4
        if not self.params.has_key('num_dists'):
            self.params['num_dists'] = -1
        if not self.params.has_key('num_precs'):
            self.params['num_precs'] = 8

        return remove_me

def printUsage():
    print 'Usage: test_data_generator.py jurisdiction [OUTPUT ELECTION FILE]'
    print '   OR: test_data_generator.py contestlist [OUTPUT ELECTION FILE]'
    print '   OR: test_data_generator.py counts [# OF SAMPLES]'
    print '       [INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]'
    print '   OR: test_data_generator.py counts [# OF SAMPLES]'
    print '       [INPUT ELECTION FILE] [OUTPUT SAMPLES FILE] [OPTION]'
    print
    print
    print 'Where [OPTION] can consist of one of the following:'
    print '   -1'
    print '      All count fields in the generated BCT output will contain'
    print '      the value 1'
    print 
    print '   +[NUMBER]'
    print '      All count fields in the generated BCT output will contain'
    print '      a value between 0 and [NUMBER]'
    exit()

def main(): 
    # First make sure that the command line input is valid. If it is not
    #  then output a usage statement and exit
    if len(sys.argv) == 1: sys.argv.append('')
    type = sys.argv[1]
    if type == 'jurisdiction':
        if len(sys.argv) != 3:
            printUsage()
    elif type == 'contestlist':
        if len(sys.argv) != 3:
            printUsage()
    elif type == 'counts':
        # This condition is complicated by the possibility of BCT flags
        if len(sys.argv) != 5 and \
         ( len(sys.argv) != 6 or (not sys.argv[5][0] in ['-','+']) ):
            printUsage()
    else:
        printUsage()
    # Get rid of unneccesary command line arguments and generate random
    #  data of the specified type
    p = ProvideRandomBallots(sys.argv[1:])

    if type == 'jurisdiction':
        print 'Done. Generated sample jurisdiction template files',
        print '%s.yml and %s.xml\n' % (sys.argv[2], sys.argv[2])

    elif type == 'contestlist':
        print 'Done. Generated sample contestlist template files',
        print '%s.yml and %s.xml\n' % (sys.argv[2], sys.argv[2])
    else:
        print 'Done. Generated sample ballot files',
        print '%s.yaml and %s.xml\n' % (sys.argv[4], sys.argv[4])

    return 0
    
if __name__ == '__main__': main()
