#!/bin/bash
#carddir=../vbfcards/PostPASCards/
#carddir=../parkedcards/cards031114/125
carddir=../exocombcards/125
mass=125
#card=vbfhinv_${mass}_8TeV.txt
card=/vols/cms04/pjd12/invcmssws/CMSSW_7_1_5/src/HiggsAnalysis/CombinedLimit/exocombcards/125/hinvcombinedcard.txt
#vbfhinv_125alljets25metsig4cjvmjj1000.txt

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
#numofnuis=`grep "number of nuisance parameters" $card | awk '{print $2}'`
#newnumofnuis=0
#cat $card | sed s:"kmax $numofnuis ":"kmax $newnumofnuis ": >nonuiscard.txt
cat $card >nonuiscard.txt
#echo "kmax *" >nonuiscard.txt

for sources in `grep -A 10000 "$firsterr" $card | awk '{print $1}'`
do
  echo $sources
    cat nonuiscard.txt > tmpcard1.txt
    cat tmpcard1.txt | sed s:$sources:'#'$sources: > nonuiscard.txt
    rm tmpcard1.txt
done

#RUN WITH NO NUISANCES
echo "   "Getting expected limit with no nuisances
combine -M Asymptotic -m $mass nonuiscard.txt &> tmpcombresult.txt
nonuismedexp=`grep "Expected 50.0%" tmpcombresult.txt | awk '{print $5}'`
rm tmpcombresult.txt

allnuislimit=`echo "100*$allnuismedexp"|bc -l`
nonuislimit=`echo "100*$nonuismedexp"|bc -l`

printf "Median expected limit with: & All Nuisances: %.1f\\%% & No Nuisances: %.1f\\%% \\\\\\\\ \n" "$allnuislimit" "$nonuislimit"

printf "Nuisance      &                Removal effect &  Addition effect \\\\\\\\ \n"
#LOOP OVER NUISANCES
for sources in `grep -A 10000 "$firsterr" $card | awk '{print $1}'`
do
    if [[ $sources == *"bin"* ]]
    then
	continue
    fi
    sourceout=`echo ${sources}|sed s:_:'\\\\'_:g`":"
    printf "%-30s &" "$sourceout"
    #GET CARD WITHOUT NUISANCE
    #numofnuis=`grep "number of nuisance parameters" $card | awk '{print $2}'`
    #newnumofnuis=$[$numofnuis-1]
    #cat $card | sed s:"kmax $numofnuis ":"kmax $newnumofnuis ": >tmpcard1.txt
    cat $card >tmpcard1.txt
    cat tmpcard1.txt | sed s:$sources:'#'$sources: > tmpcard.txt

    #RUN ON CARD WITHOUT NUISANCE
    combine -M Asymptotic -m $mass tmpcard.txt &> tmpcombresult.txt #!!
    nuissubtmedexp=`grep "Expected 50.0%" tmpcombresult.txt | awk '{print $5}'`
    deltasubt=`echo "$nuissubtmedexp-$allnuismedexp"|bc -l`
    percdiffsubt=`echo "100*$deltasubt/$allnuismedexp"|bc -l`
    rm tmpcard.txt tmpcard1.txt tmpcombresult.txt

    #GET CARD WITH ONLY THIS NUISANCE
#!!    cat nonuiscard.txt | sed s:"kmax 0 ":"kmax 1 ": >tmpcard1.txt
#!!    cat tmpcard1.txt | sed s:'#'$sources:$sources: > tmpcard.txt

    #RUN ON CARD WITH ONLY THIS NUISANCE
#!!    combine -M Asymptotic -m $mass tmpcard.txt | tee tmpcombresult.txt
#!!    nuisonlymedexp=`grep "Expected 50.0%" tmpcombresult.txt | awk '{print $5}'` 
#!!    echo $nuisonlymedexp #!!
#!!    deltaonly=`echo "$nuisonlymedexp-$nonuismedexp"|bc -l`
#!!    echo $deltaonly #!!
#!!    percdiffonly=`echo "100*$deltaonly/$nonuismedexp"|bc -l`
#!!    echo $percdiffonly #!!
#!!    rm tmpcard.txt tmpcard1.txt tmpcombresult.txt

    #echo Result with nuisance subtracted: $nuissubtmedexp, result with only this Nuisance: $nuisonlymedexp
    
    outpercdiffsubt=`printf "%.1f%%" "$percdiffsubt"`
    #printf "%-29s %.1f%% \n" "$outpercdiffsubt" "$percdiffonly"
    printf "%5.1f\\%%                &        N/A\\%% \\\\\\\\ \n" "$percdiffsubt" #!!"$percdiffonly"
done

rm nonuiscard.txt

cd $thisdir