#!/bin/bash
# Setup neovim for container

# Install neovim modules
pip3 install --user python_language_server
pip3 install --user neovim
pip3 install --user pynvim
pip3 install --user jedi
pip3 install --user flake8
pip3 install --user autopep8

# Install nvim plugin
USER=$(id -u -n)
mkdir -p /home/${USER}/Dev/notes-in-vim
nvim +PlugInstall +PlugUpdate +PlugUpgrade +qa
nvim +UpdateRemotePlugins +qa
