
function! nvimbols#window_name()
    return "nvimbols"
endfunction

function! nvimbols#window_number()
    let name = nvimbols#window_name()
    return bufwinnr('^' . name . '$')
endfunction

function! nvimbols#init_config()
    if winnr() == nvimbols#window_number()
        return
    endif

    call _nvimbols_init({
                \ 'ft' : &ft,
                \ 'rtp' : &runtimepath
                \ })
endfunction

function! nvimbols#update_location()
    if winnr() == nvimbols#window_number()
        return
    endif

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

function! nvimbols#update_symbol() abort
    call nvimbols#render_if_open()
endfunction


function! nvimbols#open_window() abort
    " 'Borrowed' from Vim Tagbar

    let window_name = nvimbols#window_name()
    let pos = 'botright '
    let width = 50

    execute 'silent keepalt ' . pos . 'vertical ' . width . 'split ' . window_name
    execute 'silent ' . 'vertical ' . 'resize ' . width

    setlocal filetype=nvimbols

    setlocal noreadonly 
    setlocal buftype=nofile
    setlocal bufhidden=hide
    setlocal noswapfile
    setlocal nobuflisted
    setlocal nomodifiable
    
    setlocal textwidth=0

    setlocal conceallevel=3

    setlocal nolist
    setlocal nowrap
    setlocal winfixwidth
    setlocal nospell

    setlocal nofoldenable
    setlocal foldcolumn=0
    setlocal foldmethod&
    setlocal foldexpr&

    let &l:statusline = 'nvimbols'

    setlocal modifiable
    silent %delete _
    setlocal nomodifiable

    call nvimbols#render_if_open()

    " Switch back
    " execute 'wincmd p'
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

