from .base import Base
from nvimbols.util import log
from nvimbols.communicator import COMM


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'nvimbols_symbol'
        self.kind = 'file'
        self.vars = {}
        self.matchers = ['matcher_fuzzy']

        self._content = None
        self._candidate_hashes = []
        self._new_candidates = []

        self._nvimbols = None
        self._nvimbols_obsid = None

    def render(self):
        self._content = self._nvimbols.render_denite('symbol')

        new_candidates = []
        for c in self._content.get_candidates():
            if not c['__hash'] in self._candidate_hashes:
                new_candidates += [c]

        for c in new_candidates:
            self._candidate_hashes += [c['__hash']]

        self._new_candidates += new_candidates

    def on_init(self, context):
        self._nvimbols = COMM.get('NVimbols')
        self._nvimbols_obsid = self._nvimbols.on_update(lambda: self.render())

        self._new_candidates = []
        self._candidate_hashes = []
        self.render()

    def on_close(self, context):
        if(self._nvimbols_obsid is not None):
            self._nvimbols.remove_on_update(self._nvimbols_obsid)

        self._nvimbols_obsid = None

    def gather_candidates(self, context):
        context['is_async'] = not self._content.is_complete()
        result = self._new_candidates
        self._new_candidates = []
        return result
