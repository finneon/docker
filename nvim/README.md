## Docker container for nvim
Create docker image which contains nvim configuration, installed plugins. When using by typing 'nvim' it will create a docker instance, mount user's workspace and enter to nvim

### Getting Started
1. Build ubuntu-nvim image
```
./docker-build.nvim
```
2. Customize nvim
```
cat > /usr/bin/nvim <<EOF
/home/vudao/workspace/docker/nvim/docker-run
EOF

chmod u+x /usr/bin/nvim
```
3. Go to the workspace
```
nvim
```

### Structure inside
1. Install neovim according to the offical document [here](https://github.com/neovim/neovim/wiki/Installing-Neovim)
2. Configuration files:
 - ~/.config/nvim/init.vim
3. Plugin manager:
 - ~/.config/nvim/autoload
