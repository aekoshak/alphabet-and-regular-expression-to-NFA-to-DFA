# Name: pa3.py
# Author(s): Abdulqader Koshak		abdulqaderkoshak@sandiego.edu
#			 Noelle Tuchscherer		ntuchscherer@sandiego.edu
#			 Bree Humphrey			bhumphrey@sandiego.edu
# Date: 10/05/2020
# Last Updated: 10/22/2020
# Description: This program takes an alphabet and regular expression from a file and converts it to an NFA, then a DFA.
#			   The program also determines if a string is in the language of a regular expression.

class InvalidExpression(Exception):
	pass

# Takes a value and creates a new tree node for that value
class TreeNode:
	def __init__(self, val, left_child = None, right_child = None):
		self.val = val
		self.left_child = left_child
		self.right_child = right_child
		self.children = [left_child, right_child]
	
	def __str__(self):
		return str(self.val)

class Tree:
	def __init__(self, root = None):
		self.root = root
		self.LIST = []
		
	def depth_first(self):
        # Print out nodes in depth-first fashion.
		self.depth_first_list(self.root)
		return self.LIST

	def depth_first_list(self, node):
		# Print out nodes in the subtree rooted at node,
		# # in depth-first fashion.
		if node != None:
			for child in node.children:
				self.depth_first_list(child)
			self.LIST.append(node.val)	
	
	def depth_first_recursive(self, node):
		# Print out nodes in the subtree rooted at node,
		# # in depth-first fashion.
		if node != None:
			print(node)
			for child in node.children:
				self.depth_first_recursive(child)
			
class RegEx:
	def __init__(self, filename):
		""" 
		Initializes a RegEx object from the specifications
		in the file whose name is filename.
		"""

		self.filename = filename
		file = open(filename, 'r')
		self.alphabet = file.readline().replace("\n", "")
		string = file.readline().replace("\n", "")
		
		operand_stack = []
		operator_stack = []
		
		try:
			# Keep track of the last scanned symbol
			prev_char = '$'
			for chr in string:
				# sKip spaces
				if(chr == ' '):
					continue
				
				# Character is in alphabet or e
				if chr in self.alphabet or chr == 'e':
					# If last scanned symbol was alphabet, or ) do concatenate
					if prev_char in self.alphabet or prev_char == ')':
						left_op = operand_stack.pop()
						new_node = TreeNode('#', left_op, TreeNode(chr))
						operand_stack.append(new_node)
					
					# If last scanned symbol was * do concatenate
					elif prev_char == '*':
						oper = operator_stack.pop()
						left_op = operand_stack.pop()
						new_node = TreeNode(oper, left_op)

						operator_stack.append('#')
						operand_stack.append(new_node)
						operand_stack.append(TreeNode(chr))
					# No concatenate
					else:
						operand_stack.append(TreeNode(chr))
				
				# Character is (
				if chr == ('('):
					# If last symbol scanned was ) or in alphabet, apply concatenate
					if prev_char == ')' or prev_char in self.alphabet:
						operator_stack.append('#')
					
					# If last scanned symbol was * do concatenate
					elif prev_char == '*':
						
						# Make new node
						oper = operator_stack.pop()
						left_op = operand_stack.pop()
						new_node = TreeNode(oper, left_op)

						operator_stack.append('#')
						operand_stack.append(new_node)
							
					operator_stack.append(chr)

				# Character is )
				if chr == (')'):
					while operator_stack[-1] != '(': 
						oper = operator_stack.pop()
						
						# Make new node
						if oper == '*':
							left_op = operand_stack.pop()
							new_node = TreeNode(oper, left_op)
						else:
							right_op = operand_stack.pop()
							left_op = operand_stack.pop()
							
							new_node = TreeNode(oper, left_op, right_op)
						
						operand_stack.append(new_node)
					
					operator_stack.pop()
						

				# Character is * or |
				if chr == ('*') or chr == ('|'):
					#Keep poping opreators while the stack is not empty and last oprator is lowr in precedence
					while len(operator_stack) != 0 and self.precedence(operator_stack[-1], chr):
						oper = operator_stack.pop()
						if oper == '*':
							left_op = operand_stack.pop()
							new_node = TreeNode(oper, left_op)
						else:
							right_op = operand_stack.pop()
							left_op = operand_stack.pop()
						
							new_node = TreeNode(oper, left_op, right_op)
						operand_stack.append(new_node)
					
					operator_stack.append(chr)

				prev_char = chr
				
			# After scanning the string, empty the operator stack
			while len(operator_stack) != 0:
				oper = operator_stack.pop()
				if(oper == '*'):
					left_op = operand_stack.pop()
					new_node = TreeNode(oper, left_op)
				else: 
					right_op = operand_stack.pop()
					left_op = operand_stack.pop()
					new_node = TreeNode(oper, left_op, right_op) 
				operand_stack.append(new_node)
		except IndexError:
			raise InvalidExpression
		
		# Make tree with last prerand
		self.syntaxTree = Tree(operand_stack.pop())

		# Make NFA and converte it to DFA
		nfa =  self.toNFA(self.syntaxTree)
		self.dfa = nfa.toDFA()


	def toNFA(self, tree):
		"""
		Returns a new NFA from RegEx syntax tree
		"""
		treeList = tree.depth_first()
		
		# Initialize empty states to keep track states naming 
		nfa_states = []
		
		# Initialize empty NFA list to keep track of last two created
		nfasList = []
		
		for char in treeList:
			if(char in self.alphabet or char == 'e'):
				# Make new start_state and accept_state
				start_state = str(len(nfa_states) + 1)
				nfa_states.append(start_state)
				accept_state = str(len(nfa_states) + 1)
				nfa_states.append(accept_state)

				# Make NFA with single transition 
				transition = [[start_state, char, accept_state]]
				new_nfa = NFA(self.filename, 2, self.alphabet, transition, start_state, accept_state)
				nfasList.append(new_nfa)

			if(char == '#'):
				
				# Make new nfa out of previous two nfas
				num_states = nfasList[-2].num_states + nfasList[-1].num_states
				start_state = nfasList[-2].starting_state
				accept_state = nfasList[-1].accept_states
				
				# Compinning the two NFA's transitions
				transitions = []
				for tran in nfasList[-2].transitions:
					transitions.append(tran)
				for tran in nfasList[-1].transitions:
					if(tran[0] == nfasList[-1].starting_state):
						tran[0] = nfasList[-2].accept_states

					transitions.append(tran)
				
				# Create new NFA
				new_nfa = NFA(self.filename, num_states, self.alphabet, transitions, start_state, accept_state)
				nfasList.pop()
				nfasList[-1] = new_nfa  

			if(char == '|'):
				# Make new nfa out of previous two nfas
				num_states = nfasList[-2].num_states + nfasList[-1].num_states + 2
				start_state = str(len(nfa_states) + 1)
				nfa_states.append(start_state)
				accept_state = str(len(nfa_states) + 1)
				nfa_states.append(accept_state)

				# Compinning the two NFA's transitions
				transitions = []
				for tran in nfasList[-2].transitions:
					transitions.append(tran)
				for tran in nfasList[-1].transitions:
					transitions.append(tran)
				
				#Create necessary e-transitions
				transitions.append([start_state, 'e', nfasList[-2].starting_state])
				transitions.append([start_state, 'e', nfasList[-1].starting_state])
				transitions.append([nfasList[-2].accept_states, 'e', accept_state])
				transitions.append([nfasList[-1].accept_states, 'e', accept_state])
				
				# Create new NFA
				new_nfa = NFA(self.filename, num_states, self.alphabet, transitions, start_state, accept_state)
				nfasList.pop()
				nfasList[-1] = new_nfa  
		

			if(char == '*'):
				#Make new nfa out of last NFA 
				num_states = nfasList[-1].num_states + 2
				start_state = str(len(nfa_states) + 1)
				nfa_states.append(start_state)
				accept_state = str(len(nfa_states) + 1)
				nfa_states.append(accept_state)
				
				# Add last NFA's transitions
				transitions = []
				for tran in nfasList[-1].transitions:
					transitions.append(tran)
				
				# Create necessary e-transitions
				transitions.append([start_state, 'e', nfasList[-1].starting_state])
				transitions.append([start_state, 'e', accept_state])
				transitions.append([nfasList[-1].accept_states, 'e', accept_state])
				transitions.append([nfasList[-1].accept_states, 'e', nfasList[-1].starting_state])
				
				# Create new NFA
				new_nfa = NFA(self.filename, num_states, self.alphabet, transitions, start_state, accept_state)
				nfasList[-1] = new_nfa	
		
		
		return  new_nfa


	def simulate(self, str):
		"""
		Returns True if the string str is in the language of
		the "self" regular expression.
		"""
		return self.dfa.simulate(str)
		

	def precedence(self, oprator1, oprator2):
		"""
		Returns True if oprator1 is higher in precedence than oprator2 or oprator1 == oprator2.
		Returns False otherwise.
		"""
		if oprator1 == '|' and oprator2 == '|':
			return True
		elif oprator1 == '*' and oprator2 == '*':
			return True
		elif oprator1 == '*' and oprator2 == '|':
			return True
		elif oprator1 == '*' and oprator2 == '#':
			return True
		elif oprator1 == '#' and oprator2 == '#':
			return True
		elif oprator1 == '#' and oprator2 == '|':
			return True
		else:
			return False


# you can add other classes here, including DFA and NFA (modified to suit
# the needs of this project).

class NFA:
	""" Simulates an NFA """

	# Initializes an NFA from nfa_filename and outputs an equivalent DFA
	# to dfa_filename
	def __init__(self, filename, num_states, alphabet, transitions, starting_state, accept_states):
		"""
		Initializes NFA from the file whose name is
		nfa_filename.  (So you should create an internal representation
		of the nfa.)
		"""
		# Initialize num_states
		self.num_states = num_states
		
		# Initialize alphabet
		self.alphabet = alphabet

		# Initialize transitions
		self.transitions = transitions
		
		# Starting state
		self.starting_state = starting_state
		
		# List of all accept states
		self.accept_states = accept_states

		#print(self.transitions)

	# Converts input NFA to an equivalent DFA and writes DFA to dfa_filename
	def toDFA(self):
		"""
		Converts the "self" NFA into an equivalent DFA
		and writes it to the file whose name is dfa_filename.
		The format of the DFA file must have the same format
		as described in the first programming assignment (pa1).
		This file must be able to be opened and simulated by your
		pa1 program.

		This function should not read in the NFA file again.  It should
		create the DFA from the internal representation of the NFA that you 
		created in __init__.
		"""
		# Initialize empty dfa
		dfa_transitions = []
		dfa_states = []
		dfa_accept_states = []

		# Append eclosure of NFA starting state to dfa_states
		starting_stat = self.eclosure(self.starting_state)
		dfa_states.append(starting_stat)			
	
		curr = 0
		# While there is a new state calculate it's transitions
		while curr < len(dfa_states):
			# Don't need transitions from r state
			if dfa_states[curr] == ['r']:
				curr += 1
				continue
			# For symbole in alphabet
			for s in self.alphabet:
				dest_states = []
				# For each transition check if current state can go to some destination state with symbole s
				for state in dfa_states[curr]:
					for tran in self.transitions:
						# Append destination state to the list
						if tran[0] == state and tran[1] == s and tran[2] not in dest_states:
							dest_states.append(tran[2])
				
				# Get eclosure of that destination
				final_dist = self.eclosure(dest_states)
				
				# Append new state
				if final_dist not in dfa_states and len(final_dist) != 0:
					dfa_states.append(final_dist)
				# Append new transition
				if len(final_dist) != 0:
					dfa_transitions.append([dfa_states[curr], s, final_dist])
				# If state dose not go anywhere go to reject state 'r'
				else:
					dfa_transitions.append([dfa_states[curr], s, ['r']])
					if ['r'] not in dfa_states:
						dfa_states.append(['r'])
			curr += 1
			
		# Appending accept DFA accept states	
		for states in dfa_states:
			for state in states:
				if state == self.accept_states:
					if states not in dfa_accept_states:
						dfa_accept_states.append(states)
	
		# Renaming states to 1,2,3,4...
		for transition in dfa_transitions:
			dfa_transitions[dfa_transitions.index(transition)] = [str(dfa_states.index(transition[0]) + 1), transition[1], str(dfa_states.index(transition[2]) + 1)]

		
		# Renaming states to 1,2,3,4...
		for dfa_accept in dfa_accept_states:
			if dfa_accept in dfa_states:
				dfa_accept_states[dfa_accept_states.index(dfa_accept)] = str(dfa_states.index(dfa_accept) + 1)
		
		
		# Write DFA structure to new file
		return DFA(len(dfa_states), self.alphabet, dfa_transitions, '1', dfa_accept_states)

	def eclosure(self, states):
		"""
		Returns the set of states that could be reach from states in "states (argument1)"
		with one or more e-transtions.
		"""
		# Convert state from string form to [string] from
		if isinstance(states, str):
			states = [states]
		
		
		result = []
		
		# Append self to result
		for state in states:
			result.append(state)
		
		# Append all possible e-path
		for state in result:
			for tran in self.transitions:
				if tran[0] == state and tran[1] == 'e':
					result.append(tran[2])
		
		return result


class DFA:
	""" Simulates a DFA """

	def __init__(self,num_states, alphabet, transitions, starting_state, accept_states):
		"""
		Initializes DFA from the file whose name is
		filename
		"""
		#initializing transitiions
		self.transitions =  transitions
		
		#Starting state
		self.starting_state = starting_state

		#List of all accept states
		self.accept_states = accept_states
	
	def simulate(self, str):
		""" 
		Simulates the DFA on input str.  Returns
		True if str is in the language of the DFA,
		and False if not.
		"""
		#Current_state always start from the starting state
		current_state = self.starting_state
		
		#Loop through each char in the sting str
		for ch in str:
			#Loop through each transtiion into the transtions list
			for transition in self.transitions:
				if transition[0] == current_state and transition[1].replace("'", "") == ch:#If we found the right transition 
					current_state = transition[2]#Advance current_state to the next state
					break #Skip to the next char

		#If current_state (Last state) is acceptence state retun True otherwise return False
		for accept in self.accept_states:
			if isinstance(accept, list):
				for each in accept:
					if current_state == each:
						return True

		if current_state in self.accept_states:
			return True
		else:
			return False

