#!/bin/bash

export PYTHONPATH=""$(mod --nopost | grep 'mod:' | awk '{print $2}')":"$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)":"
echo "Exported "$PYTHONPATH" to Python Path"
