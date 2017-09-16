#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}/..
rm -rf lib
rm -f output.zip
mkdir lib
pip install -r requirements.txt -t lib
cp -r src/* lib
cd lib
zip ../output.zip -r9 *
cd ${DIR}