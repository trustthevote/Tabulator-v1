#!/usr/bin/env python
# Python 2.6.2
# Name: testDataGenerator.py
# Author: Mike Anderson
# Created: Aug 5, 2009
# Purpose: To define a class that merges multiple ballot records
#  together into one record.

import ballotInfoClasses, yaml, sys

# Checks validity of two ballot record files against some election
#  specs, merges them together, and generates a report.
class Tabulator(object):
	def __init__(self, election_file, record_file1, record_file2,
	             merge_output_file, report_output_file):
		# Open a stream to a report file that will be written to during
		#  the course of tabulation.
		self.rstream = open(report_output_file, 'w')
		
		# Load ballot records from file
		try:
			stream = open(record_file1, 'r')
		except:
			self.rstream.write('Unable to open ' + record_file1 + '\n')
			print('Unable to open ' + record_file1 + '\n')
			exit()
		else:
			self.b1 = []
			self.b1 = yaml.load_all(stream)
		
		try:
			stream = open(record_file2, 'r')
		except:
			self.rstream.write('Unable to open ' + record_file2 + '\n')
			print('Unable to open ' + record_file2 + '\n')
			exit()
		else:
			self.b2 = []
			self.b2 = yaml.load_all(stream)
		
		# Get the election specs from file
		stream = open(election_file, 'r')
		self.e = yaml.load(stream)
			
		# Verify that ballot records match the election specs in file
		self.verify_match_record(election_file)
				
		# Generators were already iterated over by verify_match_record,
		#  so reload.
		stream = open(record_file1, 'r')
		self.b1 = yaml.load_all(stream)
		stream = open(record_file2, 'r')
		self.b2 = yaml.load_all(stream)
		
		# Add the vote counts of candidates with the same ID# using
		#  merge(), and output the results to the given merge file name
		m = self.merge()
		stream = open(merge_output_file, 'w')
		yaml.dump(m, stream)

		# Write the vote totals for each candidate to the report stream
		self.rstream.write('\n')
		for i in range(len(m.get_contest_list())):
			for j in range(len(m.get_contest_list()[i].get_candidate_list())):
				tot = m.get_contest_list()[i].get_candidate_list()[j].get_count()
				name = m.get_contest_list()[i].get_candidate_list()[j].get_display_name()
				self.rstream.write(str(tot) + ' votes found for ' + name + '\n')
		
		# Close any open streams
		stream.close()
		self.rstream.close()
		
	# This function is used to make sure that records in both files are 
	#  consistent with the given election specs.
	def verify_match_record(self, election_file):
		# Match the values in each record from both record files to the
		#  election specs. If any pair of values do not match, return
		#  the number (1 or 2) of the offending record file. Otherwise
		#  return 0
		for b in self.b1:
			if ((b.get_election_name() != self.e.get_election_name()) or
			(len(b.get_contest_list()) != len(self.e.get_contest_list()))):				
				print "First record file did not match election template, merge aborted\n"
				self.rstream.write("First record file did not match election template, merge aborted\n")
				exit()
			for i in range(len(self.e.get_contest_list())):
				if not self.match_contest(self.e.get_contest_list()[i],
				                          b.get_contest_list()[i]):
					print "First record file did not match election template, merge aborted\n"
					self.rstream.write("First record file did not match election template, merge aborted\n")
					exit()
		for b in self.b2:
			if ((b.get_election_name() != self.e.get_election_name()) or
			(len(b.get_contest_list()) != len(self.e.get_contest_list()))):
				print "Second record file did not match election template, merge aborted\n"
				self.rstream.write("Second record file did not match election template, merge aborted\n")
				exit()
			for i in range(len(self.e.get_contest_list())):
				if not self.match_contest(self.e.get_contest_list()[i], 
				                          b.get_contest_list()[i]):
					print "Second record file did not match election template, merge aborted\n"
					self.rstream.write("Second record file did not match election template, merge aborted\n")
					exit()
		self.rstream.write("Both record files matched election template.\n")
				
	# This returns true if the data members of two contests have the
	#  same values. Else returns false.
	def match_contest(self, cont1, cont2):
		if((cont1.get_display_name() != cont2.get_display_name()) or
		(cont1.get_district_id() != cont2.get_district_id()) or
		(cont1.get_ident() != cont2.get_ident()) or
		(cont1.get_open_seat_count() != cont2.get_open_seat_count()) or
		(cont1.get_voting_method_id() != cont2.get_voting_method_id()) or
		(len(cont1.get_candidate_list()) != len(cont2.get_candidate_list()))):
			return False
		for i in range(len(cont1.get_candidate_list())):
			if not self.match_candidate(cont1.get_candidate_list()[i],
			                            cont2.get_candidate_list()[i]):
				return False		
		return True
	
	# This returns true if the data members of two candidates have the
	#  same values (with the exception of count). Else returns false.
	def match_candidate(self, cand1, cand2):
		if((cand1.get_display_name() != cand2.get_display_name()) or
		(cand1.get_ident() != cand2.get_ident()) or
		(cand1.get_party_id() != cand2.get_party_id())):
			return False
		return True
		
	# Sums up the separate vote counts in each record for each candidate
	#  and returns the cumulative result as a ballot_info object.
	def merge(self):
		merge = self.e        # Vote counts of each candidate are 0 in e
		for rec in self.b1:		
			for i in range(len(rec.get_contest_list())):
				for j in range(len(rec.get_contest_list()[i].get_candidate_list())):
					curTot = merge.get_contest_list()[i].get_candidate_list()[j].get_count()					
					addThis = rec.get_contest_list()[i].get_candidate_list()[j].get_count()
					sum = curTot + addThis		
					merge.get_contest_list()[i].get_candidate_list()[j].set_count(sum)					
		for rec in self.b2:
			for i in range(len(rec.get_contest_list())):
				for j in range(len(rec.get_contest_list()[i].get_candidate_list())):
					curTot = merge.get_contest_list()[i].get_candidate_list()[j].get_count()
					addThis = rec.get_contest_list()[i].get_candidate_list()[j].get_count()
					sum = curTot + addThis
					merge.get_contest_list()[i].get_candidate_list()[j].set_count(sum)
		return merge			

def main():
	# Output a usage message if incorrect number of command line args
	if( len(sys.argv) != 6 ):
		print "Usage: [ELECTION SPECS FILE] [BALLOT RECORD1]",
		print "[BALLOT RECORD2] [MERGED OUTPUT FILE]", 
		print "[REPORT OUTPUT FILE]"
		exit()
	
	t = Tabulator(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
	              sys.argv[5])
	
	print "Successfully merged " + sys.argv[2] + " and " + sys.argv[3],
	print "together\n The results are stored in " + sys.argv[4]
	print "A report describing the features of the merge was created",
	print " in " + sys.argv[5]	
	
	return 0
	
if __name__ == '__main__': main()
