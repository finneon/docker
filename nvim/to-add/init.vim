""""""" The code to check and download Vim-Plug is found here:
""""""" https://github.com/yous/dotfiles/blob/e6f1e71b6106f6953874c6b81f0753663f901578/vimrc#L30-L81
if !empty(&rtp)
    let s:vimfiles = split(&rtp, ',')[0]
else
    echohl ErrorMsg
    echomsg 'Unable to determine runtime path for Vim.'
    echohl NONE
endif

" Install vim-plug if it isn't installed and call plug#begin() out of box
function! s:DownloadVimPlug()
    if !exists('s:vimfiles')
        return
    endif
    if empty(glob(s:vimfiles . '/autoload/plug.vim'))
        let plug_url = 'https://github.com/junegunn/vim-plug.git'
        let tmp = tempname()
        let new = tmp . '/plug.vim'
        try
            let out = system(printf('git clone --depth 1 %s %s', plug_url, tmp))
            if v:shell_error
                echohl ErrorMsg
                echomsg 'Error downloading vim-plug: ' . out
                echohl NONE
                return
            endif
            if !isdirectory(s:vimfiles . '/autoload')
                call mkdir(s:vimfiles . '/autoload', 'p')
            endif
            call rename(new, s:vimfiles . '/autoload/plug.vim')
            " Install plugins at first
            autocmd VimEnter * PlugInstall | quit
        finally
            if isdirectory(tmp)
                let dir = '"' . escape(tmp, '"') . '"'
                silent call system((has('win32') ? 'rmdir /S /Q ' : 'rm -rf ') . dir)
            endif
        endtry
    endif
    call plug#begin(s:vimfiles . '/plugged')
    "" Asynchronous lint engine
    " Enable autocomplete
    let g:ale_completion_enabled = 1 | Plug 'w0rp/ale', {'branch': 'v2.4.x'}
    "" Language server autocompletion with coc.nvim
    " Plug 'neoclide/coc.nvim', {'tag': '*', 'do': { -> coc#util#install()}}
    "" More autocomplete
    if has('nvim')
      Plug 'Shougo/deoplete.nvim', { 'do': ':UpdateRemotePlugins' }
    else
      Plug 'Shougo/deoplete.nvim'
      Plug 'roxma/nvim-yarp'
      Plug 'roxma/vim-hug-neovim-rpc'
    endif
    let g:deoplete#enable_at_startup = 1
    " Function argument completion
    Plug 'Shougo/neosnippet'
    Plug 'Shougo/neosnippet-snippets'
    let g:neosnippet#enable_completed_snippet = 1
    "" Fuzzy finder
    Plug 'mhinz/vim-grepper', {'on': ['Grepper', '<plug>(GrepperOperator)']}
    "" Add surrounding brackets, quotes, xml tags,...
    Plug 'tpope/vim-surround'
    "" Extended matching for the % operator
    Plug 'adelarsq/vim-matchit'
    " Auto-completion for pairs
    Plug 'Raimondi/delimitMate'
    "" Edit a region in new buffer
    Plug 'chrisbra/NrrwRgn'
    "" Tree explorer
    " Plug 'scrooloose/nerdtree', {'on': ['NERDTreeToggle', 'NERDTreeFind']} | Plug 'Xuyuanp/nerdtree-git-plugin' | Plug 'ryanoasis/vim-devicons'
    Plug 'scrooloose/nerdtree', {'on': ['NERDTreeToggle', 'NERDTreeFind']} | Plug 'Xuyuanp/nerdtree-git-plugin'
    "" Tag tree
    Plug 'majutsushi/tagbar'
    "" Run shell command asynchronously
    Plug 'skywind3000/asyncrun.vim'
    "" Text object per indent level
    Plug 'michaeljsmith/vim-indent-object'
    "" Code commenting
    Plug 'tpope/vim-commentary'
    "" Git gutter
    Plug 'airblade/vim-gitgutter'
    "" Git wrapper
    Plug 'tpope/vim-fugitive'
    "" Git management inside vim
    Plug 'jreybert/vimagit'
    "" Automatically toggle relative line number
    Plug 'jeffkreeftmeijer/vim-numbertoggle'
    "" Use registers as stack for yank and delete
    Plug 'maxbrunsfeld/vim-yankstack'
    "" Status line
    Plug 'itchyny/lightline.vim'
    "" Show buffer in tabline
    "Plug 'mgee/lightline-bufferline'
    "" Delete buffers without messing window layout
    Plug 'moll/vim-bbye'
    "" Show lint errors and warnings on status line
    Plug 'maximbaz/lightline-ale'
    "" Maintain coding style per project
    Plug 'editorconfig/editorconfig-vim'
    "" Language specific plugins
    " Python
    Plug 'nvie/vim-flake8', {'for': 'python'}
    Plug 'davidhalter/jedi-vim', {'for': 'python'}
    "" Detect file encoding
    Plug 's3rvac/AutoFenc'
    "" Indent line
    Plug 'Yggdroot/indentLine'
    "" Start screen
    Plug 'mhinz/vim-startify'
    "" Theme
    Plug 'morhetz/gruvbox'
    "Plug 'ayu-theme/ayu-vim'
    call plug#end()
endfunction

call s:DownloadVimPlug()

"""" Theme section
syntax enable
syntax on
"" GruvBox
highlight Normal ctermbg=black ctermfg=white
let g:gruvbox_italic=1
let g:gruvbox_contrast_dark = 'hard'
let g:gruvbox_invert_tabline = 1
let g:gruvbox_invert_indent_guides=1
"" Ayu
let ayucolor="dark"
try
    colorscheme gruvbox  "use the theme gruvbox
catch /^Vim\%((\a\+)\)\=:E185/
    colorscheme default
    set background=dark
endtry

"""" End theme section

"""" Misc section
if has('gui_running')
    set t_Co=256
    " set guioptions-=m  "remove menu bar
    set guioptions-=T   "remove toolbar
    set guioptions-=r   "remove right-hand scroll bar
    set guioptions-=L   "remove left-hand scroll bar
    set guioptions-=e   "Use tabline from configs instead of GUI
endif
set hidden
set cmdheight=2
"set encoding=utf-8
set mouse=a
"set guifont=Iosevka\ Nerd\ Font\ Mono:h13
" set smartcase
set smartindent
set confirm
set autoread
set number
set relativenumber
set cursorline
set scrolloff=10
set wrap
set colorcolumn=80,100,120,140,160,180,200
set binary
set list
set listchars=eol:$,tab:>-,trail:_,extends:>,precedes:<
set backspace=indent,eol,start
set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab
set spell
set completeopt+=preview
set completeopt+=menuone
set completeopt+=longest
"""" End misc section

"""" Keyboard shortcuts section
"" Change leader key
let mapleader = " "
"" Visual indication of leader key timeout
set showcmd
"" Copy and paste
vnoremap <C-c> "+yi
vnoremap <C-x> "+c
vnoremap <S-Insert> c<ESC>"+p
inoremap <S-Insert> <ESC>"+pa
"" Map Ctrl-Del to delete word
inoremap <C-Delete> <ESC>dwi
"" Use ESC to exit insert mode in :term
" tnoremap <Esc> <C-\><C-n>
"" Tab to autocomplete if in middle of line
function! InsertTabWrapper()
	let col = col('.') - 1
	if !col || getline('.')[col - 1] !~ '\k'
		return "\<tab>"
	else
		return "\<c-n>"
	endif
endfunction
inoremap <expr> <tab> InsertTabWrapper()
inoremap <s-tab> <c-p>"
"" Expand CR when auto-completing pairs
let g:delimitMate_expand_cr = 2
let g:delimitMate_expand_space = 1
let g:delimitMate_expand_inside_quotes = 1
let g:delimitMate_jump_expansion = 1
"" Toggle NERDTree
map <Leader>f :NERDTreeToggle<CR>
nnoremap <silent> <Leader>v :NERDTreeFind<CR>
"" Delete buffer without messing layout
nnoremap <Leader>x :Bd<CR>
"" Quickly switch between buffers
"nmap <Leader>1 <Plug>lightline#bufferline#go(1)
"nmap <Leader>2 <Plug>lightline#bufferline#go(2)
"nmap <Leader>3 <Plug>lightline#bufferline#go(3)
"nmap <Leader>4 <Plug>lightline#bufferline#go(4)
"nmap <Leader>5 <Plug>lightline#bufferline#go(5)
"nmap <Leader>6 <Plug>lightline#bufferline#go(6)
"nmap <Leader>7 <Plug>lightline#bufferline#go(7)
"nmap <Leader>8 <Plug>lightline#bufferline#go(8)
"nmap <Leader>9 <Plug>lightline#bufferline#go(9)
"nmap <Leader>0 <Plug>lightline#bufferline#go(10)
"" Key mapping for navigating between errors
nnoremap <silent> <C-k> <Plug>(ale_previous_wrap)
nnoremap <silent> <C-j> <Plug>(ale_next_wrap)
"" Key mapping for IDE-like behaviour
nnoremap <silent> K :ALEHover<CR>
nnoremap <silent> gd :ALEGoToDefinition<CR>
nnoremap <silent> gr :ALEFindReferences<CR>
"""" End keyboard shortcuts section

"""" Indentation config section
autocmd FileType xml setlocal shiftwidth=2 tabstop=2 expandtab
autocmd FileType json setlocal shiftwidth=2 tabstop=2 expandtab
"""" End indentation config section

"""" Directory tree browser section
" let NERDTreeQuitOnOpen = 1
let NERDTreeAutoDeleteBuffer = 1
let NERDTreeMinimalUI = 1
let NERDTreeDirArrows = 1
"""" End directory tree browser section

"""" Statusline/tabline section
let g:lightline = {
            \ 'colorscheme': 'seoul256',
            \ }
let g:lightline.enable = {
            \ 'statusline': 1,
            \ 'tabline': 1
            \ }
" let g:lightline.separator = {
"             \ 'left': '', 'right': ''
"             \ }
" let g:lightline.subseparator = {
"             \ 'left': '', 'right': ''
"             \ }
function! LightLinePercent()
    if &ft !=? 'nerdtree'
        return line('.') * 100 / line('$') . '%'
    else
        return ''
    endif
endfunction
function! LightLineLineInfo()
    if &ft !=? 'nerdtree'
        return line('.').':'. col('.')
    else
        return ''
    endif
endfunction
function! Filetype()
    " return winwidth(0) > 70 ? (strlen(&filetype) ? &filetype . ' ' . WebDevIconsGetFileTypeSymbol() : 'no ft') : ''
    return winwidth(0) > 70 ? (strlen(&filetype) ? &filetype : 'no ft') : ''
endfunction

function! Fileformat()
    " return winwidth(0) > 70 ? (&fileformat . ' ' . WebDevIconsGetFileFormatSymbol()) : ''
    return winwidth(0) > 70 ? (&fileformat) : ''
endfunction
"let g:lightline.component_expand = {
"            \ 'buffers': 'lightline#bufferline#buffers',
"            \ 'linter_checking': 'lightline#ale#checking',
"            \ 'linter_warnings': 'lightline#ale#warnings',
"            \ 'linter_errors': 'lightline#ale#errors',
"            \ 'linter_ok': 'lightline#ale#ok',
"            \ }
"let g:lightline.component_type = {
"            \ 'buffers': 'tabsel',
"            \ 'linter_checking': 'left',
"            \ 'linter_warnings': 'warning',
"            \ 'linter_errors': 'error',
"            \ 'linter_ok': 'left',
"            \ }
let g:lightline.component_expand = {
            \ 'linter_checking': 'lightline#ale#checking',
            \ 'linter_warnings': 'lightline#ale#warnings',
            \ 'linter_errors': 'lightline#ale#errors',
            \ 'linter_ok': 'lightline#ale#ok',
            \ }
let g:lightline.component_type = {
            \ 'linter_checking': 'left',
            \ 'linter_warnings': 'warning',
            \ 'linter_errors': 'error',
            \ 'linter_ok': 'left',
            \ }
let g:lightline.component_function = {
            \ 'percent': 'LightLinePercent',
            \ 'lineinfo': 'LightLineLineInfo',
            \ 'filetype': 'Filetype',
            \ 'fileformat': 'Fileformat',
            \ }
"" Statusline
set noshowmode
let g:lightline.active = {
            \   'right': 
            \       [
            \           [ 'lineinfo' ],
            \           [ 'percent' ],
            \           [
            \               'linter_checking',
            \               'linter_errors',
            \               'linter_warnings',
            \               'linter_ok',
            \           ],
            \       ],
            \}
"" Tabline
set showtabline=2
" let g:lightline#bufferline#enable_devicons = 0
" let g:lightline#bufferline#unicode_symbols = 1
" let g:lightline#bufferline#show_number = 0
" let g:lightline#bufferline#number_map = {
"             \ 0: '⁰', 1: '¹', 2: '²',
"             \ 3: '³', 4: '⁴', 5: '⁵',
"             \ 6: '⁶', 7: '⁷', 8: '⁸',
"             \ 9: '⁹'}
let g:lightline.tabline = {
            \ 'right': [
            \   ['close'],
            \   ['fileformat',
            \    'fileencoding',
            \    'filetype'],
            \ ]}
"" Linting options
" let g:lightline#ale#indicator_checking = "\uf110"
" let g:lightline#ale#indicator_warnings = "\uf071"
" let g:lightline#ale#indicator_errors = "\uf05e"
" let g:lightline#ale#indicator_ok = "\uf00c"
let g:lightline#ale#indicator_checking = "≒"
let g:lightline#ale#indicator_warnings = "¡"
let g:lightline#ale#indicator_errors = "※"
let g:lightline#ale#indicator_ok = "●"
"""" End status line section

"""" Linting section
" Keep the sign gutter open at all times
let g:ale_sign_column_always = 1
let g:ale_sign_error = 'X'
let g:ale_sign_warning = 'i'
" Lint on text change
"let g:ale_lint_on_text_changed = 'never'
"let g:ale_lint_on_text_changed = 'normal'
" Lint on opening a file
let g:ale_lint_on_enter = 0
" Fix files when you saving
let g:ale_fix_on_save = 0
" Show 3 lines of errors (default: 10)
let g:ale_list_window_size = 3
"" Explicitly enable linters
let g:ale_linters = {   'python': [
            \               'pyls',
            \               'flake8',
            \               'mypy',
            \               'prospector',
            \               'pycodestyle',
            \               'pyflakes',
            \               'pylint',
            \               'pyre',
            \               'vulture',
            \           ],
            \       }
"" Explicitly enable fixers
let g:ale_fixers = {    'python': [
            \               'add_blank_lines_for_python_control_statements',
            \               'autopep8',
            \               'black',
            \               'isort',
            \               'yapf',
            \           ],
            \           '*': [
            \                   'remove_trailing_lines',
            \                   'trim_whitespace',
            \           ],
            \      }
"""" End linting section

"""" Load external config per project
" exrc allows loading local executing local rc files.
set exrc
