from .base import Base
from nvimbols.util import log
from nvimbols.communicator import COMM


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'nvimbols_symbol'
        self.kind = 'file'
        self.vars = {}
        self.matchers = ['matcher_ignore_globs', 'matcher_regexp']

        self._nvimbols = None

    def gather_candidates(self, context):
        nvimbols = COMM.get('NVimbols')
        if nvimbols is not None:
            return nvimbols.render_denite(context, 'symbol')
        else:
            return []
