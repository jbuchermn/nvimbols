" TODO!
"   init should not be called when opening the nvimbols window!
"   update_location should only be called when not inside the nvimbols window
"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Guard
"

if exists('g:nvimbols_loaded') || &compatible
    finish
endif
let g:nvimbols_loaded = 1

"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Initialization
"

augroup nvimbols_init
    autocmd!
    autocmd BufEnter * :call nvimbols#init_config()
augroup end

"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Disable NVimbols completely by adding
"   let g:nvimbols_enabled = 0
" to your init.vim
"

if(!exists('g:nvimbols_enabled'))
    let g:nvimbols_enabled = 1
endif


"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Inform python plugin, where we are
"

if(g:nvimbols_enabled)
    augroup nvimbols_root
        autocmd!
        autocmd BufEnter * :call nvimbols#update_location()
        autocmd InsertLeave * :call nvimbols#update_location()
        autocmd CursorMoved * :call nvimbols#update_location()
    augroup end
else
    augroup nvimbols_root
        autocmd!
    augroup end
endif

"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Bar
"

command! NvimbolsToggle :call nvimbols#toggle_window()