#!/bin/bash
# Setup neovim for container

USER=$(id -u -n)

# Install neovim modules
pip3 install --user -U -r /home/${USER}/py_plugin.requirements

# Install nvim plugin
mkdir -p /home/${USER}/Dev/notes-in-vim
nvim +PlugInstall +PlugUpdate +PlugUpgrade +qa
nvim +UpdateRemotePlugins +qa
