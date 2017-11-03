"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Guard
"

if exists('g:nvimbols_loaded') || &compatible
    finish
endif
let g:nvimbols_loaded = 1

function! nvimbols#update_location()
    let [lnum, col] = getpos('.')[1:2]
    call _nvimbols_update_location(lnum, col)
endfunction
