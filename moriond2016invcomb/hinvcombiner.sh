#!/bin/bash
cl=0.95
for dir in 125
  do cd $dir
  echo $dir:
  #combineCards.py -S vbfhinv*.txt zeehinv*.txt zmmhinv*.txt zhinv_Zbb*.txt combined_hinv.txt >hinvcombinedcard.txt
#  combineCards.py -S vbfhinv*.txt zeehinv*.txt zmmhinv*.txt combined_hinv.txt >hinvcombinedcardnozbb.txt
  #combine -M Asymptotic  -m $dir hinvcombinedcard.txt | tee combineoutput${dir}.log
#  combineCards.py -S vbfhinv*.txt zeehinv*.txt zmmhinv*.txt zhinv_Zbb*.txt combined_boosted_hinv.txt combined_monojet_hinv.txt >hinvcombinedcardnoresolved.txt
#  combine -M Asymptotic --cl $cl  -m $dir -n Comb hinvcombinedcardnoresolved.txt | tee combineoutput${dir}.log
#  combineCards.py -S zeehinv*.txt zmmhinv*.txt zhinv_Zbb*.txt combined_boosted_hinv.txt >vhcombinedcard.txt
#  combine -M Asymptotic --cl $cl -m $dir -n VH vhcombinedcard.txt | tee combineoutput${dir}.log
#  combine -M Asymptotic --cl $cl -m $dir -n VBF vbfhinv_125_8TeV.txt | tee combineoutput${dir}.log
#  combine -M Asymptotic --cl $cl -m $dir -n ggH combined_monojet_hinv.txt

  combineCards.py vbfhinv*.txt #zllhinv*.txt >hinvcombinedcard.txt
#  combine -M Asymptotic --cl $cl -m $dir -n Comb hinvcombinedcard.txt
  cd ..
done
hadd -f allcombineresults.root */higgsCombineTest.Asymptotic.mH*.root