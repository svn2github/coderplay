
class EvalError(Exception):
    def __repr__(self):
        return '%%[EvalError] %s\n%s' % self.args

class InterpretControl(Exception):
    def __init__(self, *args):
        self.args = args

class BreakControl(InterpretControl):
    pass

class ContinueControl(InterpretControl):
    pass

class ReturnControl(InterpretControl):
    pass


