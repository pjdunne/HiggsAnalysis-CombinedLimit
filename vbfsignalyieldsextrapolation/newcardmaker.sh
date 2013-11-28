#!/bin/bash
echo Datacard Interpolator for VBF Higgs to Invisible Analysis
CARDDIR="../vbfcards/PromptPaperCards/cardsfromchayanit/"
TARGETDIR="../vbfcards/PromptPaperCards/searches/"
XSDATFILE="../data/lhc-hxswg/sm/xs/8TeV/8TeV-vbfH.txt"
mkdir sourceuncs

cat $XSDATFILE | awk '{print $1, $2}' >xsinfo.txt

#GET INFO AT MASSES WE HAVE CARDS FOR
echo Processing input cards:
for card in ${CARDDIR}vbfhinv_*.txt
do
    echo "   "$card
    #GET MASS FROM CARD NAME
    mass=`echo $card | sed "s:${CARDDIR}vbfhinv_::" | sed "s/_8TeV.txt/.0/"`
    #GET XS INFO FROM LHC-HXSWG FILE
    root -l -b -q xs.cpp"("'"'xsinfo.txt'"',$mass")" > xstmp.txt
    xs=`cat xstmp.txt | grep "newxs" | awk '{print $2}'`
    rm xstmp.txt

    #GET SIGNAL YIELD INFO FROM CARDS
    yield=`grep "rate" $card | awk '{print $2}'`
    echo $mass $xs $yield >>inputinfo.txt

    #GET FIRST ERROR IN CARDS
    grep -A 1 -e "----------" $card > linetmp.txt
    firsterr=`tail -1 linetmp.txt | awk '{print $1}'`
    rm linetmp.txt
    
    #GET ERROR INFO FROM CARDS
    for sources in `grep -A 10000 "$firsterr" $card | awk '{print $1}'`
    do
	#CHECK SOURCE TYPE - CURRENTLY lnN and gmN DEALT WITH
	if [ `grep "$sources" $card | awk '{print $2}'` = "lnN" ]
	then
	    rawerror=`grep "$sources" $card | awk '{print $3}'`
	    
	elif [ `grep "$sources" $card | awk '{print $2}'` = "gmN" ]
	then
	    rawerror=`grep "$sources" $card | awk '{print $4}'`
	else
	    echo ERROR: UNRECOGNISED ERROR TYPE
	    exit 1
	fi

	if [ $rawerror = "-" ]
	then
	#ERROR DOESN'T AFFECT SIGNAL
	    echo $mass noeff >> sourceuncs/$sources.txt
	else
	    #CHECK FOR ASYMMETRIC ERROR ON SIGNAL
	    echo $rawerror | grep "/" > /dev/null
	    if [ $? = 0 ]
	    then
		downerror=`echo $rawerror | sed "s/\// /" | awk '{print $1}'`
		uperror=`echo $rawerror | sed "s/\// /" | awk '{print $2}'`
		echo $mass asym $downerror $uperror >> sourceuncs/$sources.txt
	    else
	    #ERROR IS SYMMETRIC FOR SIGNAL
		echo $mass sym $rawerror >> sourceuncs/$sources.txt
	    fi
	fi

    done
done


#GET INFO AT MASSES WE WANT CARDS FOR

rm -r $TARGETDIR
mkdir $TARGETDIR

echo Making new cards for:
newmasses=`cat masses.txt`
for newmass in $newmasses
do
  mkdir $TARGETDIR/$newmass
  echo "   mH =" $newmass GeV
  #GET NEW XS 
  root -l -b -q xs.cpp"("'"'xsinfo.txt'"',$newmass")" >xstmp.txt
  xs=`cat xstmp.txt | grep "newxs" |awk '{print $2}'`
  echo $newmass $xs > outputxsinfo.txt
  rm xstmp.txt
  
#MAKE NEW CARDS
  #FIRST 12 LINES ARE UNCHANGED
  grep -m 12 "" ${CARDDIR}vbfhinv_125_8TeV.txt >$TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.txt 
  sed -i "s:# Invisible Higgs analysis for mH=125 GeV:# Invisible Higgs analysis for mH=$newmass GeV:" $TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.txt
  
  #PUT NEW RATE IN
  root -l -q newyield.cpp >yieldtmp.txt
  rate=`cat yieldtmp.txt | grep "rate" | awk '{print $2}'`
  rm yieldtmp.txt
  oldrate=`grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | awk '{print $2}'`                                                                                
  grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | sed "s:$oldrate:$rate:" >>$TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.txt
  
  #LINE 14 UNCHANGED
  echo ------------ >>${TARGETDIR}/$newmass/vbfhinv_${newmass}_8TeV.txt 
  
  #PUT NEW ERRORS IN
  for sources in `grep -A 10000 "$firsterr" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $1}'`
    do
    if [ `grep -m 1 "" sourceuncs/$sources.txt | awk '{print $2}'` = "noeff" ]
        then
        #ERROR DOESN'T AFFECT SIGNAL                                                                                                                   
	type=noeff
    elif [ `grep -m 1 "" sourceuncs/$sources.txt | awk '{print $2}'` = "asym" ]
        then
            #ERROR IS ASYMMETRIC FOR SIGNAL                                                                                                            
	type=asym
    elif [ `grep -m 1 "" sourceuncs/$sources.txt | awk '{print $2}'` = "sym" ]
	then
            #ERROR IS SYMMETRIC FOR SIGNAL                                                                                                              
	type=sym
    fi
    
    fileforrootmacro=sourceuncs/$sources.txt
    root -l -b -q newunc.cpp"("'"'$fileforrootmacro'"','"'$type'"',$newmass")" > unctmp.txt
    err=`cat unctmp.txt | grep "newerror" |awk '{print $2}'` #SET ERR EQUAL TO APPROPRIATE BIT OF CPP OUTPUT
    rm unctmp.txt
    
    if [ `grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $2}'` = "lnN" ]
        then
	olderr=`grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $3}'`
	
        elif [ `grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $2}'` = "gmN" ]
        then
	olderr=`grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $4}'`
    else
	echo ERROR: UNRECOGNISED ERROR TYPE SHOULDN"'"T HAVE GOT THIS FAR
	exit 1
        fi
    
    grep "$sources" ${CARDDIR}vbfhinv_125_8TeV.txt | sed "s:$olderr:$err:" >>${TARGETDIR}/$newmass/vbfhinv_${newmass}_8TeV.txt
  done
  
  
  rm outputxsinfo.txt
done
rm xsinfo.txt
rm inputinfo.txt
rm -r sourceuncs
echo Interpolated datacards successfully created at: $TARGETDIR