#!/bin/bash

set -e

black="\033[0;30m"
red="\033[0;31m"
bred="\033[1;31m"
green="\033[0;32m"
bgreen="\033[1;32m"
yellow="\033[0;33m"
byellow="\033[1;33m"
blue="\033[0;34m"
bblue="\033[1;34m"
purple="\033[0;35m"
bpurple="\033[1;35m"
cyan="\033[0;36m"
bcyan="\033[1;36m"
white="\033[0;37m"
nc="\033[00m"

Pbx_logo = f'''
{bred}┏━━━┓━━━━━━━━━━━━━━━┏┓━┏┓━
{bblue}┃┏━┓┃━━━━━━━━━━━━━━━┃┃━┃┃━
{yellow}┃┗━┗┛┏━━┓┏━━┓━┏━━━━┓┗━━━┛━
{bpurple}┏┓━┓┃┃ＰＢＸ┃┃ＭＵＳＩＣ┃━┃┏┓┏┓┃┏━━━┓━
{bpurple}┃┗━┛┃┃┗┛┃┃┗━┗┓┃┃┃┃┃┃┃┃━┃┃━
{byellow}┗━━━┛┃━━┛┗━━━┛┗┛┗┛┗┛┗┛━┗┛━
{bblue}━━━━━┃┃━━━━━━━━━━━━━━━━━━━
{bred}━━━━━┗┛━━━━━━━━━━━━━━━━━━━
'''

pprint (){
    local cred='\033[0;31m'
    local cgreen='\033[0;32m'
    local cyellow='\033[0;33m'
    local cblue='\033[0;34m'
    local cpurple='\033[0;35m'
    local color="$cpurple"

    case $2 in
        "cred") color="$cred" ;;
        "cgreen") color="$cgreen" ;;
        "cyellow") color="$cyellow" ;;
        "cblue") color="$cblue" ;;
    esac

    printf "$color $1\033[0;37m"
}

color_reset(){ printf '\033[0;37m'; }

yesnoprompt(){
    old_stty_cfg=$(stty -g)
    stty raw -echo
    answer=$(head -c 1)
    stty $old_stty_cfg
    echo "$answer" | grep -iq "^y"
}

update() {
    pprint "\n\nUpdating package list.. "
    if sudo apt update 2>&1 | grep "can be upgraded" &>/dev/null; then
        pprint "UPDATE AVAILABLE" "cgreen"
        pprint "\n\nDo you want to automatically upgrade (y/n)?"
        if yesnoprompt; then
            pprint "\n\nUpgrading packages.. "
            if sudo apt upgrade -y &>/dev/null; then
                pprint "DONE!\n\n" "cgreen"
            else
                pprint "FAIL.\n\n" "cred"
                exit 1
            fi
        else
            echo
        fi
    else
        pprint "ALREADY UP TO DATE\n\n" "cgreen"
    fi
}

packages(){
    if ! command -v pip &>/dev/null; then
        pprint "Couldn't find pip, installing now..."
        if sudo apt install python3-pip -y 2>pypilog.txt 1>/dev/null; then
            pprint "SUCCESS.\n\n" "cgreen"
        else
            pprint "FAIL.\n\n" "cred"
            exit 1
        fi
    fi

    if ! command -v ffmpeg &>/dev/null; then
        pprint "Couldn't find ffmpeg, installing now..."
        if sudo apt install ffmpeg -y &>/dev/null; then
            pprint "SUCCESS.\n\n" "cgreen"
        else
            pprint "FAIL.\n\n" "cred"
            pprint "You need to install ffmpeg manually in order to deploy PBXMUSIC, exiting...\n" "cblue"
            exit 1
        fi
    fi

    # Check ffmpeg version and warn user if necessary.
    if ffmpeg -version | grep -Po 'version (3.*?) ' &>/dev/null; then
        pprint "Playing live streams not going to work since you have ffmpeg $(ffmpeg -version | grep -Po 'version (3.*?) '), live streams are supported by version 4+.\n" "cblue"
    fi
}

node(){
    if command -v npm &>/dev/null; then
        return
    fi
    pprint "Installing Nodejs and Npm..  "
    curl -fsSL https://deb.nodesource.com/setup_19.x | sudo -E bash - &>nodelog.txt
    if sudo apt install -y nodejs &>>nodelog.txt && sudo npm i -g npm &>>nodelog.txt; then
        pprint "SUCCESS!\n" "cgreen"
    else
        pprint "FAIL.\n" "cred"
        exit 1
    fi
}

installation(){
    pprint "\n\nUpgrading pip and installing dependency packages..."
    if pip3 install -U pip &>>pypilog.txt && pip3 install -U -r requirements.txt &>>pypilog.txt; then
        pprint "DONE.\n" "cgreen"
    else
        pprint "FAIL.\n" "cred"
        exit 1
    fi
}

clear
pprint "${Pbx_logo}"
pprint "Welcome to PBXMUSIC Setup Installer\n\n"
pprint "If you see any error during Installation Process, Please refer to these files for logs: "
pprint "\nFor node js errors, Check nodelog.txt"
pprint "\nFor pypi packages errors, Check pypilog.txt"
sleep 1
pprint "\n\nScript needs sudo privileges in order to update & install packages.\n"
sudo true

update
packages
node
installation
pprint "\n\n\n\n\nPBXMUSIC Installation Completed !" "cgreen"
sleep 1
clear

pprint "API ID: " "cred"; color_reset; read api_id
pprint "\nAPI HASH: " "cgreen"; color_reset; read api_hash
pprint "\nBOT TOKEN: " "cyellow"; color_reset; read bot_token
pprint "\nOWNER ID: " "cblue"; color_reset; read ownid
pprint "\nMONGO DB URI: " "cgreen"; color_reset; read mongo_db
pprint "\nLOG GROUP ID: " "cblue"; color_reset; read logger_id
pprint "\nSTRING SESSION: " "cyellow"; color_reset; read Pbxstring_session

pprint "\n\nProcessing your vars, wait a while !" "cgreen"

if [ -f .env ]; then
    rm .env
fi

cat <<EOF > .env
API_ID=$api_id
API_HASH=$api_hash
BOT_TOKEN=$bot_token
DATABASE_URL=$mongo_db
LOGGER_ID=$logger_id
PBXBOT_SESSION=$Pbxstring_session
OWNER_ID=$ownid
EOF

clear
pprint "\n\n\nThanks for using PBXMUSIC installer, your vars have been saved successfully! \nIf you want to add more variables, add them in your env by: vi .env"
pprint "\n\nNow you can start the bot by: python3 -m Music\n\n"
