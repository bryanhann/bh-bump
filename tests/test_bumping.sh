#!/usr/bin/env bash
bats="${0%.*}.bats"
pushd $(dirname $0) > /dev/null
export SRC=$(dirname $PWD)
pushd $(dirname $0) > /dev/null


export VIRTUAL_ENV=
export M88_P=/tmp/bh-bump.magic/$RANDOM/tmp-$RANDOM
export BATS=/tmp/bh-bump.magic/bats
git clone https://github.com/sstephenson/bats $BATS
mkdir -p ${M88_P}
pushd ${M88_P} > /dev/null
uv init --no-workspace
uv add --editable ${SRC}
uv run bh-bump --help
popd

$BATS/bin/bats $bats
