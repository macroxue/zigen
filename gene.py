#!/usr/bin/python -OOS
# coding=utf-8

from sys import exit
from sys import stderr

import argparse
parser = argparse.ArgumentParser(
        description='Generate code book for Chinese input method')
parser.add_argument('-a', '--alternative_map',
        help='alternatively map groups to keys based on shape resemblance',
        action='store_true')
parser.add_argument('-b', '--breakdown_file',
        help='input file breaking characters down to roots',
        default='breakdown.txt')
parser.add_argument('-g', '--group_file',
        help='input file grouping roots',
        default='group.txt')
parser.add_argument('-c', '--code_file',
        help='output codes to this file',
        default='code.txt')
parser.add_argument('-f', '--freq_file',
        help='output root frequencies to this file',
        default='freq.txt')
parser.add_argument('-m', '--max_code_length',
        help='maximum code length',
        type=int, default=4)
parser.add_argument('-p', '--pad_with_pin_yin',
        help='add Pin-Yin for code length below the maximum',
        type=int, default=2)
parser.add_argument('-s', '--simple_code_length',
        help='generate simple codes up to this length',
        type=int, default=3)
parser.add_argument('-o', '--optimize',
        help='optimize for root groups, '
        'taking "all" or a comma-separated list of roots')
parser.add_argument('-n', '--new_group_file',
        help='output optimized groups to this file',
        default='group')
args = parser.parse_args()

with open(args.breakdown_file) as f:
  lines = f.readlines()

for i in range(len(lines)):
    if lines[i].strip() == '#START':
        break
else:
    print 'The character table must start with a "#START" line'
    exit(1)

#an      B0B6 岸 山(厂干ZS)SX
#ai      DEDF 捱 扌[涯右]
#biao    ECAE 飚 风(火(火火)SX)ZX
#sui     CBE8 髓 骨(辶(左月SX)ZX)

def parse_breakdown(line, i):
    breakdown = []
    while i < len(line):
        if ord(line[i]) >= 240:  # 4-byte character
            breakdown += [line[i:i+4]]
            i += 4
        elif ord(line[i]) >= 224:  # 3-byte character
            breakdown += [line[i:i+3]]
            i += 3
        elif line[i] == '[': # non-character
            j = i + 1
            while line[j] != ']':
                j  += 1
                if j >= len(line):
                    return '', i, 'mismatched ['
            breakdown += [line[i:j+1]]
            i = j + 1
        elif line[i] == '(': # structure
            part, i, err = parse_breakdown(line, i+1)
            if err != '':
                return part, i, err
            assert line[i] == ')', 'mismatched ('
            i += 1
            breakdown += [part]
        elif line[i] == ')': # structure
            return breakdown, i, ''
        elif line[i] == '?': # unknown
            return '', i, 'unknown breakdown'
        elif line[i].isalpha() or line[i] in ['{', '}']:
            i += 1
        else:
            return '', i, 'invalid character %s' % line[i]
    return breakdown, i, ''

def reverse_order(breakdown, special_roots):
    if breakdown[0] in special_roots:
        breakdown = breakdown[1:] + breakdown[:1]
    return [reverse_order(part, special_roots) if isinstance(part, list)
            else part for part in breakdown]

def traverse(breakdown):
    flat = []
    for part in breakdown:
        flat += traverse(part) if isinstance(part, list) else [part]
    return flat

sp_map = {
        'iu': 'q',
        'en': 'w',
        'e': 'e',
        'zh': 'e',
        'ou': 'r',
        'ui': 't',
        'ue': 't',
        'ue:': 't',
        'uan': 'y',
        'u': 'u',
        'sh': 'u',
        'i': 'i',
        'ch': 'i',
        'o': 'o',
        'uo': 'o',
        'un': 'p',
        'a': 'a',
        'ao': 's',
        'ang': 'd',
        'eng': 'f',
        'ng': 'f',
        'ing': 'g',
        'er': 'g',
        'ong': 'h',
        'iong': 'h',
        'ai': 'j',
        'an': 'k',
        'ian': 'l',
        'uai': 'l',
        'iang': ';',
        'uang': ';',
        'ua': 'x',
        'ia': 'x',
        'ie': 'c',
        'u:': 'v',
        'in': 'b',
        'iao': 'n',
        'ei': 'm',
        '': '',
}

def convert_py_to_sp(py):
    if py[0] in 'a':
        return 'a' + sp_map[py]
    if py[0] in 'oe' or py == 'ng':
        return 'o' + sp_map[py]
    if py[0] in 'zcs' and py[1] == 'h':
        return sp_map[py[0:2]] + sp_map[py[2:]]
    return py[0:1] + sp_map[py[1:]]

lines = lines[i+1:]
dict = {}
pinyin = {}
incomplete = []
for line in lines:
    line = line.strip()
    # Skip empty line or comment.
    if line == '' or line[0] == '#':
        continue
    # Skip a line that doesn't define a character.
    item = line.split()
    if len(item) < 3:
        continue

    # Extra Pin-Yin if it's a character.
    p = item[0]
    c = item[2]
    if p[0].isalpha():
        p = p[:args.pad_with_pin_yin]
        if not pinyin.has_key(c):
            pinyin[c] = [p]
        elif not p in pinyin[c]:
            pinyin[c] += [p]

    # Handle a character whose breakdown is not defined. Can be a root.
    if len(item) < 4:
        if not dict.has_key(c):
            dict[c] = ''
        continue

    # Merge the rest of the items into one string that defines the breakdown.
    d = item[3]
    for i in range(4, len(item)):
        d += item[i]

    breakdown, i, err = parse_breakdown(d, 0)
    if err != '':
        stderr.write('%s at: %s\n' % (err, line))
        exit(1)
    if i != len(d):
        stderr.write('Incomplete parse at: %s\n' % line)
        exit(1)

    breakdown = reverse_order(breakdown, ['辶' , '廴'])
    breakdown = traverse(breakdown)

    # Mark a reference to the part if it's not yet defined.
    for part in breakdown:
        if not dict.has_key(part):
            dict[part] = ''

    # The character has been seen before.
    if dict.has_key(c) and dict[c] != '':
        if breakdown != dict[c]:
            print 'Different breakdown for %s: %s, %s.' % (c,
                    ''.join(dict[c]), ''.join(breakdown))
        continue

    dict[c] = breakdown


new_group = True
num_groups = 0
root_group = {}  # map from roots to their group indexes
group_rep = []   # roots representing each group
dup_roots = []   # roots defined multiple times

# Read groups from group file.
with open(args.group_file) as f:
    lines = f.readlines()

for line in lines:
    if line[0] == '#':
        continue
    roots = line.split()
    if roots == []:
        new_group = True
        continue

    if new_group:
        num_groups += 1
    for root in roots[1:]:
        # Skip frequency at the end if any.
        if root[0] in '1234567890':
            continue
        if root_group.has_key(root):
            dup_roots += [root]
            continue
        root_group[root] = num_groups - 1
        if new_group:
            group_rep += [root]
            new_group = False

# Fail when there are undefined roots.
undefined_roots = [c for c, roots in dict.items()
                   if roots == '' and not root_group.has_key(c)]
if undefined_roots != []:
    stderr.write('Undefined roots: ' + ' '.join(undefined_roots) + '\n')
    exit(1)

# Warn about duplicate roots.
if dup_roots != []:
    stderr.write('Duplicate roots: ' + ' '.join(dup_roots) + '\n')

# Recursively break a character down to roots
def break_character(c):
    if dict[c]=='':
        return [c]
    roots = []
    for part in dict[c]:
        if dict.has_key(part):
            roots += break_character(part)
    return roots

# Remove minor (single-stroke) roots since they carry less info.
minor_roots = ['一', '丨', '丿', '丶']
def remove_minor_roots(roots):
    new_roots = roots[:1]
    for root in roots[1:]:
        if root not in minor_roots:
            new_roots += [root]
    return new_roots

# Generate flat dictionary where characters are broken down to roots.
flat_dict = {}
root_freq = {}
for c in dict.keys():
    if c in incomplete or c[0] == '[':
        continue

    roots = break_character(c)
    if len(roots) > args.max_code_length:
        roots = remove_minor_roots(roots)
    if len(roots) > args.max_code_length:
        roots = roots[:args.max_code_length-1] + roots[-1:]

    flat_dict[c] = roots
    for root in roots:
        if root_freq.has_key(root):
            root_freq[root] += 1
        else:
            root_freq[root] = 1

# Output root frequencies to a file.
freq_list = [[root, freq] for root, freq in root_freq.items()]
freq_list.sort(key=lambda x: x[1], reverse=True)
with open(args.freq_file, 'w') as f:
    for root, freq in freq_list:
        f.write('%s\t%d\n' % (root, freq))

# Warn about unused roots.
unused_roots = [root for root in root_group if root not in root_freq.keys()]
if unused_roots != []:
    stderr.write('Unused roots: ' + ' '.join(unused_roots) + '\n')

# Read table of character frequencies.
with open('char_freq.txt') as f:
    lines = f.readlines()
char_freq = {}
for line in lines:
    item = line.split()
    char_freq[item[0]] = int(item[1])
for c in flat_dict:
    if not char_freq.has_key(c):
        char_freq[c] = 0

# Keys used for encoding roots.
#code_keys = 'abcdefghijklmnopqrstuvwxyz;1234567890'
code_keys = 'qwertyuiopasdfgzxcvhjkl;bnm1234567890'
if args.alternative_map:
    code_keys = 'eglrkaobqpzfthxsudyijvw;cnm1234567890'

# Generate the code book.
def generate_code_book():
    for c, roots in flat_dict.items():
        if not pinyin.has_key(c):
            continue
        code = ''
        for root in roots:
            code += code_keys[root_group[root]]
        plus = pinyin[c]
        for p in plus:
            code_plus = (code + p)[:args.max_code_length]
            if not code_book.has_key(code_plus):
                code_book[code_plus] = [c]
            elif not c in code_book[code_plus]:
                code_book[code_plus] += [c]

# Generate simple codes based on character frequencies.
def generate_simple_codes():
    for length in range(1, args.simple_code_length+1):
        simple_code_candidates = {}
        for code, characters in code_book.items():
            if len(code) <= length:
                continue
            simple_code = code[0:length]
            if length > 1 and code_book.has_key(simple_code):
                available = True
                for char in code_book[simple_code]:
                    if char not in char_simple_code:
                        available = False
                        break
                if not available:
                    continue
            if simple_code_candidates.has_key(simple_code):
                simple_code_candidates[simple_code] += characters
            else:
                simple_code_candidates[simple_code] = [] + characters
        for code, candidates in simple_code_candidates.items():
            candidates.sort(key=lambda c: char_freq[c], reverse=True)
            for c in candidates:
                if c in char_simple_code:
                    new = True
                    for simple_code in char_simple_code[c]:
                        if code.startswith(simple_code):
                            new = False
                            break
                    if new:
                        char_simple_code[c] += [code]
                        simple_code_book[code] = c
                        break
                else:
                    char_simple_code[c] = [code]
                    simple_code_book[code] = c
                    break

# Output code book to a file.
def output_code_book():
    with open(args.code_file, 'w') as f:
        for code in sorted(simple_code_book):
            f.write('%4s\t%s\t1\n' % (code, simple_code_book[code]))
        for code in sorted(code_book.keys()):
            characters = code_book[code]
            full_codes = []
            for c in characters:
                if c not in char_simple_code:
                    full_codes += [c]
            full_codes.sort(key=lambda c: char_freq[c], reverse=True)
            code_count = len(full_codes)
            for c in full_codes:
                f.write('%4s\t%s\t%d\n' % (code, c, code_count))

def count_dups():
    num_dups = 0
    for code in sorted(code_book.keys()):
        characters = code_book[code]
        full_codes = []
        for c in characters:
            if c not in char_simple_code:
                full_codes += [c]
        full_codes.sort(key=lambda c: char_freq[c], reverse=True)
        code_count = len(full_codes)

        # Don't count dups for code length 1 because many of them are
        # non-characters.
        if len(code) <= 1:
            continue
        if code_count >= 2:
            num_dups += code_count
    return num_dups

code_book = {}
generate_code_book()

simple_code_book = {}
char_simple_code = {}
generate_simple_codes()

output_code_book()
num_dups = count_dups()
print '编码键数: %d  重码字数: %d' % (num_groups, num_dups)

# See if optimization for root grouping is asked.
if args.optimize is None:
    exit(0)
elif args.optimize == 'all':
    roots_to_optimize = root_freq.keys()
else:
    roots_to_optimize = list(set(args.optimize.split(',')) - set(unused_roots))
    non_roots = list(set(roots_to_optimize) - set(root_group.keys()))
    if non_roots != []:
        stderr.write('Cannot optimize for non-root: %s\n' % ' '.join(non_roots))
        exit(1)

# Evaluation to figure out duplicate codes.
def evalulate_dups():
    global code_book
    code_book = {}
    generate_code_book()

    global simple_code_book
    global char_simple_code
    simple_code_book = {}
    char_simple_code = {}
    generate_simple_codes()

    return count_dups()

# Sort roots by frequency. Optimize for frequently used roots first.
roots_to_optimize.sort(key=lambda r: root_freq[r], reverse=True)
for root in roots_to_optimize:
    min_dups = num_dups
    min_group = root_group[root]
    for target_group in range(num_groups):
        root_group[root] = target_group
        new_dups = evalulate_dups()
        if len(roots_to_optimize) == 1:
            print code_keys[target_group], group_rep[target_group], new_dups
        if new_dups < min_dups:
            min_dups = new_dups
            min_group = target_group
    root_group[root] = min_group
    num_dups = min_dups
    print root, '->', code_keys[min_group], group_rep[min_group], min_dups

# Output optimized groups to a file.
with open(args.new_group_file, 'w') as f:
    for g in range(num_groups):
        roots = [root for root, freq in freq_list if root_group[root] == g]
        freqs = [freq for root, freq in freq_list if root_group[root] == g]
        f.write('%c %s %d\n\n' % (code_keys[g], ' '.join(roots), sum(freqs)))
