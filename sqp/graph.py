"""
# The null graph:
>>> Node('null node').is_terminal()
1

>>> # An infinitely recursing graph: node1 --> node2 --> node1 --> ...
... n1 = Node("node1")
>>> n2 = Node("node2")
>>> b1 = Branch(next = n2)
>>> b2 = Branch(next = n1)
>>> n1.add(b1)
>>> n2.add(b2)
>>>
>>> print "Node 1 terminal?"
Node 1 terminal?
>>> print n1.is_terminal()
0

>>> # A simple acyclical graph:
... #              --> n3
... #  n1 --> n2 --|
... #              --> n4 --> n5
... n1 = Node('Start')
>>> n2 = Node('Second')
>>> n3 = Node('Third, first')
>>> n4 = Node('Third, second')
>>> n5 = Node('Fourth from Third, second')
>>>
>>> b1 = Branch(next = n2)
>>> b2 = Branch(next = n3)
>>> b3 = Branch(next = n4)
>>> b4 = Branch(next = n5)
>>>
>>> n1.add(b1)
>>> n2.add(b2)
>>> n2.add(b3)
>>> n4.add(b4)
>>>
>>> print n1.is_terminal()
1

>>> # terminal graph with a cycle
>>> #    -> b1 ->  b2 -> b3
>>> # a -|
>>> #    -> c1 -> c2 -> b1
>>>
>>> a = Node('a')
>>> b1 = Node('b1')
>>> b2 = Node('b2')
>>> b3 = Node('b3')
>>> c1 = Node('c1')
>>> c2 = Node('c2')
>>> c3 = Node('c3')
>>>
>>> a.add(Branch(next = b1))
>>> b1.add(Branch(next = b2))
>>> b2.add(Branch(next = b3))
>>>
>>> a.add(Branch(next = c1))
>>> c1.add(Branch(next = c2))
>>> c2.add(Branch(next = b1))
>>>
>>> print a.is_terminal()
1

"""

# Total number of times the recursive function is_terminal has been called:
num_calls = 0 


class Node:
    """A Node is an abstraction that will later be represented by a
    Characteristic. It is found in a Graph, which will be a CharacteristicSet."""
    def __init__(self, name):
        self.name = name
        self.branches = [] 

    def add(self, branch):
        """Adds a branch to this node."""
        self.branches.append(branch)

    def is_terminal(self, seen_nodes = None):
        """Recurses from this node to see if *all* its branches eventually
            end up in a terminal node. Calling this on the source node of a
            graph establishes that the graph is terminal. 
           Returns 1 if yes, 0 if no. """
        if seen_nodes is None: seen_nodes = set() # default arguments are static
        global num_calls # For debugging 
        num_calls += 1

        if self in seen_nodes: # deja vu, we are going in circles
            return 0
        seen_nodes.add(self) 

        num_terminal = 0
        for branch in self.branches:
            if branch.next: # Recurse through this branch
                num_terminal += branch.next.is_terminal(set(seen_nodes)) 
                # note that a _copy_ of seen_nodes is passed.
            else: # Found the terminal node ('sink')
                num_terminal += 1

        if num_terminal == len(self.branches): # all branches are terminal
            return 1
        else: # at least one branch is not terminal or no branches
            return 0


class Branch:
    """A branch is an edge. It is found in a Node and points to what we can only
    hope is another Node."""
    next = False
    
    def __init__(self, next = False):
        self.next = next


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    print "is_terminal() was called a total of %d times."  % num_calls
