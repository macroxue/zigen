keys="; a b c d e f g h i j k l m n o p q r s t u v w x y z"
for key in $keys; do
  echo $key "->" $(grep -o "${key}[a-z;]" code.txt | cut -c2 | sort | uniq -c | sort -nr)
done
for key in $keys; do
  echo $key "<-" $(grep -o "[a-z;]${key}" code.txt | cut -c1 | sort | uniq -c | sort -nr)
done
