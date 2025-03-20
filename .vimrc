filetype off                  " required
filetype plugin indent on     " required
"set nu
syntax on
set encoding=utf-8
filetype plugin on
execute pathogen#infect()

" Enable full mouse support.
"set mouse=a

" Enable folding/with the spacebar
set foldmethod=indent
set foldlevel=99
nnoremap <space> za

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

" add all your plugins here (note older versions of Vundle
" used Bundle instead of Plugin)
"
Plugin 'tmhedberg/SimpylFold'
let g:SimpylFold_docstring_preview=1

Bundle 'Valloric/YouCompleteMe'
let g:ycm_autoclose_preview_window_after_completion=1
map <leader>g  :YcmCompleter GoToDefinitionElseDeclaration<CR>
let g:ycm_python_interpreter_path = ''
let g:ycm_python_sys_path = []
let g:ycm_global_ycm_extra_conf = '~/.global_extra_conf.py'
let g:ycm_extra_conf_vim_data = [
                        \  'g:ycm_python_interpreter_path',
                        \  'g:ycm_python_sys_path',
                        \]
"Plugin 'vim-syntastic/syntastic'
Plugin 'dense-analysis/ale'
let g:ale_virtualtext_cursor = 'disabled'
"
" Flake8 and config options
Plugin 'nvie/vim-flake8'
let g:flake8_show_in_gutter=1
let g:flake8_warning_marker=''
let g:flake8_max_line_length=159
let g:flake8_ignore="E252,W251"
"
"
Plugin 'integralist/vim-mypy'
let python_highlight_all=1

" Color schemes
Plugin 'flazz/vim-colorschemes'
Plugin 'altercation/vim-colors-solarized'
Plugin 'Wombat'
Plugin 'lifepillar/vim-solarized8'
Plugin 'jonathanfilip/vim-lucius'
if has('gui_running')
  set background=light
  colorscheme elflord
else
  set background=dark
  colorscheme solarized8
endif

Plugin 'preservim/nerdtree'
Plugin 'jistr/vim-nerdtree-tabs'
Plugin 'ctrlpvim/ctrlp.vim'
Plugin 'tpope/vim-fugitive'
Bundle 'matze/vim-move'
Plugin 'vim-airline/vim-airline'
let g:airline#extensions#ale#enabled = 1
" tags and scope
Plugin 'lukelbd/vim-tags'
Plugin 'majutsushi/tagbar'
nmap <F8> :TagbarToggle<CR>
Plugin 'python-rope/ropevim'
"
" !IMPORTANT!
" All of your Plugins must be added before the following line
call vundle#end()            " required

" Languages/defaults
" C
augroup langC
        au BufRead,BufNewFile *.c,*.h set expandtab
        au BufRead,BufNewFile *.c,*.h set tabstop=4
        au BufRead,BufNewFile *.c,*.h set shiftwidth=4
        au BufRead,BufNewFile *.c,*.h set autoindent
        au BufRead,BufNewFile *.c,*.h call matchadd("BadWhitespace", '/^\t\+/')
        au BufRead,BufNewFile *.c,*.h call matchadd("BadWhitespace", '/\s\+$/')
        au BufNewFile *.c,*.h set fileformat=unix
        au BufRead,BufNewFile *.c,*.h let b:comment_leader = '/* '
augroup END

" Java
augroup langJava
        au BufRead,BufNewFile *.js,*.java set expandtab
        au BufRead,BufNewFile *.js,*.java set tabstop=4
        au BufRead,BufNewFile *.js,*.java set shiftwidth=4
        au BufRead,BufNewFile *.js,*.java set autoindent
        au BufRead,BufNewFile *.js,*.java call matchadd("BadWhitespace", '/^\t\+/')
        au BufRead,BufNewFile *.js,*.java call matchadd("BadWhitespace", '/\s\+$/')
        au BufNewFile *.js,*.java set fileformat=unix
        au BufRead,BufNewFile *.js,*.java let b:comment_leader = '//'
augroup END

" Python, PEP-008
augroup langPython
        highlight BadWhitespace ctermbg=red guibg=red
        au BufRead,BufNewFile *.py,*.pyw set expandtab
        au BufRead,BufNewFile *.py,*.pyw retab
        au BufRead,BufNewFile *.py,*.pyw set textwidth=159
        au BufRead,BufNewFile *.py,*.pyw set tabstop=4
        au BufRead,BufNewFile *.py,*.pyw set softtabstop=4
        au BufRead,BufNewFile *.py,*.pyw set shiftwidth=4
        au BufRead,BufNewFile *.py,*.pyw set autoindent
        au BufRead,BufNewFile *.py,*.pyw call matchadd("BadWhitespace", '/^\t\+/')
        au BufRead,BufNewFile *.py,*.pyw call matchadd("BadWhitespace", '/\s\+$/')
        au BufNewFile *.py,*.pyw set fileformat=unix
        au BufRead,BufNewFile *.py,*.pyw let b:comment_leader = '#'
augroup END

" Makefile
augroup langMake
        au BufRead,BufNewFile Makefile* set noexpandtab
augroup END

"XML language to include XenRT sequence file extensions
augroup langXML
        au BufNewFile,BufRead *.seq set syntax=xml
        au BufRead,BufNewFile *.xml,*.seq set expandtab
        au BufRead,BufNewFile *.xml,*.seq set tabstop=2
        au BufRead,BufNewFile *.xml,*.seq set softtabstop=2
        au BufRead,BufNewFile *.xml,*.seq set shiftwidth=2
        au BufRead,BufNewFile *.xml,*.seq retab
        au BufRead,BufNewFile *.xml,*.seq set autoindent
        au BufRead,BufNewFile *.xml,*.seq call matchadd("BadWhitespace", '/^\t\+/')
        au BufRead,BufNewFile *.xml,*.seq call matchadd("BadWhitespace", '/\s\+$/')
        au BufNewFile *.xml,*.seq set fileformat=unix
        au BufRead,BufNewFile *.xml,*.seq let b:comment_leader = '<!-- '
augroup END

augroup langJSON
        au BufRead,BufNewFile *.json set expandtab
        au BufRead,BufNewFile *.json set tabstop=2
        au BufRead,BufNewFile *.json set softtabstop=2
        au BufRead,BufNewFile *.json set shiftwidth=2
        au BufRead,BufNewFile *.json retab
        au BufRead,BufNewFile *.json set autoindent
        au BufRead,BufNewFile *.json call matchadd("BadWhitespace", '/^\t\+/')
        au BufRead,BufNewFile *.json call matchadd("BadWhitespace", '/\s\+$/')
        au BufNewFile *.json set fileformat=unix
augroup END
