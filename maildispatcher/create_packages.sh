#!/bin/sh

python setup.py sdist
python setup.py bdist_rpm
rpm --addsign dist/maildispatcher-0.2-1.noarch.rpm
