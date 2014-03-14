#!/bin/bash
for dir in 105 115 125 135 145
  do cd $dir
  echo $dir:
  combineCards.py -S zeehinv*.txt zmmhinv*.txt zhinv_Zbb*.txt >zhcombinedcard.txt
  sed 's:QCDscale_VH:#QCDscale_VH:' zhcombinedcard.txt > zhxscard1.tmp
  sed 's:kmax:kmax * #kmax:' zhxscard1.tmp > zhxscard.tmp
  combine -M Asymptotic -m $dir zhxscard.tmp | tee xscombineoutput${dir}.log
  rm zhxscard.tmp zhxscard1.tmp
  cd ..
done
hadd -f zhxscombineresults.root */higgsCombineTest.Asymptotic.mH*.root