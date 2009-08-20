#!/usr/bin/env python3
# Python 2.6.2
# Name: ballotInfoClasses.py
# Author: Mike Anderson
# Created: Jul 30, 2009
# Purpose: To define the classes pertinent to a BallotInfo record


# Define getter and setter methods for the data members of a ballot info class,
#  namely the ballot info type, the name of the election, and the list of
#  contests.
class Ballot_info(object):
	def __init__(self):
		self.contest_list = []

	def get_type(self):
		return self.type
	def set_type(self, value):
		self.type = value

	def get_election_name(self):
		return self.election_name
	def set_election_name(self, value):
		self.election_name = value

	def get_contest_list(self):
		return self.contest_list
	def set_contest_list(self, value):
		self.contest_list = value


# Define getter and setter methods for the data members of a contest class,
#  namely the list of candidates, the display name, the district id, the
#  unique contest id, the number of open seats, and the voting method.
class Contest(object):
	def __init__(self):
		self.candidate_list = []
	
	def get_candidate_list(self):
		return self.candidate_list
	def set_candidate_list(self, value):
		self.candidate_list = value

	def get_display_name(self):
		return self.display_name
	def set_display_name(self, value):
		self.display_name = value

	def get_district_id(self):
		return self.district_id
	def set_district_id(self, value):
		self.district_id = value

	def get_ident(self):
		return self.ident
	def set_ident(self, value):
		self.ident = value
				
	def get_open_seat_count(self):
		return self.open_seat_count
	def set_open_seat_count(self, value):
		self.open_seat_count = value

	def get_voting_method_id(self):
		return self.voting_method_id
	def set_voting_method_id(self, value):
		self.voting_method_id = value


# Define getter and setter methods for the data members of a candidate class,
#  namely the number of votes, the candidate's name, the candidate's unique id,
#  and the candidate's party.
class Candidate(object):
	def get_count(self):
		return self.count
	def set_count(self, value):
		self.count = value

	def get_display_name(self):
		return self.display_name
	def set_display_name(self, value):
		self.display_name = value

	def get_ident(self):
		return self.ident
	def set_ident(self, value):
		self.ident = value

	def get_party_id(self):
		return self.party_id
	def set_party_id(self, value):
		self.party_id = value
