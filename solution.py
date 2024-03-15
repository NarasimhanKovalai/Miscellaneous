from collections import deque
import copy

class StringOperators:    
    disjunction = '\u22C1'
    conjunction = '\u22C0'
    implication = '\u2192'
    double_implication = '\u2194'
    negation  = '\u223c'
    arrow = '\u21D2'

    @staticmethod
    def is_operator(str_value):
        operators = [StringOperators.implication, StringOperators.double_implication, StringOperators.disjunction, StringOperators.conjunction, StringOperators.negation]
        return str_value in operators
    
    @staticmethod
    def precedence_of_operators(operator):
        precedence = { 
            StringOperators.negation: 1,
            StringOperators.disjunction: 2,
            StringOperators.conjunction: 3,
            StringOperators.implication: 4,
            StringOperators.double_implication: 5 
        }
        return precedence.get(operator, -1)

class Brackets:
    round_opening = "("
    round_closing = ")"
    square_opening = "["
    sqaure_closing = "]"
    curly_opening = "{"
    curly_closing = "}"

    @staticmethod
    def is_opening_bracket(s):
        brackets_list = [Brackets.round_opening, Brackets.square_opening, Brackets.curly_opening]
        return s in brackets_list
    
    @staticmethod
    def corresponding_closing_bracket(bracket):
        if bracket == Brackets.round_opening:
            return Brackets.round_closing
        elif bracket == Brackets.curly_opening:
            return Brackets.curly_closing
        elif bracket == Brackets.square_opening:
            return Brackets.sqaure_closing
        return None
    
    @staticmethod
    def append_bracket_at_start_and_end(list):
        result = []
        result.append(Brackets.round_opening)
        result.extend(list)
        result.append(Brackets.round_closing)
        return result

class Node:
    def __init__(self, LHS, RHS) -> None:
        # list of list of strings
        self.LHS = []
        for left in LHS:
            if (left is None) or (not left):
                continue
            else:
                self.LHS.append(left)
        if len(self.LHS) == 0:
            self.LHS.append([])

        # list of list of strings
        self.RHS = []
        for right in RHS:
            if (right is None) or (not right):
                continue
            else:
                self.RHS.append(right)
        if len(self.RHS) == 0:
            self.RHS.append([])
            
        self.left_child = None
        self.right_child = None

    def set_left_child(self, left_child):
        self.left_child = left_child

    def set_right_child(self, right_child):
        self.right_child = right_child

    def get_left_child(self):
        return self.left_child
    
    def get_right_child(self):
        return self.right_child
    
    def strip_left_and_right_handside(self):
        self.strip_for_list_of_list(self.LHS)
        self.strip_for_list_of_list(self.RHS)

    def strip_for_list_of_list(self, list):
        for formula in list:
            if formula is None or len(formula) == 0:
                continue
            initial_value_bracket = Brackets.is_opening_bracket(formula[0])
            while initial_value_bracket:
                initial_symbol= formula[0]
                corresponding_closing_symbol = Brackets.corresponding_closing_bracket(initial_symbol)
                cnt = 1

                need_to_remove = False
                for i in range(1, len(formula)):
                    curr_symbol = formula[i]
                    if curr_symbol == initial_symbol:
                        cnt += 1
                    elif curr_symbol == corresponding_closing_symbol:
                        cnt -= 1

                    if cnt == 0:
                        if  i== (len(formula) - 1):
                            need_to_remove = True
                        break
                if need_to_remove:
                    del formula[0]
                    del formula[len(formula) - 1]
                else:
                    break

                initial_value_bracket = Brackets.is_opening_bracket(formula[0])

    def break_a_formula_into_two_parts_given_index(self, formula, index):
        before_index = formula[:index]
        after_index = formula[index + 1:]
        result = [before_index, after_index]
        return result
    
    # returns the index at which splitting needs to be done
    def splitting_character_index(self, formula):
        stack = []
        result = -1
        for i, symbol in enumerate(formula):
            # check if symbol is an operator
            if StringOperators.is_operator(symbol):
                while stack and (StringOperators.precedence_of_operators(symbol) <= StringOperators.precedence_of_operators(formula[stack[-1]])):
                    result = stack[-1]
                    stack.pop()
                stack.append(i)
            elif symbol =="(":
                stack.append(i)
            elif symbol == ")":
                while stack and formula[stack[-1]] != "(":
                    result = stack[-1]
                    stack.pop()
                stack.pop()

        if stack:
            result = stack[-1]
        stack.clear()

        return result

    def deep_copy_list_of_list(self, input_list):
        result = []
        for formula in input_list:
            result.append(copy.deepcopy(formula))
        return result
    
    def generate_new_formula_for_double_implication(self, first, second):
        first_implication_formula = []
        first_implication_formula.extend(first)
        first_implication_formula.append(StringOperators.implication)
        first_implication_formula.extend(second)

        first_implication_formula = Brackets.append_bracket_at_start_and_end(first_implication_formula)

        second_implication_formula = []
        second_implication_formula.extend(second)
        second_implication_formula.append(StringOperators.implication)
        second_implication_formula.extend(first)

        second_implication_formula = Brackets.append_bracket_at_start_and_end(second_implication_formula)

        result = []
        result.extend(first_implication_formula)
        result.append(StringOperators.conjunction)
        result.extend(second_implication_formula)

        result = Brackets.append_bracket_at_start_and_end(result)
        
        return result

    def break_node_for_left_side(self, left, index):
        broken_formula = self.break_a_formula_into_two_parts_given_index(left, index)
        symbol_on_which_splitting = left[index]
        if symbol_on_which_splitting == StringOperators.double_implication:
            # create one different node, lambda, A <-> B => delta
            #                           lambda, ( A -> B ) and ( B -> A ) => delta

            new_lhs = self.deep_copy_list_of_list(self.LHS)
            new_lhs.remove(left)
            new_formula = self.generate_new_formula_for_double_implication(broken_formula[0], broken_formula[1])
            new_lhs.append(new_formula)

            new_rhs = self.deep_copy_list_of_list(self.RHS)

            new_node = Node(new_lhs, new_rhs)
            node_list = [new_node]

            return node_list
            
        elif symbol_on_which_splitting == StringOperators.implication:
            # create two nodes, A->B => delta
            #       lambda, B => delta
            #       lambda  => A, delta

            new_lhs_first = self.deep_copy_list_of_list(self.LHS)
            new_lhs_first.remove(left)
            new_lhs_first.append(broken_formula[1])

            new_rhs_first = self.deep_copy_list_of_list(self.RHS)
            first_node = Node(new_lhs_first, new_rhs_first)

            new_lhs_second = self.deep_copy_list_of_list(self.LHS)
            new_lhs_second.remove(left)

            new_rhs_second = self.deep_copy_list_of_list(self.RHS)
            new_rhs_second.append(broken_formula[0])
            second_node = Node(new_lhs_second, new_rhs_second)

            node_list = [first_node, second_node]

            return node_list   
        
        elif symbol_on_which_splitting == StringOperators.conjunction:
            # create one other node, lambda, A and B => delta
            #                          lambda, A, B => delta

            new_lhs = self.deep_copy_list_of_list(self.LHS)
            new_lhs.remove(left)
            new_lhs.append(broken_formula[0])
            new_lhs.append(broken_formula[1])

            new_rhs = self.deep_copy_list_of_list(self.RHS)

            new_node = Node(new_lhs, new_rhs)
            node_list = [new_node]

            return node_list
        
        elif symbol_on_which_splitting == StringOperators.disjunction:
            # create two different nodes, lambda, A or B => delta
            #                           lambda, A => delta
            #                           lambda, B => delta

            new_lhs_first = self.deep_copy_list_of_list(self.LHS)
            new_lhs_first.remove(left)
            new_lhs_first.append(broken_formula[0])

            new_rhs_first = self.deep_copy_list_of_list(self.RHS)
            first_node = Node(new_lhs_first, new_rhs_first)

            new_lhs_second = self.deep_copy_list_of_list(self.LHS)
            new_lhs_second.remove(left)
            new_lhs_second.append(broken_formula[1])

            new_rhs_second = self.deep_copy_list_of_list(self.RHS)
            second_node = Node(new_lhs_second, new_rhs_second)

            node_list = [first_node, second_node]

            return node_list  
        
        elif symbol_on_which_splitting == StringOperators.negation:
            # create one other node, lambda, not A => delta
            #                       lambda => A, delta

            #assert not broken_formula[0]
            new_lhs = self.deep_copy_list_of_list(self.LHS)
            new_lhs.remove(left)

            new_rhs = self.deep_copy_list_of_list(self.RHS)
            new_rhs.append(broken_formula[1])

            new_node = Node(new_lhs, new_rhs)
            node_list = [new_node]

            return node_list
        
        else:
            return None
        
    def break_node_for_right_side(self, right, index):
        broken_formula = self.break_a_formula_into_two_parts_given_index(right, index)
        symbol_on_which_splitting = right[index]

        if symbol_on_which_splitting == StringOperators.double_implication:
            # create one different node, lambda => A <-> B, delta
            #                           lambda => ( A -> B ) and ( B -> A ), delta

            new_lhs = self.deep_copy_list_of_list(self.LHS)

            new_rhs = self.deep_copy_list_of_list(self.RHS)
            new_rhs.remove(right)
            new_formula = self.generate_new_formula_for_double_implication(broken_formula[0], broken_formula[1])
            new_rhs.append(new_formula)
            new_node = Node(new_lhs, new_rhs)
            node_list = [new_node]

            return node_list
        
        elif symbol_on_which_splitting == StringOperators.implication:
            # create one different node, lambda => A->B, delta
            #                           lambda, A => B, delta

            new_lhs = self.deep_copy_list_of_list(self.LHS)
            new_lhs.append(broken_formula[0])

            new_rhs = self.deep_copy_list_of_list(self.RHS)
            new_rhs.remove(right)
            new_rhs.append(broken_formula[1])

            new_node = Node(new_lhs, new_rhs)
            node_list = [new_node]

            return node_list
        
        elif symbol_on_which_splitting == StringOperators.conjunction:
            # create two different nodes, lamba => A and B, delta
            #                           lambda => A, delta
            #                           lambda => B, delta

            new_lhs_first = self.deep_copy_list_of_list(self.LHS)
            
            new_rhs_first = self.deep_copy_list_of_list(self.RHS)
            new_rhs_first.remove(right)
            new_rhs_first.append(broken_formula[0])

            first_node = Node(new_lhs_first, new_rhs_first)

            new_lhs_second = self.deep_copy_list_of_list(self.LHS)

            new_rhs_second = self.deep_copy_list_of_list(self.RHS)
            new_rhs_second.remove(right)
            new_rhs_second.append(broken_formula[1])

            second_node = Node(new_lhs_second, new_rhs_second)
            node_list = [first_node, second_node]

            return node_list
        
        elif symbol_on_which_splitting == StringOperators.disjunction:
            # create one different node, lambda => A or B, delta
            #                            lamba => A, B, delta

            new_lhs = self.deep_copy_list_of_list(self.LHS)

            new_rhs = self.deep_copy_list_of_list(self.RHS)
            new_rhs.remove(right)
            new_rhs.append(broken_formula[0])
            new_rhs.append(broken_formula[1])

            new_node = Node(new_lhs, new_rhs)
            node_list = [new_node]

            return node_list

        elif symbol_on_which_splitting == StringOperators.negation:
            # create a different node, lambda => not A, delta
            #                           lambda, A => delta

            # assert not broken_formula[0]

            new_lhs = self.deep_copy_list_of_list(self.LHS)
            print(f"Hello  {broken_formula}")
            new_lhs.append(broken_formula[1])

            new_rhs = self.deep_copy_list_of_list(self.RHS)
            new_rhs.remove(right)

            new_node = Node(new_lhs, new_rhs)
            node_list = [new_node]

            return node_list
        
        else:
            return None
        
    def get_new_nodes(self):
        # loop on left
        for left in self.LHS:
            index_of_splitting = self.splitting_character_index(left)

            if index_of_splitting < 0:
                # no splitting
                continue
            result = self.break_node_for_left_side(left, index_of_splitting)
            assert result is not None

            for node in result:
                node.strip_left_and_right_handside()
            return result
        
        # loop on right
        for right in self.RHS:
            index_of_splitting = self.splitting_character_index(right)

            if index_of_splitting < 0:
                # no splitting
                continue
            result = self.break_node_for_right_side(right, index_of_splitting)
            assert result is not None

            for node in result:
                node.strip_left_and_right_handside()
            return result
        
        # returns an empty list
        return []

    def is_leaf_node(self):
        for left in self.LHS:
            if len(left) > 1:
                return False
            
        for right in self.RHS:
            if len(right) > 1:
                return False
            
        return True

    def is_contradiction(self):
        if self.is_leaf_node():
            for left in self.LHS:
                if left in self.RHS:
                    return True
                
        return False
    
    def __str__(self):
        return f"{self.LHS} {StringOperators.arrow} {self.RHS}"

class GentzensTree:
    def __init__(self, expression):
        LHS = []
        RHS = []
        RHS.append(expression)

        self.root_node = Node(LHS, RHS)
        self.root_node.strip_left_and_right_handside()
        self.leaf_nodes = []

    def algorithm_for_gentzen_system_creating_tree(self):
        unserved_nodes = deque()
        unserved_nodes.append(self.root_node)

        while unserved_nodes:
            curr_node = unserved_nodes.popleft()

            new_nodes_for_curr = curr_node.get_new_nodes()
            assert len(new_nodes_for_curr) <= 2

            if len(new_nodes_for_curr) == 0 :
                self.leaf_nodes.append(curr_node)
            elif len(new_nodes_for_curr) == 1:
                curr_node.set_left_child(new_nodes_for_curr[0])
            elif len(new_nodes_for_curr) == 2:
                curr_node.set_left_child(new_nodes_for_curr[0])
                curr_node.set_right_child(new_nodes_for_curr[1])

            unserved_nodes.extend(new_nodes_for_curr)

    def print_tree(self):
        print("BFS on Gentzen's Proof Tree: \n")
        q = deque()
        q.append(self.root_node)

        while q:
            curr = q.popleft()
            print(curr)
            print()

            if curr.get_left_child() is not None:
                q.append(curr.get_left_child())
            
            if curr.get_right_child() is not None:
                q.append(curr.get_right_child())

    def contradicting_node(self):
        for node in self.leaf_nodes:
            if node.is_contradiction():
                return node        
        return None
    
    def print_contradicting_node(self):
        print(f"Contradicting Node: {self.contradicting_node()}")

    def check_contradiction(self):
        return self.contradicting_node() is not None
    
    def check_satisfiability(self):
        return self.check_contradiction is not None

def read_and_parse_input():
        try: 
            input_list = input("Enter the expression: ")
            input_list = input_list.split()
            inputs = [s for s in input_list if s]
            if inputs:
                return inputs
            else:
                return []
        except Exception as e:
            print(f"invalid input: {e}")
            return None

def print_available_operators():
    print("")
    print("---------------------------------------------------------------------------")
    print("Operator Domain available: ")
    print(f"Negation: {StringOperators.negation}")
    print(f"Conjunction: {StringOperators.conjunction}")
    print(f"Disjunction: {StringOperators.disjunction}")
    print(f"Implication: {StringOperators.implication}")
    print(f"Double-Implication: {StringOperators.double_implication}")
    print(f"Express other operators using above operators..")
    print("---------------------------------------------------------------------------")
    print("")

def main():
    print_available_operators()
    input_exp = read_and_parse_input()

    print("\nInput Expression: ", *input_exp )
    print("")

    gentzen_tree = GentzensTree(input_exp)

    print("Resolving using Gentzens rules.............................................\n")
    gentzen_tree.algorithm_for_gentzen_system_creating_tree()
    gentzen_tree.print_tree()

    print(f"Leaf Node Contradictions (IF ANY): {gentzen_tree.contradicting_node()}")
    print()
    if gentzen_tree.check_contradiction() == True:
        gentzen_tree.print_contradicting_node()
        print()
        print("NOT SATISFIABLE")
    else:
        print("SATISFIABLE")
        print()
    print("---------------------------------------------------------------------------")
    
if __name__ == "__main__":
    main()
    