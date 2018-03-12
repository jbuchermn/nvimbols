import neovim
import os
import time
from threading import Lock, Thread, Timer

from nvimbols.content import Content, Wrapper, Highlight
from nvimbols.job_queue import JobQueue
from nvimbols.util import find_rplugins, import_plugin, on_error, log
from nvimbols.nvimbols import NVimbols
from nvimbols.location import Location
from nvimbols.communicator import COMM

@neovim.plugin
class NVimbolsPlugin:
    def __init__(self, vim):
        self._vim = vim
        self._config = {}
        self._main = None
        self._sources = None
        self._lock = Lock()

        self._content_if_deactivated = Content()

        """
        Needs a rewrite... something like synchronized queue...
        """
        self._put_content_lock = Lock()
        self._put_content_queue = JobQueue(1, self._vim, True)
        self._content = None

    def _dispatch(self, func, *args, **kwargs):
        def wrapped():
            with self._lock:
                try:
                    func(*args, **kwargs)
                except Exception as err:
                    on_error(self._vim, err)

        Thread(target=wrapped).start()

    def _init(self, args):
        self._config = args[0]
        ft = args[1]

        if(ft == "nvimbols" or ft == "denite"):
            return

        """
        Initialise sources
        """
        if(self._sources is None):
            log("Initialising NVimbols sources...")
            self._sources = {}

            for path in find_rplugins(self._config['rtp']):
                name = os.path.splitext(os.path.basename(path))[0]
                source = None
                try:
                    Source = import_plugin(path, 'source', 'Source')
                    if not Source:
                        continue

                    source = Source(self._vim)
                    source.name = getattr(source, 'name', name)
                    source.path = path

                    log("  <> found source %s for filetypes %s" % (source.name, source.filetypes))

                    self._sources[source.name] = source

                except Exception as err:
                    on_error(self._vim, err)

        """
        Message in case selection of sources fails
        """
        self._content_if_deactivated = Content()
        self._content_if_deactivated += Wrapper(Highlight('Title', "Nvimbols"),
                                                " could not find source for\n  filetype ",
                                                Highlight('PreProc', ft),
                                                ".\nRegistered sources are:")
        for source in self._sources:
            self._content_if_deactivated += Wrapper("\n ",
                                                    Highlight('Title', self._sources[source].name),
                                                    " for \n   filetypes ",
                                                    Highlight('PreProc', ", ".join(self._sources[source].filetypes)))

        if(self._main is not None and ft in self._main.filetypes):
            return

        """
        Select source and start NVimbols
        """
        log("Initialising NVimbols for filetype %s..." % ft)

        possible_sources = []
        for s in self._sources:
            if(ft in self._sources[s].filetypes):
                possible_sources += [self._sources[s]]

        selected_source = None
        if(len(possible_sources) != 0):
            selected_source = possible_sources[0]

        if(selected_source is not None):
            log("  <> selected source: %s" % selected_source.name)
            self._main = NVimbols(self, selected_source)

            """
            Enable automatic rendering
            """
            self._main.on_update(lambda: self._render())
        else:
            log("  <> no source selected, deactivating")
            self._main = None
            self._render()

        COMM.set('NVimbols', self._main)

    def _put_content(self):
        """
        Do not lock inside threadsafe_call. This causes deadlocks
        """
        if self._put_content_lock.acquire(False):
            try:
                buf = None
                for b in self._vim.buffers:
                    if b.name.endswith(self._config['nvimbols_window_name']):
                        buf = b
                        break

                if buf is not None:
                    buf.api.set_option('modifiable', True)

                    buf[:] = self._content.raw()
                    for highlight in self._content.highlights():
                        buf.add_highlight(highlight.name,
                                          highlight.line - 1,
                                          highlight.start_col - 1,
                                          highlight.end_col - 1 if highlight.end_col >= 1 else -1,
                                          -1)

                    buf.api.set_option('modifiable', False)

                jumps = {
                    'links': self._content.links(),
                    'quickjumps': self._content.quickjumps()
                }
                self._vim.call("nvimbols#set_jumps", jumps)

            finally:
                self._put_content_lock.release()
        else:
            return True

    def _render(self, force_put=False):
        content = self._content_if_deactivated if self._main is None else self._main.render()

        if force_put or self._content != content:
            self._content = content
            if self._put_content_queue.is_empty():
                self._put_content_queue.job(lambda: self._put_content())

        self._content = content

    def _update_location(self, args):
        if(self._main is None):
            return

        filename = args[0]
        line = args[1]
        col = args[2]

        location = Location(filename, line, col)
        self._main.update_location(location)
        self._render()

    def _command(self, args):
        if(self._main is None):
            return

        self._main.command(args[0])

    def _cancel(self, args):
        if(self._main is None):
            return

        self._main.cancel()

    """
    Public asynchronous interface, immediately dispatched to own threads.
    """
    @neovim.function('_nvimbols_init')
    def init(self, args):
        self._dispatch(NVimbolsPlugin._init, self, args)

    @neovim.function('_nvimbols_update_location')
    def update_location(self, args):
        self._dispatch(NVimbolsPlugin._update_location, self, args)

    @neovim.function('_nvimbols_render')
    def render(self, args):
        self._dispatch(NVimbolsPlugin._render, self, args[0] != 0 if len(args) > 0 else False)

    @neovim.function('_nvimbols_command')
    def command(self, args):
        self._dispatch(NVimbolsPlugin._command, self, args)

    @neovim.function('_nvimbols_vimleave')
    def vimleave(self, args):
        self._dispatch(NVimbolsPlugin._cancel, self, args)













