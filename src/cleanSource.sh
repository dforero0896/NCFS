#!/bin/bash
rm *.txt
rm *.tex
rm *.aux
rm *.out
rm *.log
path=$(pwd)
#mv formula* ../FormulasPacientes
if ls $path"/historia"* 1> /dev/null 2>&1; then
  mv historia* ../HistoriasPacientes
fi
if ls $path"/formula"* 1> /dev/null 2>&1; then
  mv formula* ../FormulasPacientes
fi
