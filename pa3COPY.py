# Name: pa3.py
# Author(s): Abdulqader Koshak		abdulqaderkoshak@sandiego.edu
#			 Noelle Tuchscherer		ntuchscherer@sandiego.edu
#			 Bree Humphrey			bhumphrey@sandiego.edu
# Date: 10/05/2020
# Last Updated: 10/21/2020
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
			#Keep track of the last scanned symbol
			prev_char = '$'
			for chr in string:
				#If two alphabet chars are scanned in a row, apply concatenate
				#If ) then ( is scanned, apply concatenate
				if chr in self.alphabet or chr == 'e':
					#If last scanned symbol was alphabet, do concatenate
					if prev_char in self.alphabet:
						left_op = operand_stack.pop()
						new_node = TreeNode('.', left_op, TreeNode(chr))
						operand_stack.append(new_node)
					elif prev_char == '*':
						oper = operator_stack.pop()
						left_op = operand_stack.pop()
						new_node = TreeNode(oper, left_op)
						operator_stack.append('.')
						operand_stack.append(new_node)
						operand_stack.append(TreeNode(chr))
					else:
						operand_stack.append(TreeNode(chr))
				
				if chr == ('('):
					#If last symbol scanned was ), apply concatenate
					if prev_char == ')':
						right_op = operand_stack.pop()
						left_op = operand_stack.pop()
						
						new_node = TreeNode('.', left_op, right_op)
						operand_stack.append(new_node)
					else:
						operator_stack.append(chr)

				if chr == (')'):
					while operator_stack[-1] != '(': 
						oper = operator_stack.pop()
						if(oper == '*' and len(operand_stack) == 1):
							left_op = operand_stack.pop()
							new_node = TreeNode(oper, left_op)
						else:
							right_op = operand_stack.pop()
							left_op = operand_stack.pop()
							
							new_node = TreeNode(oper, left_op, right_op)
							operand_stack.append(new_node)
					operator_stack.pop()
						

				if chr == ('*') or chr == ('|'):
					if len(operator_stack) != 0 and self.precedence(operator_stack[-1], chr):
						oper = operator_stack.pop()
						if(oper == '*' and len(operand_stack) == 1):
							left_op = operand_stack.pop()
							new_node = TreeNode(oper, left_op)
						else:
							right_op = operand_stack.pop()
							left_op = operand_stack.pop()
						
							new_node = TreeNode(oper, left_op, right_op)
						operand_stack.append(new_node)
					
					operator_stack.append(chr)

				prev_char = chr
				
			#After scanning the string, empty the operator stack
			#NEED TO HANDLE STRINGS LIKE a* WITH ONLY ONE OPERAND
			while len(operator_stack) != 0:
				oper = operator_stack.pop()
				if(oper == '*'):		# and len(operand_stack) == 1  <- I don't think we need this in the if statement
					left_op = operand_stack.pop()
					new_node = TreeNode(oper, left_op)
				else: 
					right_op = operand_stack.pop()
					left_op = operand_stack.pop()
					new_node = TreeNode(oper, left_op, right_op) 
				operand_stack.append(new_node)
		except IndexError:
			raise InvalidExpression
		
		self.syntaxTree = Tree(operand_stack.pop())
		#self.syntaxTree.depth_first()
	
		

		nfa =  self.toNFA(self.syntaxTree)
		self.dfa = nfa.toDFA()


	def toNFA(self, tree):

		treeList = tree.depth_first()
		print(treeList)
		
		nfa_states = []
		nfasList = []
		for char in treeList:
			if(char in self.alphabet or char == 'e'):
				
				start_state = str(len(nfa_states) + 1)
				nfa_states.append(start_state)
				accept_state = str(len(nfa_states) + 1)
				nfa_states.append(accept_state)

				transition = [[start_state, char, accept_state]]
				new_nfa = NFA(self.filename, 2, self.alphabet, transition, start_state, accept_state)
				nfasList.append(new_nfa)

			if(char == '.'):
				#Make new nfa out of previous two nfas
				num_states = nfasList[-2].num_states + nfasList[-1].num_states
				start_state = nfasList[-2].starting_state
				accept_state = nfasList[-1].accept_states
				transitions = []
				for tran in nfasList[-2].transitions:
					transitions.append(tran)
				for tran in nfasList[-1].transitions:
					tran[0] = nfasList[-2].accept_states
					transitions.append(tran)

				new_nfa = NFA(self.filename, num_states, self.alphabet, transitions, start_state, accept_state)
				nfasList.pop()
				nfasList[-1] = new_nfa  

			if(char == '|'):
				#Make new nfa out of nfa1 and nfa2
				num_states = nfasList[-2].num_states + nfasList[-1].num_states + 2
				start_state = str(len(nfa_states) + 1)
				nfa_states.append(start_state)
				accept_state = str(len(nfa_states) + 1)
				nfa_states.append(accept_state)


				transitions = []
				for tran in nfasList[-2].transitions:
					transitions.append(tran)
				for tran in nfasList[-1].transitions:
					transitions.append(tran)
				transitions.append([start_state, 'e', nfasList[-2].starting_state])
				transitions.append([start_state, 'e', nfasList[-1].starting_state])
				transitions.append([nfasList[-2].accept_states, 'e', accept_state])
				transitions.append([nfasList[-1].accept_states, 'e', accept_state])
				
				new_nfa = NFA(self.filename, num_states, self.alphabet, transitions, start_state, accept_state)
				nfasList.pop()
				nfasList[-1] = new_nfa  
		

			if(char == '*'):
				#Make new nfa out of nfa2
				num_states = nfasList[-1].num_states + 2
				start_state = str(len(nfa_states) + 1)
				nfa_states.append(start_state)
				accept_state = str(len(nfa_states) + 1)
				nfa_states.append(accept_state)
				
				# accept_states = nfasList[-1].start_state + nfasList[-1].accept_states
				transitions = []
				for tran in nfasList[-1].transitions:
					transitions.append(tran)
				transitions.append([start_state, 'e', nfasList[-1].starting_state])
				transitions.append([start_state, 'e', accept_state])
				transitions.append([nfasList[-1].accept_states, 'e', accept_state])
				transitions.append([nfasList[-1].accept_states, 'e', nfasList[-1].starting_state])
				
				new_nfa = NFA(self.filename, num_states, self.alphabet, transitions, start_state, accept_state)
				nfasList[-1] = new_nfa	
		
		#	treeList.remove(char)
	#	print(new_nfa.transitions)
	#	print(new_nfa.num_states)
	#	print(new_nfa.starting_state)
	#	print(new_nfa.accept_states)
		
		return  new_nfa


	def simulate(self, str):
		"""
		Returns True if the string str is in the language of
		the "self" regular expression.
		"""
		return self.dfa.simulate(str)
		

	def precedence(self, oprator1, oprator2):
		if oprator1 == '|' and oprator2 == '|':
			return True
		elif oprator1 == '*' and oprator2 == '*':
			return True
		elif oprator1 == '*' and oprator2 == '|':
			return True
		elif oprator1 == '*' and oprator2 == '.':
			return True
		elif oprator1 == '.' and oprator2 == '.':
			return True
		elif oprator1 == '|' and oprator2 == '.':
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
		# Open file and initialize variables
		self.num_states = num_states
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
	
		dfa_transitions = []
		dfa_states = []
		dfa_accept_states = []
		
		# Determine DFA start state
		start_state = []
		start_state.append(self.starting_state)
		for start in start_state:
			for tran in self.transitions:
				if tran[0] == start and tran[1] == 'e':
					if tran[2] not in start_state:
						start_state.append(tran[2])

		# Add start state to DFA
		dfa_states.append(start_state)
		
		# Determine rest of DFA states			
		for states in dfa_states:
			for s in self.alphabet:
				if s == '\n':
					continue
				states_subset = []
				for state in states:
					for tran in self.transitions:
						# Add all possible states from current state scanning s
						if tran[0] == state and tran[1] == s:
							if tran[2] not in states_subset:
								states_subset.append(tran[2])
						# Add all possible states reachable from an epsilon transition
						if tran[0] == state and tran[1] == 'e':
							eps = tran[2]
							for tran in self.transitions:
								if tran[0] == eps and tran[1] == s:
									if tran[2] not in states_subset:
										states_subset.append(tran[2])
								else:
									if state not in dfa_accept_states and eps in dfa_accept_states:
										dfa_accept_states.append(state)
									if state not in dfa_accept_states and eps==self.accept_states:
										dfa_accept_states.append(state)
				
				# If the new set of sub states is not in the DFA, add it to DFA
				if len(states_subset) != 0 and states_subset not in dfa_states:
					dfa_states.append(states_subset)
				if len(states_subset) != 0:
					new_tran = [states, s, states_subset]
					if new_tran not in dfa_transitions:
						dfa_transitions.append(new_tran)
				# Add a reject state for cases where the string extends beyond an accept
				# state with no pre-existing transitions out
				elif len(states_subset) == 0:
					new_tran = [states, s, ['r']]
					if new_tran not in dfa_transitions:
						dfa_transitions.append(new_tran)
					if ['r'] not in dfa_states:
						dfa_states.append(['r'])
		
		# Determine DFA accept states
		dfa_accept_states.append(self.accept_states)

		for states in dfa_states:
			for state in states:
				if state in dfa_accept_states:
					if states not in dfa_accept_states:
						dfa_accept_states.append(states)
					
		#print(dfa_transitions)
		#print(self.starting_state)
		#print(dfa_accept_states)
		#print(self.accept_states)


		# Write DFA structure to new file
		return DFA(len(dfa_states), self.alphabet, dfa_transitions, self.starting_state , dfa_accept_states)



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
				if transition[0][0] == current_state and transition[1].replace("'", "") == ch:#If we found the right transition 
					current_state = transition[2][0]#Advance current_state to the next state
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


if __name__ == "__main__":
	RegEx("regex6.txt")