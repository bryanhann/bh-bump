#!/usr/bin/env bash

setup () {
    [ ! -f ${BATS_PARENT_TMPNAME}.skip ] || skip "skip remaining tests"
    [ ${MAGIC_XXX}. == . ] && export MAGIC_XXX=/tmp/bh-bump.test/$RANDOM 
    cd ${M88_P}
    [ -f ./pyproject.toml ] || { echo CRAZY; exit 1; }
}

teardown() {
    [ -n "$BATS_TEST_COMPLETED" ] || touch ${BATS_PARENT_TMPNAME}.skip
}

checkv () {
    [ $1 == $(uv run bh-bump version) ]
}

checkt () {
    git fetch origin tag v$1
}

check () {
    [ $1 == $(uv run bh-bump version) ]
    [ "$1" == "0.1.0" ] && return
    git fetch origin tag v$1
}

mybump () { 
    cd ${M88_P}
    uv run bh-bump $* --wet
}

init    () { mybump init    ; }
build   () { mybump build   ; }
release () { mybump release ; }
patch   () { mybump patch   ; }
minor   () { mybump minor   ; }
major   () { mybump major   ; }

@test "0.1.0             " { true    ; check 0.1.0     ; }
@test "init    0.1.0-b0  " { init    ; check 0.1.0-b0  ; }
@test "release 0.1.0-rc0 " { release ; check 0.1.0-rc0 ; }
@test "build   0.1.0-rc1 " { build   ; check 0.1.0-rc1 ; }
@test "patch   0.1.1-b0  " { patch   ; true            ; }
@test "checkv  0.1.1-b0  " { true    ; checkv 0.1.1-b0 ; }
@test "checkt  0.1.1-b0  " { true    ; checkt 0.1.1-b0 ; }
@test "minor   0.2.0-b0  " { minor   ; check 0.2.0-b0  ; }
@test "major   1.0.0-b0  " { major   ; check 1.0.0-b0  ; }
