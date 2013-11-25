#!/bin/bash
carddir=../vbfcards/PostPASCards/
mass=125
card=vbfhinv_${mass}_8TeV.txt

thisdir=`pwd`
cd $carddir/

echo Uncertainty effect estimator script

#GET FIRST ERROR IN CARD
grep -A 1 -e "-------" $card >tmp.txt
firsterr=`tail -1 tmp.txt | awk '{print $1}'`
rm tmp.txt

#RUN WITH ALL NUISANCES
echo "   "Getting expected limit with all nuisances
combine -M Asymptotic -m $mass $card &> tmpcombresult.txt
allnuismedexp=`grep "Expected 50.0%" tmpcombresult.txt | awk '{print $5}'`
rm tmpcombresult.txt

#GET CARD WITH NO NUISANCES
numofnuis=`grep "number of nuisance parameters" $card | awk '{print $2}'`
newnumofnuis=0
cat $card | sed s:"kmax $numofnuis ":"kmax $newnumofnuis ": >nonuiscard.txt

for sources in `grep -A 10000 "$firsterr" $card | awk '{print $1}'`
do
    cat nonuiscard.txt > tmpcard1.txt
    cat tmpcard1.txt | sed s:$sources" ":'#'$sources" ": > nonuiscard.txt
    rm tmpcard1.txt
done

#RUN WITH NO NUISANCES
echo "   "Getting expected limit with no nuisances
combine -M Asymptotic -m $mass nonuiscard.txt &> tmpcombresult.txt
nonuismedexp=`grep "Expected 50.0%" tmpcombresult.txt | awk '{print $5}'`
rm tmpcombresult.txt

allnuislimit=`echo "100*$allnuismedexp"|bc -l`
nonuislimit=`echo "100*$nonuismedexp"|bc -l`

echo Median expected limit with:
printf "   All Nuisances: %.1f%%, No Nuisances: %.1f%%\n" "$allnuislimit" "$nonuislimit"

printf "Nuisance                      Effect of removing nuisance   Effect of adding nuisance to empty card \n"
#LOOP OVER NUISANCES
for sources in `grep -A 10000 "$firsterr" $card | awk '{print $1}'`
do
    sourceout=${sources}":"
    printf "%-30s" "$sourceout"
    #GET CARD WITHOUT NUISANCE
    numofnuis=`grep "number of nuisance parameters" $card | awk '{print $2}'`
    newnumofnuis=$[$numofnuis-1]
    cat $card | sed s:"kmax $numofnuis ":"kmax $newnumofnuis ": >tmpcard1.txt
    cat tmpcard1.txt | sed s:$sources" ":'#'$sources" ": > tmpcard.txt

    #RUN ON CARD WITHOUT NUISANCE
    combine -M Asymptotic -m $mass tmpcard.txt &> tmpcombresult.txt
    nuissubtmedexp=`grep "Expected 50.0%" tmpcombresult.txt | awk '{print $5}'`
    deltasubt=`echo "$nuissubtmedexp-$allnuismedexp"|bc -l`
    percdiffsubt=`echo "100*$deltasubt/$allnuismedexp"|bc -l`
    rm tmpcard.txt tmpcard1.txt tmpcombresult.txt

    #GET CARD WITH ONLY THIS NUISANCE
    cat nonuiscard.txt | sed s:"kmax 0 ":"kmax 1 ": >tmpcard1.txt
    cat tmpcard1.txt | sed s:'#'$sources" ":$sources" ": > tmpcard.txt

    #RUN ON CARD WITH ONLY THIS NUISANCE
    combine -M Asymptotic -m $mass tmpcard.txt &> tmpcombresult.txt
    nuisonlymedexp=`grep "Expected 50.0%" tmpcombresult.txt | awk '{print $5}'`
    deltaonly=`echo "$nuisonlymedexp-$nonuismedexp"|bc -l`
    percdiffonly=`echo "100*$deltaonly/$nonuismedexp"|bc -l`
    rm tmpcard.txt tmpcard1.txt tmpcombresult.txt

    #echo Result with nuisance subtracted: $nuissubtmedexp, result with only this Nuisance: $nuisonlymedexp
    
    outpercdiffsubt=`printf "%.1f%%" "$percdiffsubt"`
    #printf "%-29s %.1f%% \n" "$outpercdiffsubt" "$percdiffonly"
    printf "%5.1f%%                        %5.1f%% \n" "$percdiffsubt" "$percdiffonly"
done

rm nonuiscard.txt

cd $thisdir