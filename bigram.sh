for key in ';' a b c d e f g h i j k l m n o p q r s t u v w x y z; do
  echo $key $(grep -o "${key}[a-z;]" code.txt | cut -c2 | sort | uniq -c | sort -nr)
done
