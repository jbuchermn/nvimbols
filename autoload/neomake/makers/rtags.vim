function! neomake#makers#rtags#rtags() abort

    let maker = {'name': 'RTags'}
    function! maker.get_list_entries(jobinfo) abort
        return _rtags_neomake_get_list_entries(a:jobinfo) 
    endfunction
    return maker

endfunction

