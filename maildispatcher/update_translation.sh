#!/bin/sh

intltool-extract --type=gettext/glade share/maildispatcher/glade/maildispatcher.glade
xgettext -k_ -kN_ -o translations/maildispatcher.pot share/maildispatcher/lib/maildispatcher/*.py share/maildispatcher/glade/maildispatcher.glade.h
rm share/maildispatcher/glade/maildispatcher.glade.h
msgmerge -U translations/ru.po translations/maildispatcher.pot
