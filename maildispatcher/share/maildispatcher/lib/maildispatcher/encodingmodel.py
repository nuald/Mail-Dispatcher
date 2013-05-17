#    This file is part of Maildispatcher.
#
#    Maildispatcher is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Maildispatcher is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Maildispatcher.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright 2007-2008 Alex Slesarev


"""encodingmodel.py
Encoding wrapper."""

import gtk, gobject

#All predefined encodings: http://docs.python.org/lib/standard-encodings.html
#Format: (name, aliases, description).
ENCODINGS = (('ascii', '646, us-ascii', _('English')),
('big5', 'big5-tw, csbig5', _('Traditional Chinese')),
('big5hkscs', 'big5-hkscs, hkscs', _('Traditional Chinese')),
('cp037', 'IBM037, IBM039', _('English')),
('cp424', 'EBCDIC-CP-HE, IBM424', _('Hebrew')),
('cp437', '437, IBM437', _('English')),
('cp500', 'EBCDIC-CP-BE, EBCDIC-CP-CH, IBM500', _('Western Europe')),
('cp737', '', _('Greek')),
('cp775', 'IBM775', _('Baltic languages')),
('cp850', '850, IBM850', _('Western Europe')),
('cp852', '852, IBM852', _('Central and Eastern Europe')),
('cp855', '855, IBM855',
    _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian')),
('cp856', '', _('Hebrew')),
('cp857', '857, IBM857', _('Turkish')),
('cp860', '860, IBM860', _('Portuguese')),
('cp861', '861, CP-IS, IBM861', _('Icelandic')),
('cp862', '862, IBM862', _('Hebrew')),
('cp863', '863, IBM863', _('Canadian')),
('cp864', 'IBM864', _('Arabic')),
('cp865', '865, IBM865', _('Danish, Norwegian')),
('cp866', '866, IBM866', _('Russian')),
('cp869', '869, CP-GR, IBM869', _('Greek')),
('cp874', '', _('Thai')),
('cp875', '', _('Greek')),
('cp932', '932, ms932, mskanji, ms-kanji', _('Japanese')),
('cp949', '949, ms949, uhc', _('Korean')),
('cp950', '950, ms950', _('Traditional Chinese')),
('cp1006', '', _('Urdu')),
('cp1026', 'ibm1026', _('Turkish')),
('cp1140', 'ibm1140', _('Western Europe')),
('cp1250', 'windows-1250', _('Central and Eastern Europe')),
('cp1251', 'windows-1251',
    _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian')),
('cp1252', 'windows-1252', _('Western Europe')),
('cp1253', 'windows-1253', _('Greek')),
('cp1254', 'windows-1254', _('Turkish')),
('cp1255', 'windows-1255', _('Hebrew')),
('cp1256', 'windows1256', _('Arabic')),
('cp1257', 'windows-1257', _('Baltic languages')),
('cp1258', 'windows-1258', _('Vietnamese')),
('euc_jp', 'eucjp, ujis, u-jis', _('Japanese')),
('euc_jis_2004', 'jisx0213, eucjis2004', _('Japanese')),
('euc_jisx0213', 'eucjisx0213', _('Japanese')),
('euc_kr',
    'euckr, korean, ksc5601, ks_c-5601, ks_c-5601-1987, ksx1001, ks_x-1001',
    _('Korean')),
('gb2312',
    'chinese, csiso58gb231280, euc-cn, euccn, eucgb2312-cn, gb2312-1980,'
    ' gb2312-80, iso-ir-58', _('Simplified Chinese')),
('gbk', '936, cp936, ms936', _('Unified Chinese')),
('gb18030', 'gb18030-2000', _('Unified Chinese')),
('hz', 'hzgb, hz-gb, hz-gb-2312', _('Simplified Chinese')),
('iso2022_jp', 'csiso2022jp, iso2022jp, iso-2022-jp', _('Japanese')),
('iso2022_jp_1', 'iso2022jp-1, iso-2022-jp-1', _('Japanese')),
('iso2022_jp_2', 'iso2022jp-2, iso-2022-jp-2',
    _('Japanese, Korean, Simplified Chinese, Western Europe, Greek')),
('iso2022_jp_2004', 'iso2022jp-2004, iso-2022-jp-2004', _('Japanese')),
('iso2022_jp_3', 'iso2022jp-3, iso-2022-jp-3', _('Japanese')),
('iso2022_jp_ext', 'iso2022jp-ext, iso-2022-jp-ext', _('Japanese')),
('iso2022_kr', 'csiso2022kr, iso2022kr, iso-2022-kr', _('Korean')),
('latin_1', 'iso-8859-1, iso8859-1, 8859, cp819, latin, latin1, L1',
    _('Western Europe')),
('iso8859_2', 'iso-8859-2, latin2, L2', _('Central and Eastern Europe')),
('iso8859_3', 'iso-8859-3, latin3, L3', _('Esperanto, Maltese')),
('iso8859_4', 'iso-8859-4, latin4, L4', _('Baltic languagues')),
('iso8859_5', 'iso-8859-5, cyrillic',
    _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian')),
('iso8859_6', 'iso-8859-6, arabic', _('Arabic')),
('iso8859_7', 'iso-8859-7, greek, greek8', _('Greek')),
('iso8859_8', 'iso-8859-8, hebrew', _('Hebrew')),
('iso8859_9', 'iso-8859-9, latin5, L5', _('Turkish')),
('iso8859_10', 'iso-8859-10, latin6, L6', _('Nordic languages')),
('iso8859_13', 'iso-8859-13', _('Baltic languages')),
('iso8859_14', 'iso-8859-14, latin8, L8', _('Celtic languages')),
('iso8859_15', 'iso-8859-15', _('Western Europe')),
('johab', 'cp1361, ms1361', _('Korean')),
('koi8_r', '', _('Russian')),
('koi8_u', '', _('Ukrainian')),
('mac_cyrillic', 'maccyrillic',
    _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian')),
('mac_greek', 'macgreek', _('Greek')),
('mac_iceland', 'maciceland', _('Icelandic')),
('mac_latin2', 'maclatin2, maccentraleurope', _('Central and Eastern Europe')),
('mac_roman', 'macroman', _('Western Europe')),
('mac_turkish', 'macturkish', _('Turkish')),
('ptcp154', 'csptcp154, pt154, cp154, cyrillic-asian', _('Kazakh')),
('shift_jis', 'csshiftjis, shiftjis, sjis, s_jis', _('Japanese')),
('shift_jis_2004', 'shiftjis2004, sjis_2004, sjis2004', _('Japanese')),
('shift_jisx0213', 'shiftjisx0213, sjisx0213, s_jisx0213', _('Japanese')),
('utf_16', 'U16, utf16', _('All languages')),
('utf_16_be', 'UTF-16BE', _('All languages (BMP only)')),
('utf_16_le', 'UTF-16LE', _('All languages (BMP only)')),
('utf_7', 'U7, unicode-1-1-utf-7', _('All languages')),
('utf_8', 'U8, UTF, utf8', _('All languages')))

#Max length of texts.
LEN_DESCRIPTION = 25
LEN_ENCODING = 15

#Model class with limited functionality
class EncodingModel:# pylint: disable-msg=R0903
    """Class for working with encoding model."""

    def __init__(self):
        """Initialize and populate encoding store."""
        self.store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.current = None
        for name, aliases, desc in ENCODINGS:
            enum = [name]
            if aliases:
                enum.append(aliases)
            iter = self.store.append((name,
                '%s (%s)' % (self.strip(desc, LEN_DESCRIPTION),
                             self.strip(', '.join(enum), LEN_ENCODING))))
            if 'utf_8' in name:
                self.current = iter
        self.store.set_sort_column_id(1, gtk.SORT_ASCENDING)

    @staticmethod
    def strip(string, length):
        """Strip string is required.
        'string' is the processing string.
        'length' is the required length."""
        original_string = unicode(string)
        if len(original_string) > length:
            result = [original_string[:length]]
            result.append('...')
            return ''.join(result)
        return original_string
