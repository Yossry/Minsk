from odoo.tools import float_is_zero, pycompat
import pdb
class BaseSuspendSecurityUid(int):
    def __int__(self):
        return self

    def __eq__(self, other):
        if isinstance(other, pycompat.integer_types):
            return False
        return super(BaseSuspendSecurityUid, self).__int__() == other

    def __iter__(self):
        yield super(BaseSuspendSecurityUid, self).__int__()
