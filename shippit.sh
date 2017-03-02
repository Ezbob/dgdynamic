#!/bin/sh

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
BUILD_DIR=$CUR_DIR/dgdsl
COMMENT="Deviation Graph Dynamic Simulation Liberary version 0.9 by Anders Busch (2017)"

# copy stuff over from the git index
git checkout-index --all -f --prefix=$BUILD_DIR/
cd $BUILD_DIR
rm -rf shippit.sh tests/
cd $CUR_DIR

makeself --notemp $BUILD_DIR dgdsl.run "$COMMENT" ./shipping/init.sh

rm -rf $BUILD_DIR
