from .base import Base
from nvimbols.util import log
from nvimbols.communicator import COMM


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        
        self.name = 'nvimbols'
        self.kind = 'file'
        self.vars = {  }
        self.matchers = ['matcher_ignore_globs', 'matcher_regexp']

        self._nvimbols = None

    def on_init(self, context):
        self._nvimbols = COMM.get('NVimbols')

    def gather_candidates(self, context):
        log(context)
        if self._nvimbols is None:
            return []

        location = self._nvimbols.get_current_location()
        return [{
            'word': str(location),
            'abbr': str(location),
            'action__path': location.filename,
            'action__line': location.start_line,
            'action__col': location.start_col,
            'action__text': str(location)
        }]
