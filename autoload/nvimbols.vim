
function! nvimbols#window_name()
    return "window_nvimbols"
endfunction

function! nvimbols#window_number()
    let name = nvimbols#window_name()
    return bufwinnr('^' . name . '$')
endfunction

function! nvimbols#init_config()
    call _nvimbols_init({
                \ 'ft' : &ft,
                \ 'rtp' : &runtimepath
                \ })
endfunction

function! nvimbols#update_location()
    let [lnum, col] = getpos('.')[1:2]
    call _nvimbols_update_location(lnum, col)
endfunction

function! nvimbols#render_if_open()
    let winnr = nvimbols#window_number()
    if winnr!=-1
        call _nvimbols_render({
                    \ 'window_number': winnr
                    \ })
    endif
endfunction

function! nvimbols#update_symbol(symbol) abort
    let s:current_symbol = a:symbol
    call nvimbols#render_if_open()
endfunction

function! nvimbols#no_symbol() abort
    unlet s:current_symbol
    call nvimbols#render_if_open()
endfunction

function! nvimbols#open_window() abort
    " "Borrowed" from Vim Tagbar

    let window_name = nvimbols#window_name()
    let pos = 'botright '
    let width = 50

    execute 'silent keepalt ' . pos . 'vertical ' . width . 'split ' . window_name
    execute 'silent ' . 'vertical ' . 'resize ' . width

    setlocal filetype=nvimbols

    setlocal noreadonly " in case the "view" mode is used
    setlocal buftype=nofile
    setlocal bufhidden=hide
    setlocal noswapfile
    setlocal nobuflisted
    " setlocal nomodifiable
    " setlocal noundofile
    setlocal textwidth=0

    setlocal nolist
    setlocal nowrap
    setlocal winfixwidth
    setlocal nospell

    setlocal nofoldenable
    setlocal foldcolumn=0
    " Reset fold settings in case a plugin set them globally to something
    " expensive. Apparently 'foldexpr' gets executed even if 'foldenable' is
    " off, and then for every appended line (like with :put).
    setlocal foldmethod&
    setlocal foldexpr&

    let &l:statusline = 'nvimbols'

    " This will issue render
    execute 'wincmd p'
endfunction

function! nvimbols#close_window() abort
    let winnr = nvimbols#window_number()
    if winnr != -1
        execute winnr . 'wincmd w'
        close
    endif

endfunction

function! nvimbols#toggle_window() abort
    let winnr = nvimbols#window_number()
    if winnr != -1
        call nvimbols#close_window()
    else
        call nvimbols#open_window()
    endif
endfunction

