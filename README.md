# fa.py

A barebones Python library for manipulating deterministic and non-determinstic finite automata. Made for [CS420 @ UMB](https://www.cs.umb.edu/~stchang/cs420/f20/ "CS420").

`fa.py` can...
* import and export [JFLAP](http://www.jflap.org/ "JFLAP")-compatible XML
* validate whether a string is accepted by an automaton
* perform union, concatenation, and Kleene star operations
* be used to construct languages recognized by regular expressions


## Usage

### Initialization
```python
from fa import FA
```


### Creation
```python
nfa = FA(states, alphabet, transitions, start_state, accept_states, [prefix])
```
* `states` and `alphabet` must be **sets** of string(s).

* `transitions` must be a triple-nested dictionary. For example...
```python
{ "q1":
	{ "char":
		{ "q2", "q3" }
	}
}
```
...describes one non-deterministic transition from the state **q1** to either states **q2** or **q3** given an input of **char**. To manually represent epsilon transitions, use **ε**.

* `start_state` must be a string in `states`.

* `accept_states` must be a set of string(s) in `states`.

* `prefix` is an optional string that will be placed in front of all states.


### Validation
Validates whether the given string is in an automaton's language.
```python
nfa.validate(string)
```


### Operations

#### Union
Creates a new automaton that recognizes the union of two languages.
```python
nfa = FA.union(a, b)
```

#### Concatenation
Creates a new automaton that recognizes the concatenation of two languages.
```python
nfa = FA.concat(a, b)
```

#### Kleene star
Creates a new automaton that recognizes the Kleene closure of a language.
```python
nfa = FA.star(nfa)
```


### Resolving conflicts
Performing union and concatenation operations on two automata requires that the names of their states do not overlap.

#### Randomize
Adds a unique `prefix` to each state in an automaton's `states` if it was not specified during [creation](#Creation) or [import](#Import). If a prefix is not explicitly passed to the function, it will use a randomly generated integer between 0 and 100.
```python
FA.randomize(nfa, [prefix])
```

#### Unrandomize
Removes the `prefix` from an automaton's `states`.
```python
FA.unrandomize(nfa)
```


### XML

#### Import
Generates an automaton object from the specified JFLAP-compatible XML file (see [here](http://www.jflap.org/modules/JFLAPWorkshop2014/Upload%20Exercises%20and%20Modules%20here/JodyPaul/Modules/DFA_a.jff "here") for an example).
```python
nfa = FA.import(file, [prefix])
```

#### Export
Generates a JFLAP-compatible XML file from an automaton object. If the `file` path is not specified, the XML is output to the command line.
```python
FA.export([file])
```
