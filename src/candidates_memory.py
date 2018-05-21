class CandidatesMemory(object):

    def __init__(self):
        self.mem_dict_primary = {}
        self.mem_dict_secondary = {}

    def add_candidates(self, key, candidates, primary=True):
        if primary and key not in self.mem_dict_primary:
            self.mem_dict_primary[key] = candidates
        if not primary and key not in self.mem_dict_secondary:
            self.mem_dict_secondary[key] = candidates

    def get_candidates(self, key):
        result = self.mem_dict_primary.get(key, {})
        if result == {}:
            result = self.mem_dict_secondary.get(key, {})
        assert result != {}
        return result

    def already_processed(self, key):
        return key in self.mem_dict_primary or key in self.mem_dict_secondary
