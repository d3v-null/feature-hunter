class ResultDiff(object):
    def __init__(self, old_result, new_result):
        self.old_result = old_result
        self.new_result = new_result

    def difference(self):
        difference = []
        if not self.old_result:
            return self.new_result
        for record in self.new_result:
            if record not in self.old_result:
                difference.append(record)
        return difference
