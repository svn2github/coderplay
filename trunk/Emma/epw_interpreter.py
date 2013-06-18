
class EvalError(Exception):
    pass

class InterpretControl(Exception):
    def __init__(self, *args):
        self.args = args

class BreakControl(InterpretControl):
    pass

class ContinueControl(InterpretControl):
    pass

class ReturnControl(InterpretControl):
    pass


