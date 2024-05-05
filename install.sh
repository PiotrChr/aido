#!/bin/bash

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3."
    exit 1
fi

if ! command -v zsh &> /dev/null; then
    echo "zsh is not installed. Please install zsh."
    exit 1
fi

COMMAND_SCRIPT_PATH="./aido_daemon.py"
ZSH_AIDO_FUNCTION_PATH="./zsh_aido_function"

if [ ! -f $COMMAND_SCRIPT_PATH ]; then
    echo "Aido command script not found at $COMMAND_SCRIPT_PATH."
    exit 1
fi


cp zsh_aido_function $HOME/zsh_aido_function
cp aido_daemon.py $HOME/aido_daemon.py

if [ ! -f $ZSH_AIDO_FUNCTION_PATH ]; then
    echo "Zsh aido function script not found at $ZSH_AIDO_FUNCTION_PATH."
    exit 1
fi


echo "Please enter the working directory for AIDO (e.g., /Users/piotrchrusciel/Documents/Work/Programming):"
read AIGO_WORK_DIR
echo "export AIGO_WORK_DIR=$AIGO_WORK_DIR" >> ~/.bash_profile
echo "export AIGO_WORK_DIR=$AIGO_WORK_DIR" >> ~/.zshrc

echo "Please enter the port number for the AIDO socket connection (e.g., 5050):"
read AIGO_PORT
echo "export AIGO_PORT=$AIGO_PORT" >> ~/.bash_profile
echo "export AIGO_PORT=$AIGO_PORT" >> ~/.zshrc


chmod +x $COMMAND_SCRIPT_PATH

# Add the ZSH aido function to .zshrc if not already present
if ! grep -Fxq "source $ZSH_AIDO_FUNCTION_PATH" ~/.zshrc; then
    echo "source $ZSH_AIDO_FUNCTION_PATH" >> ~/.zshrc
fi

echo "Installation complete. Use 'aido' command from your terminal."
