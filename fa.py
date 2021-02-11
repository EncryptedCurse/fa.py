class FA:
    def __init__(self, states, alphabet, transition, start, accept, prefix=''):
        self.states = states
        self.alphabet = alphabet
        self.transition = transition
        self.start = start
        self.accept = accept
        self.prefix = prefix


    def randomize(lang, prefix=''):
        import random
        if not prefix:
            prefix = str(random.randint(0, 100))

        lang.states = {prefix + state for state in lang.states}
        lang.transition = {
                            prefix + before:
                                {
                                    char:
                                        {
                                            prefix + state for state in after
                                        }
                                    for (char, after) in transitions.items()
                                }
                            for (before, transitions) in lang.transition.items()
                         }
        lang.start = prefix + lang.start
        lang.accept = {prefix + state for state in lang.accept}
        lang.prefix = prefix
        return lang


    def unrandomize(lang):
        def remove_prefix(string):
            return string[string.startswith(lang.prefix) and len(lang.prefix):]

        if lang.prefix:
            lang.states = {remove_prefix(state) for state in lang.states}
            lang.transition = {
                                remove_prefix(before):
                                    {
                                        char:
                                            {
                                                remove_prefix(state) for state in after
                                            }
                                        for (char, after) in transitions.items()
                                    }
                                for (before, transitions) in lang.transition.items()
                             }
            lang.start = remove_prefix(lang.start)
            lang.accept = {remove_prefix(state) for state in lang.accept}
            lang.prefix = ''

        return lang


    def import_xml(file, prefix=''):
        import xml.etree.ElementTree as et

        xml = et.parse(file)
        if xml.getroot().tag != 'automaton':
            xml = xml.find('automaton')

        states = set()
        alphabet = set()
        transition = dict()
        start = None
        accept = set()

        for state in xml.findall('.//state'):
            identity = state.get('id')
            states.add(prefix + identity)
            for child in state:
                if child.tag == 'final':
                    accept.add(prefix + identity)
                if child.tag == 'initial':
                    start = prefix + identity

        for node in xml.findall('.//transition'):
            char = node.find('read').text
            before = prefix + node.find('from').text
            after = set([prefix + node.find('to').text])

            if not char:
                char = 'ε'
            else:
                alphabet.add(char)

            entry = {char: after}
            if before in transition:
                if char in transition[before]:
                    transition[before][char].update(after)
                else:
                    transition[before] = {**transition[before], **entry}
            else:
                transition[before] = entry

        construct = FA(states, alphabet, transition, start, accept)
        return construct


    def export_xml(self, file=None):
        import xml.etree.ElementTree as et

        tree = et.Element('structure')
        et.SubElement(tree, 'type').text = 'fa'
        automaton = et.SubElement(tree, 'automaton')

        for state in self.states:
            s_parent = et.SubElement(automaton, 'state')
            s_parent.set('id', state)
            s_parent.set('name', state)
            if state == self.start:
                et.SubElement(s_parent, 'initial')
            if state in self.accept:
                et.SubElement(s_parent, 'final')

        for before, step in self.transition.items():
            for char, after in step.items():
                for state in after:
                    t_parent = et.SubElement(automaton, 'transition')
                    et.SubElement(t_parent, 'from').text = str(before)
                    et.SubElement(t_parent, 'to').text = str(state)
                    et.SubElement(t_parent, 'read').text = str(char)

        xml = et.tostring(tree).decode()
        for remove in [',', "'", '{', '}', '&#949;']:
            xml = xml.replace(remove, '')

        if file:
            with open(file, 'w') as f:
                f.write(xml)
        else:
            print(xml)


    def validate(self, string):
        accepted = False

        def traverse(start, string):
            nonlocal accepted

            if accepted is True:
                return

            e = None
            if start in self.transition:
                e = self.transition[start].get('ε') if 'ε' in self.transition[start] else set()
                if isinstance(e, str): e = set([e])

            if len(string) > 0:
                if start in self.transition and string[0] in self.alphabet:
                    s = self.transition[start].get(string[0]) if string[0] in self.transition[start] else set()
                    if isinstance(s, str): s = set([s])
                    for state in s:
                        traverse(state, string[1:])
            else:
                if start in self.accept:
                    accepted = True

            if e:
                print(e)
                for state in e:
                    traverse(state, string)

        traverse(self.start, string)

        return accepted


    def union(a, b):
        q0     = a.start + 'u' + b.start
        Q      = a.states | b.states; Q.add(q0)
        sigma  = a.alphabet | b.alphabet
        delta  = dict()
        F      = a.accept | b.accept
        prefix = a.prefix + b.prefix

        sigma.add('ε')

        def insert(e):
            delta[q] = {**delta[q], **e} if q in delta else e

        for q in Q:
            for s in sigma:
                if q in a.states:
                    step = a.transition.get(q)
                    if step is not None and step.get(s) is not None:
                        insert({s: step.get(s)})
                elif q in b.states:
                    step = b.transition.get(q)
                    if step is not None and step.get(s) is not None:
                        insert({s: step.get(s)})
                elif q == q0 and s == 'ε':
                    insert({s: {a.start, b.start}})

        sigma.remove('ε')

        new = FA(Q, sigma, delta, q0, F, prefix)
        return new


    def concat(a, b):
        q0     = a.start
        Q      = a.states | b.states
        sigma  = a.alphabet | b.alphabet
        delta  = {**a.transition, **b.transition}
        F      = b.accept
        prefix = a.prefix + b.prefix

        entry = set([b.start])
        for q in a.accept:
            if q in delta:
                delta[q]['ε'] = delta[q]['ε'] | entry
            else:
                delta[q] = {'ε': entry}

        new = FA(Q, sigma, delta, q0, F, prefix)
        return new


    def star(lang):
        from copy import deepcopy

        q0     = lang.prefix + '*'
        Q      = deepcopy(lang.states); Q.add(q0)
        sigma  = deepcopy(lang.alphabet)
        delta  = deepcopy(lang.transition)
        F      = deepcopy(lang.accept)
        prefix = lang.prefix

        delta[q0] = {'ε': set([lang.start])}
        for q in F:
            if q in delta:
                if 'ε' in delta[q]:
                    delta[q]['ε'].add(q0)
                else:
                    delta[q]['ε'] = set([q0])
            else:
                delta[q] = {'ε': set([q0])}

        F.add(q0)

        new = FA(Q, sigma, delta, q0, F, prefix)
        return new


    def __str__(self):
        return str([self.states, self.alphabet, self.transition, self.start, self.accept, self.prefix])
# for debugging only!
#       return f'''    states: {self.states}
#   alphabet: {self.alphabet}
# transition: {self.transition}
#      start: {self.start}
#     accept: {self.accept}
#     prefix: {self.prefix}'''
