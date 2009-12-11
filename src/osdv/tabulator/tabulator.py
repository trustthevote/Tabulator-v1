#!/usr/bin/env python
# Python 2.6.2
# Name: tabulator.py
# Author: Mike Anderson
# Created: Aug 5, 2009
# Purpose: To define a class that takes as input a merged BallotInfo
#  file and generates a report

import yaml
import sys
from datetime import date
from plistlib import writePlistToString as xmlSerialize

import audit_header

class Tabulator(object):
    def __init__(self, args):
        self.precs = 0
        # Load ballot records from yaml file
        self.input = args[0]
        try:
            stream = open(self.input + '.yaml', 'r')
        except:
            print('Unable to open ' + self.input + '\n')
            exit(0)
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            self.b = list(yaml.load_all(stream))

        # Load the jurisdiction slate or precinct contestlist template
        try:
            stream = open(args[1] + '.yaml', 'r')
        except:
            print('Unable to open ' + self.input + '\n')
            exit(0)
        else:
            a = audit_header.AuditHeader()
            a.load_from_file(stream)
            self.templ = yaml.load(stream)

        # Add the vote counts of candidates with the same ID# using
        #  sumation(). Write the vote totals for each candidate to the
        #  report stream.
        self.serialize_csv_pvt(self.sumation())
        #self.serialize_pvt(self.sumation())

        """
        # Dump output into a file in yaml format
        stream = open(args[1] + '_report.yaml', 'w') 
        stream.write(self.sumation().serialize_yaml())
        yaml.dump(b, stream)

        # Dump output into a file in XML file
        stream = open(args[1] + '_report.xml', 'w')
        stream.write(self.sumation().serialize_xml())
        stream.writelines(xmlSerialize(b)[173:]. \
            replace('\t', '    ').replace('\n</plist>', ''))
        """

    # Sum up the separate vote counts in each record for each candidate
    #  and return the cumulative result as a dictionary.
    def sumation(self):
        sum_list = {}

        # If the template is a precinct_contestlist, then populate its
        #  precinct_list with only the one precinct

        """
        a = audit_header.AuditHeader()
        a.load_from_file(self.templ)
        if a.type == 'precinct contestlist':
            self.templ['precinct_list'] = []
            self.templ['precinct
        """

        for prec in self.templ['precinct_list']:
            sum_list[prec['display_name']] = {}
            sum_list[prec['display_name']]['Polling'] = {}
            sum_list[prec['display_name']]['Absentee'] = {}
            sum_list[prec['display_name']]['Early Voting'] = {}
            sum_list[prec['display_name']]['Other'] = {}
            sum_list[prec['display_name']]['Totals'] = {}
        for rec in self.b:
            for precinct in self.templ['precinct_list']:
                if precinct['prec_id'] == rec['prec_id']:
                    prec = precinct['display_name']            
            type = rec['vote_type']
            for i in range(len(rec['contests'])):
                cont = rec['contests'][i]
                co_name = cont['contest_id']
                if not sum_list[prec][type].has_key(co_name):
                    sum_list[prec][type][co_name] = {}
                    sum_list[prec][type][co_name]['Total'] = 0
                    sum_list[prec][type][co_name]['Blank'] = 0
                    sum_list[prec][type][co_name]['Over'] = 0
                if not sum_list[prec]['Totals'].has_key(co_name):
                    sum_list[prec]['Totals'][co_name] = {}
                    sum_list[prec]['Totals'][co_name]['Total'] = 0
                    sum_list[prec]['Totals'][co_name]['Blank'] = 0
                    sum_list[prec]['Totals'][co_name]['Over'] = 0
                sum_list[prec][type][co_name]['Total'] += \
                 cont['total_votes']
                sum_list[prec][type][co_name]['Blank'] += \
                 cont['uncounted_ballots']['blank_votes']
                sum_list[prec][type][co_name]['Over'] += \
                 cont['uncounted_ballots']['over_votes']
                sum_list[prec]['Totals'][co_name]['Total'] += \
                 cont['total_votes']
                sum_list[prec]['Totals'][co_name]['Blank'] += \
                 cont['uncounted_ballots']['blank_votes']
                sum_list[prec]['Totals'][co_name]['Over'] += \
                 cont['uncounted_ballots']['over_votes']
                for j in range(len(cont['candidates'])):
                    cand = cont['candidates'][j]
                    ca_name = cand['display_name']
                    if not sum_list[prec][type][co_name].has_key(ca_name):
                        sum_list[prec][type][co_name][ca_name] = 0
                    if not sum_list[prec]['Totals'][co_name].has_key(ca_name):
                        sum_list[prec]['Totals'][co_name][ca_name] = 0
                    sum_list[prec][type][co_name][ca_name] += cand['count']
                    sum_list[prec]['Totals'][co_name][ca_name] += cand['count']
        return sum_list

    # Serialize a list of contests and their respective candidate vote
    #  counts into a .csv & .pvt format, and output each to a file
    def serialize_csv_pvt(self, sum_list):
        s_pvt = open(self.input + '_report_pvt.csv', 'w')
        s_pvt.write('Contest,Precinct,Type,Name,Party,Count,\n')
        stream = open(self.input + '_report.csv', 'w')
        stream.write('Election Summary Report,,\n')
        stream.write(
           'Generated by TrustTheVote Tabulation and Reporting Module,,\n')
        d = date.today()
        stream.write('Report generated on, ' +
                    str(d.month) + '-' + str(d.day) + '-' + str(d.year) + ',\n')
        if self.input.rfind('/') != -1:
            fname = self.input[self.input.rfind('/') + 1:]
        else:
            fname = self.input
        stream.write('Input BallotInfo File, ' + fname + '.yaml,\n')
        stream.write(',,\n')

        for cont in self.templ['contests']:
            co_name = cont['contest_id']
            stream.write(',,\n,TURN OUT,,,' + cont['display_name'].upper() + \
                         ',\n')
            stream.write(',Reg. Voters,Cards Cast,%Turnout,')
            stream.write('Reg. Voters,Times Counted,Total Votes,')
            stream.write('Times Blank Voted,Times Over Voted,')
            for cand in cont['candidates']:
                stream.write(cand['display_name'])
                if cand['display_name'] != 'Write-In Votes':
                    stream.write(',')
                
            stream.write('\n')
            for prec in self.templ['precinct_list']:
                pr_name = prec['display_name']
                stream.write(str(pr_name) + ',\n')
                for type in ['Polling','Absentee','Early Voting','Other','Totals']:
                    if sum_list[pr_name][type].has_key(co_name):
                        temp = sum_list[pr_name][type][co_name]
                    else:
                        continue
                    num_voters = (prec['registered_voters'])
                    cards_cast = temp['Total'] + temp['Blank'] + temp['Over']
                    stream.write(type + ',' + str(num_voters) + ',' + \
                     str(cards_cast) + ',' + \
                     str(int(round(float(cards_cast)/num_voters * 100))) + '%'\
                     ',' + str(num_voters) + ',' + str(cards_cast) + ',' + \
                     str(temp['Total']) + ',' + str(temp['Blank']) + ',' + \
                     str(temp['Over']) + ',')
                    for cand in cont['candidates']:
                        ca_name = cand['display_name']
                        stream.write(str(temp[ca_name]))
                        stream.write(',')
                        if type != ['Totals']:
                            s_pvt.write( co_name + ',' + str(pr_name) + ',' + \
                             type + ',' + ca_name + ',' + cand['party_id']  + \
                             ',' + str(temp[ca_name]) + ',\n')
                    stream.write('\n')
        s_pvt.close()
        stream.close()

def main():
    # Output a usage message if incorrect number of command line args
    if( len(sys.argv) != 3 ):
        print "Usage: [MERGED INPUT FILE][JURISDICTION FILE]"
        exit()

    t = Tabulator(sys.argv[1:])

    print 'SOVC report created in ' + sys.argv[1] + '_report.csv, '
    print sys.argv[1] + '_report_pvt.csv' + sys.argv[1] + '_report.yaml, and '
    print sys.argv[1] + '_report.xml\n'

    return 0

if __name__ == '__main__': main()
