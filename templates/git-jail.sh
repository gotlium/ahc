#!/bin/bash

read oldrev newrev ref

MESSAGE=$(git log -1 $newrev --pretty=format:%%s)
USER=$(git log -1 $newrev --pretty=format:%an)
EMAIL=$(git log -1 $newrev --pretty=format:%ae)
BRANCH=${ref#refs/heads/}
GIT=$(which git)
DEBUG=1


function git_action() {
    if [ "$DEBUG" -eq "0" ]; then
        env -i GIT_COMMITTER_EMAIL="$EMAIL" GIT_AUTHOR_EMAIL="$EMAIL" \
            GIT_AUTHOR_NAME="$USER" GIT_COMMITTER_NAME="$USER" \
            $GIT $@ >& /dev/null
    else
        echo ">> git $@"
        env -i GIT_COMMITTER_EMAIL="$EMAIL" GIT_AUTHOR_EMAIL="$EMAIL" \
            GIT_AUTHOR_NAME="$USER" GIT_COMMITTER_NAME="$USER" \
            $GIT $@
    fi
}

function commit() {
    if [ "$DEBUG" -eq "0" ]; then
        env -i GIT_COMMITTER_EMAIL="$EMAIL" GIT_AUTHOR_EMAIL="$EMAIL" \
            GIT_AUTHOR_NAME="$USER" GIT_COMMITTER_NAME="$USER" \
            $GIT commit -am "$1" >& /dev/null
    else
        echo ">> git commit -am $1"
        env -i GIT_COMMITTER_EMAIL="$EMAIL" GIT_AUTHOR_EMAIL="$EMAIL" \
            GIT_AUTHOR_NAME="$USER" GIT_COMMITTER_NAME="$USER" \
            $GIT commit -am "$1"
    fi
}

function do_git {
    git_action "$1" origin "$BRANCH"
}

function ch_dir_and_go_to_branch {
    if [ ! "$DEBUG" -eq "0" ]; then
        echo "cd $1"
    fi
    cd "$1"
    CURRENT_BRANCH=$(env -i git symbolic-ref --short -q HEAD)
    git_action stash save

    if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
        IS_EXISTS=$(env -i git branch|grep "$BRANCH")
        if [ -z "$IS_EXISTS" ]; then
            git_action fetch --all
            git_action checkout -b "$BRANCH" "origin/$BRANCH"
            if [ "$?" != "0" ]; then
                git_action checkout -b "$BRANCH"
            fi
        else
            git_action checkout "$BRANCH"
        fi
    else
        git_action checkout "$BRANCH"
    fi
}

function push_to_origin_repository() {
    REPO_IS_EXISTS=$(git_action remote -v | cut -f1 | uniq | grep "repo")
    if [ ! -z "$REPO_IS_EXISTS" ]; then
        do_git "push"
    fi
}
