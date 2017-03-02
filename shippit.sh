#!/bin/sh

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
BUILD_DIR=$CUR_DIR/build

# copy stuff over from the git index
git checkout-index --all -f --prefix=$BUILD_DIR/
cd $BUILD_DIR
rm shippit.sh
cd $CUR_DIR


