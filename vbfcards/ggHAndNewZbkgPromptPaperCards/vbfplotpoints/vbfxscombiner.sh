#!/bin/bash
for dir in 110 125 150 200 300 400
  do cd $dir
  echo $dir:
  sed 's:kmax 19:kmax 18:' vbfhinv*.txt > xscard1.tmp
  sed 's:QCDscale_qqH:#QCDscale_qqH:' xscard1.tmp > xscard.tmp
  #combineCards.py -S vbfhinv*.txt zeehinv*.txt zmmhinv*.txt zhinv_Zbb*.txt >hinvcombinedcard.txt
  combine -M Asymptotic -m $dir xscard.tmp | tee xscombineoutput${dir}.log
  rm xscard.tmp xscard1.tmp
  cd ..
done
hadd -f vbfxscombineresults.root */higgsCombineTest.Asymptotic.mH*.root