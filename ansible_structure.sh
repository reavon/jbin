#!/bin/bash

export ANSIBLE_HOME=$HOME/Projects/mantoso/projects/ansible/

if [[ -z "$ANSIBLE_HOME" ]]; then
    echo 'You must have $ANSIBLE_HOME set to run this script' 1>&2
    exit 1
fi

mkdir -p "$ANSIBLE_HOME"

cd "$ANSIBLE_HOME" || exit

if [ ! -d "$ANSIBLE_HOME/ansible-site" ]; then
    git clone git@github.com:mantoso/ansible-site.git
    cd "$ANSIBLE_HOME/ansible-site" || exit
fi

if [ ! -f "$ANSIBLE_HOME"/ansible-site/README.md ]; then
    touch README.md
    touch ansible.cfg

    stages="production staging testing integration"

    mkdir -p {.bin,bin,misc,pkistore,playbooks/{files,handlers,tasks,templates,vars}}

    for dir in $stages; do
      mkdir -p inventory/"$dir"/{{group_vars,host_vars}/all,inventory}
      touch inventory/"$dir"/inventory/hosts.yml
    done

    ln -s playbooks/files files
    ln -s playbooks/handlers handlers
    ln -s playbooks/tasks tasks
    ln -s playbooks/templates templates
    ln -s playbooks/vars vars
fi

mkdir -p ../ansible-roles
mkdir -p ../ansible-collections

ln -s ../ansible-roles roles
ln -s ../ansible-collections collections

mkdir -p roles/{local,public}

touch roles/requirements.yml

