# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: arto
# @file: /build_note.sh
# @created: Sunday, 1st November 2020
# @author: C. Zhang (chuwzhang@gmail.com)
# @modified: C. Zhang (chuwzhang@gmail.com>)
#    Sunday, 1st November 2020 8:02:36 pm
# @description:
# build note using new version of pandoc
# - pandoc 2.11.0.4
# compile pandoc md

# args
DOC=$1
AFFIX=$2

# env
PANDOC_FILTERS=$HOME/.cabal/bin/
PY_FIX=$PWD/fix_latex_equations.py

if [ -z $AFFIX ]; then
  MD=${DOC}.md
  HTML=${DOC}.html
  TEX=$DOC.tex
else
  MD=${DOC}.${AFFIX}.md
  HTML=${DOC}.${AFFIX}.html
  TEX=$DOC.${AFFIX}.tex
fi

cd $DOC/ &&
  $PANDOC_FILTERS/pandoc \
    --citeproc \
    --katex --toc \
    --csl=assets/ieee.csl \
    --css=assets/pandoc.css \
    -o $HTML \
    --toc \
    -s $MD

echo $PWD
# latex
# exit
$PANDOC_FILTERS/pandoc \
  --citeproc \
  --pdf-engine=xelatex \
  --csl=assets/institute-for-operations-research-and-the-management-sciences.csl \
  --template=assets/markdown.tex \
  -t latex \
  -N \
  --toc \
  -o $TEX \
  -s $MD

# %fix latex equation issues
python3 $PY_FIX $TEX

echo "...equation fix done..."

latexmk -C -cd $TEX
latexmk --xelatex -f -cd -quiet $TEX
# latexmk -c -cd $TEX
