#!/usr/bin/env python
# Python 2.6.2
# Name: test_data_generator.py
# Author: Mike Anderson
# Created: Jul 30, 2009
# Purpose: To generate test files for the ballot tabulator

import random
import yaml
import sys
import copy
import uuid

import ballot_info_classes

# Provides random election specs or random ballot counts
class ProvideRandomBallots(object):
    # Takes as its arguments the type of random data to generate
    def __init__(self, type, args):
        # These variables are used to ensure that if the same random
        #  data is generated in some circumstances, it will not appear
        #  twice in the template.
        self.already_used_streps = []
        self.already_used_dreps = []
        self.already_used_names = []
        self.already_used_cand_idents = []
        self.already_used_cont_did = []
        self.already_used_supreme = False
        
        if type == 'election':
            # Generate a sample election and output it to the location
            #  specified by the user in the command line, in yaml format.        
            b = ballot_info_classes.BallotInfo()
            stream = open(args[0], 'w') 
            
            # Give each file its own GUID header            
            stream.write("GUID: " + str(uuid.uuid1()) + '\n\n')
            
            b = self.random_elec()
            b.set_type("election")
            yaml.dump(b, stream)
        elif type == 'counts':
            # Load election specs from given file in yaml format     
            stream = open(args[1], 'r')
            stream.readline()
            stream.readline() # Skip past the audit header
            e = yaml.load(stream)
            e.set_type("precinct_contestlist")
        
            # Make the number of random ballot_info records specified by
            #  the user. Use the loaded election specs as a template,
            #  assign the vote counts of each candidate a value between 
            #  0 and 99.
            b_list = []
            for i in range(0, int(args[0])):
                b = copy.deepcopy(e)                
                for j in range(0, len(b.get_contest_list())):
                    for k in range(0, len(b.get_contest_list()[j].get_candidate_list())):
                        r = random.randint(0,99)
                        b.get_contest_list()[j].get_candidate_list()[k].set_count(r)
                b_list.append(b)
            
            # Store the results in yaml format back into the specified 
            #  file. Any existing file with the given filename will be 
            #  overwritten.
            stream = open(args[2], 'w')

            # Give each file its own GUID header
            stream.write("GUID: " + str(uuid.uuid1()) + '\n\n')

            yaml.dump_all(b_list, stream)
        else:
            exit()
    
    # Makes and returns a ballot of precinct_contestlist type with
    #  initialized data members
    def random_elec(self):        
        self.cand_num = 1
                
        b = ballot_info_classes.BallotInfo()     
        
        # Make the election headliner some random presidential election
        r = random.randint(0,3)
        b.set_election_name(str(r*4+2000) + " Presidential")        
        
        # Generate a few contests
        r = random.randint(2,5)
        for i in range(0,r):
            list = b.get_contest_list()
            list.append(self.random_contest())
            b.set_contest_list(list)
        return b

    # Makes and returns a contest object with initialized data members
    def random_contest(self):
        cont = ballot_info_classes.Contest()

        # Generate a few candidates per contest
        r = random.randint(3,5)
        for i in range(0,r):
            list = cont.get_candidate_list()
            list.append(self.random_candidate())
            cont.set_candidate_list(list)
        
        # Make sure that a maximum of one supreme court justice contest
        #  is generated.
        if self.already_used_supreme:
            r = random.randint(1,2)
        else:
            r = random.randint(1,3)
        
        # Generate a random type of race
        if r == 1:
            cont.set_display_name("Representative in Congress")

            # Generate random values for the dist number until an unused
            #  number is generated. Once this is successful, use the
            #  unused number and add it to a list of used numbers.
            while True:
                r = random.randint(1,9)
                if self.already_used_dreps.count(r) == 0:
                    self.already_used_dreps.append(r)
                    if r == 1:
                        cont.set_ident("Rep1stDistrict")
                    elif r == 2:
                        cont.set_ident("Rep2ndDistrict")
                    elif r == 3:
                        cont.set_ident("Rep3rdDistrict")
                    else:
                        cont.set_ident("Rep"+str(r)+"thDistrict")
                    break
        elif r == 2:
            cont.set_display_name("State Representative")
            
            # Generate random values for the House number until an unused
            #  number is generated. Once this is successful, use the
            #  unused number and add it to a list of used numbers.
            while True:
                r = random.randint(1,9)
                if self.already_used_streps.count(r) == 0:
                    self.already_used_streps.append(r)
                    if r == 1:
                        cont.set_ident("StateRep1stHouse")
                    elif r == 2:
                        cont.set_ident("StateRep2ndHouse")
                    elif r == 3:
                        cont.set_ident("StateRep3rdHouse")
                    else:
                        cont.set_ident("StateRep"+str(r)+"thHouse")                 
                    break
        else:
            cont.set_display_name("Supreme Court Justice")
            cont.set_ident("JustSupCrt")
            self.already_used_supreme = True
    
        r = random.randint(1,2)
        cont.set_open_seat_count(r)
        
        # The district number and the voting machine number are 
        #  randomly generated.
        while True:
            r = random.randint(10,99)
            if self.already_used_cont_did.count(r) == 0:
                self.already_used_cont_did.append(r)
                cont.set_district_id("DIST-" + str(r))
                break           
        cont.set_voting_method_id("VOTM-" + str(random.randint(1,5)))        
        
        return cont

    # Makes and returns a candidate object with initialized data members
    def random_candidate(self):
        cand = ballot_info_classes.Candidate()        
        
        # Count just gets a null value, since it is irrelevant to the
        #  specs generated here.
        cand.set_count(0)
        
        cand.set_display_name(self.random_fullname())
        while True:
            r = random.randint(100,999)
            if self.already_used_cand_idents.count(r) == 0:
                self.already_used_cand_idents.append(r)
                cand.set_ident("CAND-" + str(r))
                break           
        cand.set_party_id("PART-" + str(random.randint(1,9)))       
        
        return cand
    
    # Makes and returns a random full name string
    def random_fullname(self):
        # A pool of first and last names to choose from
        first_name_list = ['Adam', 'Barbara', 'Corey', 'Derek', 'Emily',
                           'Frank', 'Greg', 'Harriet', 'Ilsie', 'Joey']
        last_name_list = ['Anders', 'Brenner', 'Callihan', 'Davis',
                          'Elmhurst', 'Fawcett', 'Garrison', 'House',
                          'Imamura', 'Jackson']
        
        # Generate a first and last name combination
        fname = first_name_list[random.randint(0,9)]
        lname = last_name_list[random.randint(0,9)]
        fullname = fname + ' ' + lname
        
        if self.already_used_names.count(fullname) == 0:
            self.already_used_names.append(fullname)
            return fullname
        else:
            return(self.random_fullname())      

def main(): 
    # First make sure that the command line input is valid. If it is not
    #  then output a usage statement and exit    
    if len(sys.argv) == 1: sys.argv.append("")
    type = sys.argv[1]
    if sys.argv[1] == "election":
        if len(sys.argv) != 3:
            print "Usage: test_data_generator.py election [OUTPUT ELECTION FILE]"
            print "   OR: test_data_generator.py counts [#  OF SAMPLES]",
            print "[INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]"
            exit()
    elif sys.argv[1] == "counts":
        if len(sys.argv) != 5:
            print "Usage: test_data_generator.py election [OUTPUT ELECTION FILE]"
            print "   OR: test_data_generator.py counts [#  OF SAMPLES]",
            print "[INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]"
            exit()
    else:
        print "Usage: test_data_generator.py election [OUTPUT ELECTION FILE]"
        print "   OR: test_data_generator.py counts [#  OF SAMPLES]",
        print "[INPUT ELECTION FILE] [OUTPUT SAMPLES FILE]"
        exit()
    
    # Get rid of unneccesary command line arguments and generate random
    #  data of the specified type
    args = sys.argv[2:]
    p = ProvideRandomBallots(type, args)
    
    if sys.argv[1] == "election":
        print "Done. Generated sample election template file",
        print sys.argv[2] + "\n"
    else:
        print "Done. Generated sample ballot file",
        print sys.argv[4] + "\n"

    return 0
    
if __name__ == '__main__': main()
