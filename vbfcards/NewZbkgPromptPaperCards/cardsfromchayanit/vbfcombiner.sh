#!/bin/bash
for dir in 115 125 135 145
  do cd $dir
  echo $dir:
  #combineCards.py -S vbfhinv*.txt zeehinv*.txt zmmhinv*.txt zhinv_Zbb*.txt >hinvcombinedcard.txt
  combine -M Asymptotic -m $dir vbfhinv*.txt | tee combineoutput${dir}.log
  cd ..
done
hadd -f vbfcombineresults.root */higgsCombineTest.Asymptotic.mH*.root