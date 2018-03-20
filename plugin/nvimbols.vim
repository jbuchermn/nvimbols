" Guard {{{
if exists('g:nvimbols_loaded') || &compatible
    finish
endif
let g:nvimbols_loaded = 1
" }}}

" Configuration {{{

" Disable completely
if(!exists('g:nvimbols_enabled'))
    let g:nvimbols_enabled = 1
endif

if(g:nvimbols_enabled)
    " Default bindings: <leader>s
    if(!exists('g:nvimbols_default_bindings'))
        let g:nvimbols_default_bindings = 1
    endif

    " Window name to be used for bar
    if(!exists('g:nvimbols_window_name'))
        let g:nvimbols_window_name = "nvimbols"
    endif

endif

" }}}

" Auto-Commands {{{
if(g:nvimbols_enabled)
    augroup nvimbols_root
        autocmd!
        autocmd BufEnter * :call nvimbols#bufenter()
        autocmd Filetype * :call nvimbols#filetype()
        autocmd InsertLeave * :call nvimbols#insertleave()
        autocmd TextChanged * :call nvimbols#textchanged()
        autocmd CursorMoved * :call nvimbols#cursormoved()
        autocmd VimLeave * :call nvimbols#vimleave()
    augroup end
else
    augroup nvimbols_root
        autocmd!
    augroup end
endif
" }}}

" Commands {{{
if(g:nvimbols_enabled)
    " General commands
    command! NVimbolsToggle :call nvimbols#toggle_window()
    command! NVimbolsClear :call nvimbols#command('clear')
    command! NVimbolsHelp :call nvimbols#command('help')
    command! NVimbolsSwitch :call nvimbols#command('switch_mode')
    " Commands when cursor is on symbol
    command! NVimbolsFollowTarget :call nvimbols#follow_quickjump("first_source_of_references", '')
    command! NVimbolsFollowParent :call nvimbols#follow_quickjump("first_source_of_is_child_of", '')
    command! NVimbolsFollowBase :call nvimbols#follow_quickjump("first_source_of_inherits_from", '')
    command! NVimbolsFollowTargetVertical :call nvimbols#follow_quickjump("first_source_of_references", 'v')
    command! NVimbolsFollowParentVertical :call nvimbols#follow_quickjump("first_source_of_is_child_of", 'v')
    command! NVimbolsFollowBaseVertical :call nvimbols#follow_quickjump("first_source_of_inherits_from", 'v')
    " Commands when cursor is in NVimbols window
    command! NVimbolsFollow :call nvimbols#follow_link('')
    command! NVimbolsFollowVertical :call nvimbols#follow_link('v')
endif
" }}}

" Key-Bindings {{{
if(g:nvimbols_enabled && g:nvimbols_default_bindings)
    nnoremap <silent> <leader>sc :NVimbolsClear<CR>
    nnoremap <silent> <leader>sf :NVimbolsFollowTarget<CR>
    nnoremap <silent> <leader>sp :NVimbolsFollowParent<CR>
    nnoremap <silent> <leader>sb :NVimbolsFollowBase<CR>
    nnoremap <silent> <leader>sF :NVimbolsFollowTargetVertical<CR>
    nnoremap <silent> <leader>sP :NVimbolsFollowParentVertical<CR>
    nnoremap <silent> <leader>sB :NVimbolsFollowBaseVertical<CR>
    nnoremap <silent> <leader>sd :Denite -no-quit nvimbols:symbol<CR>
    nnoremap <silent> <leader>sj :Denite -no-quit nvimbols:list<CR>
endif
" }}}
