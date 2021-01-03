# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: repair
# @file: /test.sh
# @created: Sunday, 29th November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 29th November 2020 9:41:53 pm
# @description:


python -u main.py 5 10 10 &>101010.log
python -u main.py 5 10 15 &>101015.log
python -u main.py 5 10 20 &>101020.log
python -u main.py 5 10 25 &>101025.log
python -u main.py 5 15 10 &>101510.log
python -u main.py 5 15 15 &>101515.log
python -u main.py 5 15 20 &>101520.log
python -u main.py 5 15 25 &>101525.log
python -u main.py 5 20 20 &>102020.log
python -u main.py 5 20 25 &>102025.log
python -u main.py 5 25 20 &>102520.log
python -u main.py 5 25 25 &>102525.log
