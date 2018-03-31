#!/usr/bin/python -OOS
# coding=utf-8

import argparse
parser = argparse.ArgumentParser(
        description='Generate heat map for Chinese input method')
parser.add_argument('-c', '--code_file',
        help='file encoding Chinese characters',
        default='code.txt')
parser.add_argument('-t', '--text_file',
        help='use this text file to generate heat map',
        default='test.txt')
parser.add_argument('-b', '--show_bigram',
        help='show bigram table for the keys',
        action='store_true')
args = parser.parse_args()

with open(args.code_file) as f:
    lines = f.readlines()

code_book = {}
code_book['，'] = ','
code_book['。'] = '.'
for line in lines:
    line = line.strip()
    # Skip empty line or comment.
    if line == '' or line[0] == '#':
        continue
    # Skip a line that doesn't define a character.
    item = line.split()
    if len(item) < 2:
        continue
    code_book[item[1]] = item[0]

with open(args.text_file) as f:
    lines = f.readlines()

freq = {'.': 0, ',': 0, ';': 0, '/': 0}
bigram = {}
total_keys = 0
total_chars = 0
left_hand_keys = 'qwertasdfgzxcvb'
last_hand = 0  # 0=left, 1=right
last_key = ''
same_hand_count = 0
for line in lines:
    i = 0
    while i < len(line):
        if ord(line[i]) < 128:  # ASCII character
            if line[i] == ',' or line[i] == '.':
                total_keys += 1
                total_chars += 1
                freq[line[i]] += 1
            i += 1
            continue
        c = line[i:i+3]
        i += 3
        if not code_book.has_key(c):
            continue
        code = code_book[c]

        total_chars += 1
        for key in code:
            total_keys += 1
            if freq.has_key(key):
                freq[key] += 1
            else:
                freq[key] = 1
            combo = last_key, key
            if args.show_bigram:
                if bigram.has_key(combo):
                    bigram[combo] += 1
                else:
                    bigram[combo] = 1
            this_hand = 0 if key in left_hand_keys else 1
            if this_hand == last_hand:
                same_hand_count += 1
            last_hand = this_hand
            last_key = key

def show_freq(keys):
    for key in keys:
        print '%c%4.1f ' % (key, freq[key]*100.0/total_keys),

def sum_freq(keys):
    sum = 0
    for key in keys:
        sum += freq[key]
    return sum*100.0 / total_keys

print '字数: %d  按键: %d  每字按键: %.2f  同手连击: %.2f%%' % (
        total_chars, total_keys, float(total_keys)/total_chars,
        100.0*same_hand_count/total_keys)
print
show_freq('qwertyuiop')
print '   %4.1f=%4.1f+%4.1f' % (
        sum_freq('qwertyuiop'), sum_freq('qwert'), sum_freq('yuiop'))
show_freq('asdfghjkl;')
print '   %4.1f=%4.1f+%4.1f' % (
        sum_freq('asdfghjkl;'), sum_freq('asdfg'), sum_freq('hjkl;'))
show_freq('zxcvbnm,.')
print '          %4.1f=%4.1f+%4.1f' % (
        sum_freq('zxcvbnm,.'), sum_freq('zxcvb'), sum_freq('nm,.'))
print
print '%5.1f  %5.1f  %5.1f  %5.1f  %5.1f  %5.1f  %5.1f  %5.1f  %5.1f  %5.1f' % (
        sum_freq('qaz'),
        sum_freq('wsx'),
        sum_freq('edc'),
        sum_freq('rfvtgb'),
        sum_freq('qwertasdfgzxcvb'),
        sum_freq('yuiophjkl;nm,.'),
        sum_freq('yhnujm'),
        sum_freq('ik,'),
        sum_freq('ol.'),
        sum_freq('p;'))

if args.show_bigram:
    keys = 'qwertasdfgzxcvbyuiophjkl;nm'
    print
    print '  %00',
    for k2 in keys:
        print '%5s' % k2,
    print
    for k1 in keys:
        print '%5s' % k1,
        for k2 in keys:
            combo = k1, k2
            count = bigram[combo] if bigram.has_key(combo) else 0
            percent = count*10000.0 / total_keys
            print '%5.1f' % percent,
        print

