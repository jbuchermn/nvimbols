function! moveconcealed#l(count)
    let cnt=a:count
    let mvcnt=0
    let c=col('.')
    let l=line('.')
    let lc=col('$')
    let line=getline('.')
    while cnt
        if c>=lc
            let mvcnt+=cnt
            break
        endif
        if stridx(&concealcursor, 'n')==-1
            let isconcealed=0
        else
            let [isconcealed, cchar, group]=synconcealed(l, c)
        endif
        if isconcealed
            let cnt-=strchars(cchar)
            let oldc=c
            let c+=1
            while c<lc && synconcealed(l, c)[0]
                let c+=1
            endwhile
            let mvcnt+=strchars(line[oldc-1:c-2])
        else
            let cnt-=1
            let mvcnt+=1
            let c+=len(matchstr(line[c-1:], '.'))
        endif
    endwhile
    return ":\<C-u>\e".mvcnt."l"
endfunction

function! moveconcealed#j(count)
    let mvcnt = 1
    return ":\<C-u>\e".mvcnt."j"
endfunction

function! moveconcealed#k(count)
    let mvcnt = 1
    return ":\<C-u>\e".mvcnt."k"
endfunction

function! moveconcealed#h(count)
    let cnt=a:count
    let mvcnt=0
    let c=col('.')
    let l=line('.')
    let lc=1
    let line=getline('.')
    while cnt
        if c<=lc
            let mvcnt+=cnt
            break
        endif
        if stridx(&concealcursor, 'n')==-1
            let isconcealed=0
        else
            let [isconcealed, cchar, group]=synconcealed(l, c)
        endif
        if isconcealed
            let cnt-=strchars(cchar)
            let oldc=c
            let c-=1
            while c>lc && synconcealed(l, c)[0]
                let c-=1
            endwhile
            let mvcnt+=strchars(line[c-1:oldc-2])
        else
            let cnt-=1
            let mvcnt+=1
            let c-=len(matchstr(line[c-1:], '.'))
        endif
    endwhile
    return ":\<C-u>\e".mvcnt."h"
endfunction
