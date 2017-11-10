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
" Disable NVimbols completely by adding
"   let g:nvimbols_enabled = 0
" to your init.vim
"

if(!exists('g:nvimbols_enabled'))
    let g:nvimbols_enabled = 1
endif


"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Initialization
" Inform python plugin, where we are
"

if(g:nvimbols_enabled)
    augroup nvimbols_init
        autocmd!
        autocmd BufEnter * :call nvimbols#init_config()
    augroup end
    augroup nvimbols_root
        autocmd!
        autocmd BufEnter * :call nvimbols#update_location()
        autocmd InsertLeave * :call nvimbols#update_location()
        autocmd CursorMoved * :call nvimbols#update_location()
    augroup end
else
    augroup nvimbols_init
        autocmd!
    augroup end
    augroup nvimbols_root
        autocmd!
    augroup end
endif

"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Bar
"

command! NVimbolsToggle :call nvimbols#toggle_window()
command! NVimbolsFollow :call nvimbols#follow_link_to_first_reference()

"
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Default bindings: <leader>s
"
if(!exists('g:nvimbols_default_bindings'))
    let g:nvimbols_default_bindings = 1
endif

if(g:nvimbols_default_bindings)
    nnoremap <silent> <leader>sf :NVimbolsFollow<CR>
endif
