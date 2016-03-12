#!/bin/bash
cl=0.95
for dir in 125
  do cd $dir
  echo $dir:
  echo "VBF only:"
  combineCards.py -S vbfhinv*.txt > vbfcombinedcard.txt
  combine -M Asymptotic --cl $cl -m $dir -n VBF vbfcombinedcard.txt

  # echo "ggH only:"
  # combineCards.py monojet_*.txt > gghcombinedcard.txt
  # combine -M Asymptotic --cl $cl -m $dir -n ggH gghcombinedcard.txt

  echo "VH only:"
#  combineCards.py -S monov_*.txt zh${dir}*.text > vhcombinedcard.txt
  combineCards.py -S zh${dir}*.text > vhcombinedcard.txt
  combine -M Asymptotic --cl $cl -m $dir -n VH vhcombinedcard.txt

  # echo "ZH+VBF only:"
  # combineCards.py -S vbfhinv*.txt zh${dir}*.text > vbfzhcombinedcard.txt
  # combine -M Asymptotic --cl $cl -m $dir -n vbfzh vbfzhcombinedcard.txt

  echo "Combined:"
  combineCards.py -S vbfhinv*.txt zh${dir}*.text >hinvcombinedcard.txt
  combine -M Asymptotic --cl $cl -m $dir -n Comb hinvcombinedcard.txt

  # echo "Combined:"
  # combineCards.py -S vbfhinv*.txt zh${dir}*.text monov_*.txt monojet_*.txt >hinvcombinedcard.txt
  # combine -M Asymptotic --cl $cl -m $dir -n Comb hinvcombinedcard.txt
  cd ..
done
hadd -f allcombineresults.root */higgsCombineTest.Asymptotic.mH*.root




#8 TeV lines
#  combineCards.py -S vbfhinv*.txt zeehinv*.txt zmmhinv*.txt combined_hinv.txt >hinvcombinedcardnozbb.txt
  #combine -M Asymptotic  -m $dir hinvcombinedcard.txt | tee combineoutput${dir}.log
#  combineCards.py -S vbfhinv*.txt zeehinv*.txt zmmhinv*.txt zhinv_Zbb*.txt combined_boosted_hinv.txt combined_monojet_hinv.txt >hinvcombinedcardnoresolved.txt
#  combine -M Asymptotic --cl $cl  -m $dir -n Comb hinvcombinedcardnoresolved.txt | tee combineoutput${dir}.log
#  combineCards.py -S zeehinv*.txt zmmhinv*.txt zhinv_Zbb*.txt combined_boosted_hinv.txt >vhcombinedcard.txt
#  combine -M Asymptotic --cl $cl -m $dir -n VH vhcombinedcard.txt | tee combineoutput${dir}.log
#  combine -M Asymptotic --cl $cl -m $dir -n VBF vbfhinv_125_8TeV.txt | tee combineoutput${dir}.log
#  combine -M Asymptotic --cl $cl -m $dir -n ggH combined_monojet_hinv.txt