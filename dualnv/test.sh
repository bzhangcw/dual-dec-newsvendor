# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: repair
# @file: /test.sh
# @created: Sunday, 29th November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 29th November 2020 9:41:53 pm
# @description:

NUM_INSTANCES=$1

for i in {12..24..1}; do
  for t in {15..30..1}; do
    echo $i $t
    python -u main.py $NUM_INSTANCES $i $t &> $NUM_INSTANCES$i$t.log
  done
done
