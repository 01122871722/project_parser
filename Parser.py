import re
import sys
from collections import defaultdict
from graphviz import Digraph

def is_simple_grammar(rules):
    terminal_mapping = defaultdict(set)
    for non_terminal, productions in rules.items():
        for production in productions:
            if production == "":
                return False  # No epsilon allowed
            if production[0].isupper():
                return False  # Production cannot start with a non-terminal
            for terminal in production:
                if terminal.islower():
                    terminal_mapping[non_terminal].add(terminal)
                elif terminal == non_terminal:
                    return False  # Left recursion not allowed
        if len(terminal_mapping[non_terminal]) != len(set(terminal_mapping[non_terminal])):
            return False  # Non-terminal maps to overlapping terminals
    return True

def build_parser_tree(tree, current, production, node_counter):
    for symbol in production:
        if symbol.isupper():
            new_node = f"{symbol}_{node_counter[0]}"
            tree.node(new_node, symbol)
            tree.edge(current, new_node)
            node_counter[0] += 1
            build_parser_tree(tree, new_node, grammar[symbol][0], node_counter)
        else:
            leaf_node = f"{symbol}_{node_counter[0]}"
            tree.node(leaf_node, symbol)
            tree.edge(current, leaf_node)
            node_counter[0] += 1

def parse_string(input_string, grammar, start_symbol):
    def parse(non_terminal, index):
        if index > len(input_string):
            return False, index

        for production in grammar.get(non_terminal, []):
            temp_index = index
            matched = True
            for symbol in production:
                if symbol.isupper():
                    success, temp_index = parse(symbol, temp_index)
                    if not success:
                        matched = False
                        break
                elif temp_index < len(input_string) and input_string[temp_index] == symbol:
                    temp_index += 1
                else:
                    matched = False
                    break
            if matched:
                return True, temp_index
        return False, index

    success, final_index = parse(start_symbol, 0)
    return success and final_index == len(input_string)

grammar = defaultdict(list)
while True:
    print("\n\U0001F4DA Grammars \U0001F4DA")
    grammar.clear()
    try:
        num_rules = int(input("Enter the number of rules: "))
        if num_rules <= 0:
            print("Number of rules must be positive.")
            continue
    except ValueError:
        print("Invalid input. Enter a valid number.")
        continue

    for _ in range(num_rules):
        try:
            rule_input = input("Enter rule (Format: S -> aB): ").strip()
            if "->" not in rule_input:
                print("Invalid rule format. Use S -> aB.")
                break
            non_terminal, productions = map(str.strip, rule_input.split("->"))
            if not non_terminal.isupper():
                print("Non-terminal must be an uppercase letter.")
                break
            for production in productions.split("/"):
                production = production.strip()
                if production and production[0].isupper():
                    print("Grammar rejected: Production cannot start with a non-terminal.")
                    grammar.clear()
                    break
                grammar[non_terminal].append(production)
        except Exception as e:
            print(f"Error: {e}")
            break

    if not grammar:
        continue

    if not is_simple_grammar(grammar):
        print("The Grammar isn't simple. Try again.")
        continue

    print("Grammar is simple.")
    start_symbol = input("Enter the start symbol: ").strip()
    if start_symbol not in grammar:
        print("Start symbol must be in the grammar.")
        continue

    while True:
        print("\n1- Another Grammar\n2- Another String\n3- Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            break
        elif choice == "2":
            string = input("Enter the string to be checked: ").strip()
            if not string:
                print("String cannot be empty.")
                continue
            input_string = list(string)

            accepted = False
            for production in grammar[start_symbol]:
                if parse_string(input_string, {**grammar, start_symbol: [production]}, start_symbol):
                    accepted = True
                    break
            if accepted:
                print("Your input String is Accepted.")
                tree = Digraph()
                tree.node("root", start_symbol)
                build_parser_tree(tree, "root", grammar[start_symbol][0], [1])
                tree.render("parser_tree", format="png", cleanup=True)
                print("Parser Tree generated: parser_tree.png")
            else:
                print("Your input String is Rejected.")
        elif choice == "3":
            print("Exiting program...")
            sys.exit()
        else:
            print("Invalid choice. Try again.")
