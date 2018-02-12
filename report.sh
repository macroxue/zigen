#!/bin/bash

file=code.txt

echo "指标1：有该字符参于的编码的重码个数"
echo "指标2：有该字符参于的编码个数"
echo "指标3：以该字符开始的编码的重码个数"
echo "指标4：以该字符开始的编码个数"
for c in a b c d e f g h i j k l m n o p q r s t u v w x y z ';'; do
  freq=$(grep $c $file | wc -l)
  dups=$(grep "^ *$c.*[2-9]" $file | wc -l)
  dup_freq=$(grep "$c.*[2-9]" $file | wc -l)
  section=$(grep "^ *$c" $file | wc -l)
  echo $c $dup_freq/$freq $dups/$section
done | sort -k 2 -nr

