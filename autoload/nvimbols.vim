
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

    "
    " CursorMoved appears buggy (or somehow reacting to python render events..)
    " Not very nice fix here..
    "
    if !exists('s:LastFilename')
        let s:LastFilename = ""
    endif
    if !exists('s:LastLine')
        let s:LastLine=-1
    endif
    if !exists('s:LastCol')
        let s:LastCol=-1
    endif

    let filename = expand('%:p')
    let [line, col] = getpos('.')[1:2]

    if filename==s:LastFilename && line==s:LastLine && col==s:LastCol
        return
    endif

    let s:LastFilename = filename
    let s:LastLine = line
    let s:LastCol = col

    call _nvimbols_update_location(filename, line, col)
endfunction


function! nvimbols#follow_link() abort
    if winnr() != nvimbols#window_number()
        return
    endif

    let [line, col] = getpos('.')[1:2]
    let result = _nvimbols_get_link(line, col)
    if result==""
        return
    endif

    let t_filename = split(result,":")[0]
    let t_line = split(result,":")[1]
    let t_col = split(result,":")[2]

    execute 'wincmd p'
    execute 'edit ' . t_filename
    call cursor(t_line, t_col)
endfunction

function! nvimbols#follow_first_reference(reference_name) abort
    let result = _nvimbols_get_first_reference(a:reference_name)
    if result==""
        return
    endif

    let t_filename = split(result,":")[0]
    let t_line = split(result,":")[1]
    let t_col = split(result,":")[2]

    execute 'edit ' . t_filename
    call cursor(t_line, t_col)
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

    " Force redraw
    call _nvimbols_render(1)

    " Switch back
    " execute 'wincmd p'
endfunction

function! nvimbols#close_window() abort
    let winnr = nvimbols#window_number()
    if winnr != -1
        execute winnr . 'wincmd w'
        bwipeout
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

function! nvimbols#clear() abort
    call _nvimbols_clear()
endfunction

