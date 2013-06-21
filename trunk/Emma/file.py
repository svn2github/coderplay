
class Lines():
    def __init__(self, filename='[PROMT]'):
        self.filename = filename
        self.text = ''
        self.nchars = 0
        self.line_ranges = []
        self.idxchar = 0

    def get_rest_text(self):
        if self.idxchar >= len(self.text):
            return None
        return self.text[self.idxchar:]

    def get_line(self, lineno):
        'lineno starts from 0'
        if lineno >= len(self.line_ranges):
            return None
        start, end = self.line_ranges
        return self.text[start:end]

    def append(self, line):
        text_length = len(self.text)
        line_length = len(line)
        self.text += line
        self.line_ranges.append((text_length, text_length+line_length))
        self.nchars += line_length

    def reset(self):
        self.text = ''
        self.nchars = 0
        self.line_ranges = []
        self.idxchar = 0



class File():
    def __init__(self):
        pass

