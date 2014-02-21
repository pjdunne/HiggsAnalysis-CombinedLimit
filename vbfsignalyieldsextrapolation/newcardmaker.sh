#!/bin/bash
echo Datacard Interpolator for VBF Higgs to Invisible Analysis
CARDDIR="../vbfcards/PromptPaperCards/cardsfromchayanit/"
TARGETDIR=../extracard #"../vbfcards/PromptPaperCards/searches/"
VBFXSDATFILE="../data/lhc-hxswg/sm/xs/8TeV/8TeV-vbfH.txt"
GGHXSDATFILE="../data/lhc-hxswg/sm/xs/8TeV/8TeV-ggH.txt"
DOGGH=1
mkdir sourceuncs

cat $VBFXSDATFILE | awk '{print $1, $2}' >vbfxsinfo.txt
if [ "$DOGGH" = "1" ]
    then
    cat $GGHXSDATFILE | awk '{print $1, $2}' >gghxsinfo.txt
fi

#GET INFO AT MASSES WE HAVE CARDS FOR
echo Processing input cards:
for card in ${CARDDIR}vbfhinv_*.txt
do
    echo "   "$card
    #GET MASS FROM CARD NAME
    mass=`echo $card | sed "s:${CARDDIR}vbfhinv_::" | sed "s/_8TeV.txt/.0/"`
    #GET XS INFO FROM LHC-HXSWG FILE
    root -l -b -q xs.cpp"("'"'vbfxsinfo.txt'"',$mass")" > vbfxstmp.txt
    vbfxs=`cat vbfxstmp.txt | grep "newxs" | awk '{print $2}'`
    rm vbfxstmp.txt
    
    if [ "$DOGGH" = "1" ]
	then
	root -l -b -q xs.cpp"("'"'gghxsinfo.txt'"',$mass")" > gghxstmp.txt
	gghxs=`cat gghxstmp.txt | grep "newxs" | awk '{print $2}'`
	rm gghxstmp.txt
    fi

    #GET SIGNAL YIELD INFO FROM CARDS
    if [ "$DOGGH" = "1" ]
	then
	vbfyield=`grep "rate" $card | awk '{print $3}'`
	gghyield=`grep "rate" $card | awk '{print $2}'`
	echo $mass $gghxs $gghyield >>gghinputinfo.txt
    else
	vbfyield=`grep "rate" $card | awk '{print $2}'`
    
    fi
    echo $mass $vbfxs $vbfyield >>vbfinputinfo.txt

        

    #!!DONE UP TO HERE


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

#!!ABOVE NOT DONE, BELOW OK TO NEXT MARK

#GET INFO AT MASSES WE WANT CARDS FOR

rm -r $TARGETDIR
mkdir $TARGETDIR

echo Making new cards for:
newmasses="110 125 150 200 300 400" #`cat masses.txt`
for newmass in $newmasses
do
  mkdir $TARGETDIR/$newmass
  echo "   mH =" $newmass GeV
  #GET NEW XS 
  root -l -b -q xs.cpp"("'"'vbfxsinfo.txt'"',$newmass")" >vbfxstmp.txt
  vbfxs=`cat vbfxstmp.txt | grep "newxs" |awk '{print $2}'`
  echo $newmass $vbfxs > outputvbfxsinfo.txt
  rm vbfxstmp.txt
  if [ "$DOGGH" = "1" ]
      then
      root -l -b -q xs.cpp"("'"'gghxsinfo.txt'"',$newmass")" >gghxstmp.txt
      gghxs=`cat gghxstmp.txt | grep "newxs" |awk '{print $2}'`
      echo $newmass $gghxs > outputvbfxsinfo.txt
      rm gghxstmp.txt
  fi
  
  
#MAKE NEW CARDS
  #FIRST 12 LINES ARE UNCHANGED
  grep -m 12 "" ${CARDDIR}vbfhinv_125_8TeV.txt >$TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.txt 
  sed -i "s:# Invisible Higgs analysis for mH=125 GeV:# Invisible Higgs analysis for mH=$newmass GeV:" $TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.txt
  
  #PUT NEW RATE IN
  root -l -b -q newyield.cpp"("'"'vbfinputinfo.txt'"'")" >vbfyieldtmp.txt
  vbfrate=`cat vbfyieldtmp.txt | grep "rate" | awk '{print $2}'`
  rm vbfyieldtmp.txt
  
  if [ "$DOGGH" = "1" ]
      then
      root -l -b -q newyield.cpp"("'"'gghinputinfo.txt'"'")" >gghyieldtmp.txt
      gghrate=`cat gghyieldtmp.txt | grep "rate" | awk '{print $2}'`
      rm gghyieldtmp.txt
  fi
  
  if [ "$DOGGH" = "1" ]
      then
      oldvbfrate=`grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | awk '{print $3}'`                                                                                
      grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | sed "s:$oldvbfrate:$vbfrate:" >ratetmp.txt
      oldgghrate=`grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | awk '{print $2}'`                                                                                
      grep "rate" ratetmp.txt | sed "s:$oldgghrate:$gghrate:" >>$TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.tx
      echo $gghrate >>newgghrates.txt
  else
      oldvbfrate=`grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | awk '{print $2}'`                                                                                
      grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | sed "s:$oldvbfrate:$vbfrate:" >>$TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.txt
  fi

  echo $vbfrate >> newvbfrates.txt

  #LINE 14 UNCHANGED
  echo ------------ >>${TARGETDIR}/$newmass/vbfhinv_${newmass}_8TeV.txt 
 
    #!!DONE UP TO HERE 

  #PUT NEW ERRORS IN
  echo $newmass>>newerrors.txt
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
    echo $err >>newerrors.txt
  done
  
  
  rm outputvbfxsinfo.txt
done
rm vbfxsinfo.txt
rm vbfinputinfo.txt
rm -r sourceuncs
echo Interpolated datacards successfully created at: $TARGETDIR