
class Lines():
    def __init__(self, filename='[PROMT]'):
        self.filename = filename
        self.text = ''
        self.line_ranges = []
        self.pos = 0

    def get_lineno(self, pos):
        'Get the line number from the char position in overall text'
        for idx, (start, end) in enumerate(self.line_ranges):
            if start<=pos and pos<end:
                return idx
        return None

    def get_linepos(self, pos):
        """
        Get the line number and position in the line given the overall position.
        """
        lineno = self.get_lineno(pos)
        colpos = pos - self.line_ranges[lineno][0]
        return (lineno, colpos)

    def get_content_around_pos(self, pos):
        'Get the input content around the pos in the overall text'
        lineno, colpos = self.get_linepos(pos)
        padding = '    '
        arrow   = '--> '
        content = ''
        for idx in range(lineno-2, lineno+1):
            oneline = self.get_line(idx)
            if oneline is not None:
                txt_ln = '%4d' % (idx+1)
                if idx == lineno:
                    content += arrow
                else:
                    content += padding
                content += txt_ln + padding + oneline
        content += ' ' * (colpos+2*len(padding)+len(txt_ln)) + '^\n'
        return content


    def get_line(self, lineno):
        'lineno starts from 0'
        if lineno<0 or lineno >= len(self.line_ranges):
            return None
        start, end = self.line_ranges[lineno]
        return self.text[start:end]

    def append(self, line):
        text_length = len(self.text)
        line_length = len(line)
        self.text += line
        self.line_ranges.append((text_length, text_length+line_length))

    def reset(self):
        self.text = ''
        self.line_ranges = []
        self.pos = 0



class File():
    def __init__(self):
        pass

