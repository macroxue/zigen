code_book=${1:-code.txt}

len1=$(grep '^   ' $code_book | wc -l)
len2=$(grep '^  ' $code_book | wc -l)
len3=$(grep '^ ' $code_book | wc -l)
len4=$(grep '^' $code_book | wc -l)
dups=$(grep '[2-9]' $code_book | wc -l)
echo 一码:$len1 二码:$((len2-len1)) 三码:$((len3-len2)) 四码:$((len4-len3)) 重码: $dups

keys="; a b c d e f g h i j k l m n o p q r s t u v w x y z"
printf "二码细分: "
for key in $keys; do
  len2=$(grep "^  $key" $code_book | wc -l)
  printf "$key $len2 "
done
echo
printf "三码细分: "
for key in $keys; do
  len3=$(grep "^ $key" $code_book | wc -l)
  printf "$key $len3 "
done
echo
