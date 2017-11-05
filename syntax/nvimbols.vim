
syn region NVimbolsTitle matchgroup=NVimbolsControls start=#{{{{Title}}}}# end=#{{{{\/Title}}}}# concealends
syn region NVimbolsStatement matchgroup=NVimbolsControls start=#{{{{Statement}}}}# end=#{{{{\/Statement}}}}# concealends
hi def link NVimbolsTitle Title
hi def link NVimbolsStatement Statement


