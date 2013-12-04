#!/bin/bash
for dir in 115  125  135  145  175  200  300
  do cd $dir
  echo $dir:
  combineCards.py -S zeehinv*.txt zmmhinv*.txt vbfhinv*.txt >zllvbfcombinedcard.txt
  combine -M Asymptotic -m $dir zllvbfcombinedcard.txt | tee combineoutput${dir}.log
  cd ..
done
hadd -f zllvbfcombineresults.root */higgsCombineTest.Asymptotic.mH*.root