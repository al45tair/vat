# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import unicodedata
import fuzzy
import Levenshtein

_mappings = {
    'de': {
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue', 'ä': 'ae',
        'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 'ẞ': 'SS' },
    'latin': {
        'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 
        'Ä': 'A', 'Å': 'A','Ă': 'A', 'Æ': 'AE',
        'Ç': 'C', 'È': 'E', 'É': 'E', 'Ê': 'E',
        'Ë': 'E', 'Ì': 'I', 'Í': 'I', 'Î': 'I',
        'Ï': 'I', 'Ð': 'D', 'Ñ': 'N', 'Ò': 'O',
        'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
        'Ő': 'O', 'Ø': 'O','Ș': 'S','Ț': 'T',
        'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
        'Ű': 'U', 'Ý': 'Y', 'Þ': 'TH', 'ß': 'ss',
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a',
        'ä': 'a', 'å': 'a', 'ă': 'a', 'æ': 'ae',
        'ç': 'c', 'è': 'e', 'é': 'e', 'ê': 'e',
        'ë': 'e', 'ì': 'i', 'í': 'i', 'î': 'i',
        'ï': 'i', 'ð': 'd', 'ñ': 'n', 'ò': 'o',
        'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 
        'ő': 'o', 'ø': 'o', 'ș': 's', 'ț': 't',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ű': 'u', 'ý': 'y', 'þ': 'th', 'ÿ': 'y' },
    'latin_symbols': {
        '©': '(c)', '®': '(r)', '™': 'TM' },
    'el': {
        'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e',
        'ζ': 'z', 'η': 'h', 'θ': '8', 'ι': 'i', 'κ': 'k',
        'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': '3', 'ο': 'o', 
        'π': 'p', 'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'y',
        'φ': 'f', 'χ': 'x', 'ψ': 'ps', 'ω': 'w', 'ά': 'a',
        'έ': 'e', 'ί': 'i', 'ό': 'o', 'ύ': 'y', 'ή': 'h',
        'ώ': 'w', 'ς': 's', 'ϊ': 'i', 'ΰ': 'y', 'ϋ': 'y',
        'ΐ': 'i', 'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D',
        'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Θ': '8', 'Ι': 'I',
        'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': '3',
        'Ο': 'O', 'Π': 'P', 'Ρ': 'R', 'Σ': 'S', 'Τ': 'T',
        'Υ': 'Y', 'Φ': 'F', 'Χ': 'X', 'Ψ': 'PS',
        'Ω': 'W', 'Ά': 'A', 'Έ': 'E', 'Ί': 'I', 'Ό': 'O',
        'Ύ': 'Y', 'Ή': 'H', 'Ώ': 'W', 'Ϊ': 'I', 'Ϋ': 'Y' },
    'tr': {
        'ş': 's', 'Ş': 'S', 'ı': 'i', 'İ': 'I', 'ç': 'c',
        'Ç': 'C', 'ü': 'u', 'Ü': 'U', 'ö': 'o', 'Ö': 'O',
        'ğ': 'g', 'Ğ': 'G' },
    'ru': {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 
        'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's',
        'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
        'ч': 'ch', 'ш': 'sh', 'щ': 'sh', 'ъ': '', 
        'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 
        'И': 'I', 'Й': 'J', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S',
        'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C',
        'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sh', 'Ъ': '', 
        'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya' },
    'uk': {
        'Є': 'Ye', 'І': 'I', 'Ї': 'Yi', 'Ґ': 'G',
        'є': 'ye', 'і': 'i', 'ї': 'yi', 'ґ': 'g' },
    'cs': {
        'č': 'c', 'ď': 'd', 'ě': 'e', 'ň': 'n', 'ř': 'r',
        'š': 's', 'ť': 't', 'ů': 'u', 'ž': 'z', 'Č': 'C',
        'Ď': 'D', 'Ě': 'E', 'Ň': 'N', 'Ř': 'R', 'Š': 'S',
        'Ť': 'T', 'Ů': 'U', 'Ž': 'Z' },
    'pl': {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z', 'Ą': 'A',
        'Ć': 'C', 'Ę': 'e', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O',
        'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z' },
    'ro': {
        'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't' },
    'lv': {
        'ā': 'a', 'č': 'c', 'ē': 'e', 'ģ': 'g', 'ī': 'i',
        'ķ': 'k', 'ļ': 'l', 'ņ': 'n', 'š': 's', 'ū': 'u', 
        'ž': 'z', 'Ā': 'A', 'Č': 'C', 'Ē': 'E', 'Ģ': 'G',
        'Ī': 'i', 'Ķ': 'k', 'Ļ': 'L', 'Ņ': 'N', 'Š': 'S',
        'Ū': 'u', 'Ž': 'Z' },
    'lt': {
        'ą': 'a', 'č': 'c', 'ę': 'e', 'ė': 'e', 'į': 'i',
        'š': 's', 'ų': 'u', 'ū': 'u', 'ž': 'z', 'Ą': 'A',
        'Č': 'C', 'Ę': 'E', 'Ė': 'E', 'Į': 'I', 'Š': 'S',
        'Ų': 'U', 'Ū': 'U', 'Ž': 'Z' }
    }

_charmap = {}
_char_re = None
_punct_re = re.compile(r'[-.\']')
_invalid_re = re.compile(r'[^A-Za-z0-9]+')
_token_re = re.compile(r'\s+', re.UNICODE)
_word_re = re.compile(r'^[A-Za-z]+$')

_metaphone = fuzzy.DMetaphone()

def _build_charmap():
    """Construct the character map we use for transliteration"""
    global _charmap
    global _char_re
    
    chars = []
    for mapping in _mappings.itervalues():
        for k, v in mapping.iteritems():
            _charmap[k] = v
            chars.append(k)
    _char_re = re.compile('[%s]' % ''.join(chars), re.UNICODE)

def _transliterate(s):
    if _char_re is None:
        _build_charmap()

    def sub_fn(ch):
        return _charmap[ch.group(0)]
        
    return _char_re.sub(sub_fn, s)

def _strip_punct(s):
    return _invalid_re.sub(' ', _punct_re.sub('', s)).strip()

def _tokenize(s):
    tokens = _token_re.split(s)
    result = []
    for tok in tokens:
        if _word_re.match(tok):
            result.append(_metaphone(tok))
        else:
            result.append(tok)
    return result

_infinity = float('inf')

def _word_difference(s, t):
    # s and t are allowed to be lists or tuples
    if isinstance(s, list) or isinstance(s, tuple):
        min_dist = _infinity
        for w in s:
            if w is None:
                break
            min_dist = min(min_dist, _word_difference(w, t))
        return min_dist

    if isinstance(t, list) or isinstance(t, tuple):
        min_dist = _infinity
        for w in t:
            if w is None:
                break
            min_dist = min(min_dist, _word_difference(s, w))
        return min_dist

    s = unicode(s)
    t = unicode(t)
    max_ed = max(len(s), len(t))
    return float(Levenshtein.distance(s, t)) / max_ed

def _edit_distance(s, t):
    m = len(s)
    n = len(t)

    d_prev = range(0, m + 1)
    d_curr = [0]*(m + 1)

    for j in range(1, n + 1):
        d_curr[0] = j
        for i in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                d_curr[i] = d_prev[i - 1]
            elif i < m and j < n \
                and s[i - 1] == t[j] \
                and s[i] == t[j - 1]:
                d_curr[i] = d_prev[i - 1]
            elif i > 1 and j > 1 \
              and s[i - 2] == t[j - 1] \
              and s[i - 1] == t[j - 2]:
              d_curr[i] = d_prev[i - 1]
            else:
                deleted = d_curr[i - 1] + 1
                inserted = d_prev[i] + 1
                substituted = d_prev[i - 1] + _word_difference(s[i - 1], t[j - 1])

                d_curr[i] = min(deleted, inserted, substituted)
        d_prev = d_curr
        d_curr = [0]*(m + 1)

    return d_prev[m]

def compare(a, b):
    """Compare two addresses, returning a similarity value between 0 and 1."""
    s = _tokenize(_strip_punct(_transliterate(a)))
    t = _tokenize(_strip_punct(_transliterate(b)))

    max_ed = max(len(s), len(t))
    ed = _edit_distance(s, t)

    return 1.0 - (float(ed) / max_ed) ** 2
