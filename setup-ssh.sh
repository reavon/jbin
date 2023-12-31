#!/bin/bash

# Original file lives in https://gist.github.com/menduz/709c68518a0baea40f6942b987423819

printf "\n> Setting up agent files...\n"

test_gpg() {
  # ===
  # Test GPG
  # ===

  printf "> 👾 Testing GPG signature, you will have to write the passphrase...\n"

  echo "test" > ~/test.txt
  rm ~/test.txt.asc &> /dev/null || true
  gpg --armor --sign ~/test.txt
  cat ~/test.txt.asc
}

# ===
# setup SSH
# ===

(mkdir -p ~/.ssh || true)
(mkdir -p ~/.gnupg || true)

chmod 700 ~/.ssh
chmod 700 ~/.gnupg

touch ~/.ssh/known_hosts
chmod 644 ~/.ssh/known_hosts

printf "\n> Installing dependencies...\n"

eval "$(brew shellenv)"

alias grep=ggrep

MY_BREW_PREFIX=$(brew --prefix)

cat <<GPG_AGENT_CONF > "$HOME/.gnupg/gpg-agent.conf"
# THIS FILE IS AUTOGENERATED, DO NOT EDIT IT.
pinentry-program $MY_BREW_PREFIX/bin/pinentry-mac

# enables SSH support (ssh-agent)
enable-ssh-support

# writes environment information to ~/.gpg-agent-info
write-env-file
use-standard-socket

# default cache timeout of 600 seconds
default-cache-ttl 600
max-cache-ttl 7200
GPG_AGENT_CONF

chmod 644 "$HOME/.gnupg/gpg-agent.conf"

cat <<GPG_AGENT_CONF > "$HOME/.gnupg/scdaemon.conf"
# THIS FILE IS AUTOGENERATED

reader-port Yubico Yubi
disable-ccid

# debug-all
# debug-level guru
# log-file /tmp/scd.log
GPG_AGENT_CONF

chmod 644 "$HOME/.gnupg/scdaemon.conf"

printf "\n> Killing agents...\n"

# grep is intalled here
export PATH="/usr/local/opt/grep/libexec/gnubin:$PATH"

# ===
# Initialize GPG & SSH
# ===

gpgconf --kill gpg-agent &> /dev/null || true
pkill gpg &> /dev/null || true
pkill pinentry &> /dev/null || true
pkill ssh-agent &> /dev/null || true
# Restart the gpg agent.
killall scdaemon &> /dev/null || true
killall gpg-agent &> /dev/null || true
killall ssh-agent &> /dev/null || true
echo ">   ok"

printf "\n> Starting agent...\n"
# Launch gpg-agent
r=$(gpg-connect-agent /bye 2>&1)
echo ">   ret: $? $r"

printf "\n> Starting SSH agent...\n"
# When using SSH support, use the current TTY for passphrase prompts
r=$(gpg-connect-agent updatestartuptty /bye 2>&1)
echo ">   ret: $? $r"

printf "\n> Starting GPG agent...\n"
# Point the SSH_AUTH_SOCK to the one handled by gpg-agent
if [ -S "$(gpgconf --list-dirs agent-ssh-socket)" ]; then
  export SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)
  echo "  OK Socket=$SSH_AUTH_SOCK"
else
  echo "⚠️ $(gpgconf --list-dirs agent-ssh-socket) doesn't exist. Is gpg-agent running ?"
fi

# ===
# Get our keys
# ===
printf "\n> 👾 Testing git connection, you will have to write the passphrase and Touch your YubiKey!...\n"
ssh-add -L | grep "cardno" > ~/.ssh/id_rsa_yubikey.pub
rawgit=$(ssh -T git@github.com 2>&1)
username=$(echo "$rawgit" | grep -Po --color=never "(?<=Hi ).*(?=\!)")
if [ -z "$username" ]; then
  echo ">   ! Error connecting with GitHub. Make sure the SSH is added to your account."
  echo ">     The SSH stored in the card is:"
  cat ~/.ssh/id_rsa_yubikey.pub
  echo ">     The response from github was:"
  echo "$rawgit"
else
  echo ">     Username: $username"
  echo ">     Importing GPG from https://github.com/${username}.gpg"
  curl --silent "https://github.com/${username}.gpg" | gpg --import
fi

echo ""

# ===
# git GPG
# ===

printf "> Setting up GPG signature...\n"

CARD_MAIL=$(gpg --card-status | grep -Po --color=never "(?<=<).*(?=>)")
if [[ $? == 0 ]]; then
  echo ">   Using git mail: ${CARD_MAIL}"
  git config --global user.email "${CARD_MAIL}"
else
  echo ">   ! Cannot find CARD_MAIL"
fi

CARD_NAME=$(gpg --card-status | grep -Po --color=never "(?<=[0-9]{4}-[0-9]{2}-[0-9]{2} ).*(?= <${CARD_MAIL})")
if [[ $? != 0 ]]; then
  echo ">   ! Cannot find CARD_NAME."
else
  echo ">   Using git name: ${CARD_NAME}"
  git config --global user.name "${CARD_NAME}"
fi

KEY_ID=$(gpg --card-status --keyid-format 0xlong | sed -n 's/: pub//gp' | grep -Po "0x[A-F0-9]{16}")
if [[ $? == 0 ]]; then
  echo ">   Using GPG key for git: ${KEY_ID}"

  git config --global commit.gpgsign true
  git config --global user.signingkey "${KEY_ID}"

  echo ">   Git configured using GPG:${KEY_ID} NAME:${CARD_NAME} MAIL:${CARD_MAIL}"

cat <<GPG_KEY_CONF > "$HOME/.user-data"
# THIS FILE IS AUTOGENERATED, DO NOT EDIT IT.

export GPG_KEY="${KEY_ID}"
GPG_KEY_CONF

  echo ""
  test_gpg
else
  echo ">   ! Cannot find KEY_ID"
  echo ">   FAILED!"
fi
