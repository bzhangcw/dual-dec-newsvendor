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
    --filter $PANDOC_FILTERS/pandoc-citeproc \
    --filter $PANDOC_FILTERS/pandoc-csv2table \
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
  --filter $PANDOC_FILTERS/pandoc-citeproc \
  --filter $PANDOC_FILTERS/pandoc-csv2table \
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
latexmk --xelatex -f -cd -quiet --shell-escape $TEX
# latexmk -c -cd $TEX
