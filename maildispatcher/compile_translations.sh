#!/bin/sh

if grep -q -e '^#,.*fuzzy.*' translations/ru.po; then
    echo "Fuzzy string have been found. Please fix it before compilation!"
    exit 1
fi
msgfmt translations/ru.po -o share/maildispatcher/i18n/ru/LC_MESSAGES/maildispatcher.mo
