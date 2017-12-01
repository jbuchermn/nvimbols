" Python interface {{{
function! nvimbols#init_config()
    call _nvimbols_init({
                \   'nvimbols_window_name': g:nvimbols_window_name,
                \   'rtp': &runtimepath
                \ }, 
                \ &filetype)
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

function! nvimbols#command(command) abort
    call _nvimbols_command(a:command)
endfunction

function! nvimbols#set_jumps(jumps) abort
    let s:Jumps = a:jumps
endfunction

function! nvimbols#get_link(line, col) abort
    if(!exists("s:Jumps"))
        return ""
    endif
    for d in items(s:Jumps.links)
        let t_line = split(d[0], ":")[0]
        let t_start_col = split(d[0], ":")[1]
        let t_end_col = split(d[0], ":")[2]
        if(t_line == a:line && t_start_col <= a:col && (t_end_col == -1 || t_end_col >= a:col))
            return d[1]
        endif
    endfor

    return ""
endfunction

function! nvimbols#get_quickjump(quickjump) abort
    if(!exists("s:Jumps"))
        return ""
    endif
    return get(s:Jumps.quickjumps, a:quickjump, "")
endfunction
" }}}

" Window management {{{
function! nvimbols#window_number()
    return bufwinnr('^' . g:nvimbols_window_name . '$')
endfunction

function! nvimbols#open_window() abort
    " 'Borrowed' from Vim Tagbar

    let window_name = g:nvimbols_window_name
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
" }}}

" Jump around {{{
function! nvimbols#follow_link(split) abort
    if winnr() != nvimbols#window_number()
        return
    endif

    let [line, col] = getpos('.')[1:2]
    let result = nvimbols#get_link(line, col)
    if result==""
        return
    endif

    let t_filename = split(result,":")[0]
    let t_line = split(result,":")[1]
    let t_col = split(result,":")[2]

    execute 'wincmd p'
    if a:split == 'v'
        execute 'vnew ' . t_filename
    else
        execute 'edit ' . t_filename
    endif
    call cursor(t_line, t_col)
endfunction

function! nvimbols#follow_quickjump(quickjump, split) abort
    let result = nvimbols#get_quickjump(a:quickjump)
    if result==""
        return
    endif

    let t_filename = split(result,":")[0]
    let t_line = split(result,":")[1]
    let t_col = split(result,":")[2]

    if a:split == 'v'
        execute 'vnew ' . t_filename
    else
        execute 'edit ' . t_filename
    endif
    call cursor(t_line, t_col)
endfunction
" }}}

" Auto-Commands {{{
function! nvimbols#filetype() abort
    call nvimbols#init_config()
endfunction

function! nvimbols#bufenter() abort
    call nvimbols#update_location()
endfunction

function! nvimbols#insertleave() abort
    call nvimbols#update_location()
endfunction

function! nvimbols#cursormoved() abort
    call nvimbols#update_location()
endfunction

function! nvimbols#vimleave() abort
    call _nvimbols_vimleave()
endfunction
" }}}


