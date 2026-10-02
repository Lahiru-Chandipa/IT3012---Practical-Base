class KnowledgeBase:
    """
    Knowledge Base for storing facts and logical rules.

    Facts are stored as a set so that each fact is unique.
    Rules are stored as tuples containing:
        (premise_list, conclusion)
    """

    def __init__(self):
        # Store unique facts
        self.facts = set()

        # Store rules as:
        # ([premise1, premise2, ...], conclusion)
        self.rules = []

    def tell_fact(self, fact_string):
        """
        Add a fact to the Knowledge Base.
        """
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        """
        Add a rule to the Knowledge Base.

        Example:
            ['TargetVisible', 'HasDust'] -> 'SafeToEngage'
        """
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self):
        """
        Remove all current facts from the Knowledge Base.

        Rules are preserved.
        """
        self.facts.clear()

    def forward_chain(self):
        """
        Apply forward chaining until no new facts can be deduced.
        """

        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:
                # Only attempt to derive the conclusion
                # if it is not already known.
                if conclusion not in self.facts:
                    # Modus Ponens:
                    # If ALL premises are known,
                    # the conclusion can be added.
                    if all(premise in self.facts for premise in premises):
                        self.facts.add(conclusion)

                        new_facts_added = True
