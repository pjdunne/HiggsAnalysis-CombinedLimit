#!/bin/bash

outfolder=diffnuisanceoutputs
#mkdir $outfolder

for cards in higcombcard.txt 125/vbfhinv_125_8TeV.txt zllcard.txt zbbcard.txt 
do
    if [ $cards = "higcombcard.txt" ]
    then
	name=hig
    elif [ $cards = "125/vbfhinv_125_8TeV.txt" ]
    then
	name=vbf
    elif [ $cards = "zllcard.txt" ]
    then
	name=zll
    elif [ $cards = "zbbcard.txt" ]
    then
	name=zbb
    fi
    name=$outfolder/$name
    #combine -M MaxLikelihoodFit $cards
    # python ../test/diffNuisances.py mlfit.root --all -g ${name}.root > ${name}_diffnuisances.txt
    # combine -M MaxLikelihoodFit $cards -t -1 --expectSignal 0    
    # python ../test/diffNuisances.py mlfit.root --all -g ${name}_sig0.root > ${name}_diffnuisances_sig0.txt
    # combine -M MaxLikelihoodFit $cards -t -1 --expectSignal 1    
    # python ../test/diffNuisances.py mlfit.root --all -g ${name}_sig1.root > ${name}_diffnuisances_sig1.txt
    # combine -M MaxLikelihoodFit $cards -t -1 --expectSignal 0.5    
    # python ../test/diffNuisances.py mlfit.root --all -g ${name}_sig05.root > ${name}_diffnuisances_sig05.txt
    combine -M MaxLikelihoodFit $cards -t -1 --expectSignal 0.3    
    python ../test/diffNuisances.py mlfit.root --all -g ${name}_sig03.root > ${name}_diffnuisances_sig03.txt
done


for cards in 125/combined_hinv.txt 125/combined_boosted_hinv.txt 125/combined_resolved_hinv.txt 125/combined_monojet_hinv.txt 125/hinvcombinedcard.txt
do
    if [ $cards = "125/hinvcombinedcard.txt" ]
    then
	name=all
    elif [ $cards = "125/combined_hinv.txt" ]
    then
	name=exo
    elif [ $cards = "125/combined_boosted_hinv.txt" ]
    then
	name=exoboosted
    elif [ $cards = "125/combined_resolved_hinv.txt" ]
    then
	name=exoresolved
    elif [ $cards = "125/combined_monojet_hinv.txt" ]
    then
	name=exomonojet
    fi
    name=$outfolder/$name
    # combine -M MaxLikelihoodFit $cards --toysFrequentist
    # python ../test/diffNuisances.py mlfit.root --all -g ${name}.root > ${name}_diffnuisances.txt
    # combine -M MaxLikelihoodFit $cards -t -1 --toysFrequentist --expectSignal 0    
    # python ../test/diffNuisances.py mlfit.root --all -g ${name}_sig0.root > ${name}_diffnuisances_sig0.txt
    # combine -M MaxLikelihoodFit $cards -t -1 --toysFrequentist --expectSignal 1    
    # python ../test/diffNuisances.py mlfit.root --all -g ${name}_sig1.root > ${name}_diffnuisances_sig1.txt
    # combine -M MaxLikelihoodFit $cards -t -1 --toysFrequentist --expectSignal 0.5    
    # python ../test/diffNuisances.py mlfit.root --all -g ${name}_sig05.root > ${name}_diffnuisances_sig05.txt
    combine -M MaxLikelihoodFit $cards -t -1 --toysFrequentist --expectSignal 0.3    
    python ../test/diffNuisances.py mlfit.root --all -g ${name}_sig03.root > ${name}_diffnuisances_sig03.txt
done