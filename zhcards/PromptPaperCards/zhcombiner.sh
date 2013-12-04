#!/bin/bash
for dir in 105 115 125 135 145
  do cd $dir
  echo $dir:
  combineCards.py -S zeehinv*.txt zmmhinv*.txt zhinv_Zbb*.txt >zhcombinedcard.txt
  combine -M Asymptotic -m $dir zhcombinedcard.txt | tee combineoutput${dir}.log
  cd ..
done
hadd -f zhcombineresults.root */higgsCombineTest.Asymptotic.mH*.root