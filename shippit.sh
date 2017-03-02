#!/bin/sh

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
BUILD_DIR=$CUR_DIR/build
COMMENT="Deviation Graph Dynamic Simulation Liberary version 0.9"

# copy stuff over from the git index
git checkout-index --all -f --prefix=$BUILD_DIR/
cd $BUILD_DIR
rm -rf shippit.sh tests/
cd $CUR_DIR

makeself --notemp --current $CUR_DIR/dgDynamic dgdsl.run $COMMENT $CUR_DIR/build/shipping/init.sh

rm -rf $BUILD_DIR
