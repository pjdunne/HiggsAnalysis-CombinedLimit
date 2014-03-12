#!/bin/bash
echo Datacard Interpolator for VBF Higgs to Invisible Analysis
CARDDIR="../vbfcards/PromptPaper120314Cards/cardsfromchayanit/"
TARGETDIR="trialfornewcards/" #../vbfcards/ggHAndNewZbkgPromptPaperCards/couplings/" #"../vbfcards/PromptPaperCards/searches/"
VBFXSDATFILE="../data/lhc-hxswg/sm/xs/8TeV/8TeV-vbfH.txt"
GGHXSDATFILE="../data/lhc-hxswg/sm/xs/8TeV/8TeV-ggH.txt"
DOGGH=1
rm vbfxsinfo.txt
rm vbfinputinfo.txt
rm gghinputinfo.txt
rm gghxsinfo.txt
rm gghnmcs.txt
rm -r sourceuncs
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
	    if [ "$DOGGH" = "1" ]
		then
		rawggherror=`grep "$sources" $card | awk '{print $3}'`
		rawvbferror=`grep "$sources" $card | awk '{print $4}'`
	    else
		rawvbferror=`grep "$sources" $card | awk '{print $3}'`
	    fi
	    
	elif [ `grep "$sources" $card | awk '{print $2}'` = "gmN" ]
	then
	    if [ "$DOGGH" = "1" ]
		then
		rawggherror=`grep "$sources" $card | awk '{print $4}'`
		rawvbferror=`grep "$sources" $card | awk '{print $5}'`
		if [ "$sources" = "CMS_VBFHinv_ggH_norm" ]
		    then
		    gghnmc=`grep "$sources" $card | awk '{print $3}'`
		    echo $mass sym $gghnmc >>gghnmcs.txt
		fi
	    else
		rawvbferror=`grep "$sources" $card | awk '{print $4}'`
	    fi
	else
	    echo ERROR: UNRECOGNISED ERROR TYPE
	    exit 1
	fi

	if [ $rawvbferror = "-" ]
	then
	#ERROR DOESN'T AFFECT SIGNAL
	    echo $mass noeff >> sourceuncs/vbf$sources.txt
	else
	    #CHECK FOR ASYMMETRIC ERROR ON SIGNAL
	    echo $rawvbferror | grep "/" > /dev/null
	    if [ $? = 0 ]
	    then
		downvbferror=`echo $rawvbferror | sed "s/\// /" | awk '{print $1}'`
		upvbferror=`echo $rawvbferror | sed "s/\// /" | awk '{print $2}'`
		echo $mass asym $downvbferror $upvbferror >> sourceuncs/vbf$sources.txt
	    else
	    #ERROR IS SYMMETRIC FOR SIGNAL
		echo $mass sym $rawvbferror >> sourceuncs/vbf$sources.txt
	    fi
	fi

	if [ "$DOGGH" = "1" ]
	    then
	    if [ $rawggherror = "-" ]
		then
	#ERROR DOESN'T AFFECT SIGNAL
		echo $mass noeff >> sourceuncs/ggh$sources.txt
	    else
	    #CHECK FOR ASYMMETRIC ERROR ON SIGNAL
		echo $rawggherror | grep "/" > /dev/null
		if [ $? = 0 ]
		    then
		    downggherror=`echo $rawggherror | sed "s/\// /" | awk '{print $1}'`
		    upggherror=`echo $rawggherror | sed "s/\// /" | awk '{print $2}'`
		    echo $mass asym $downggherror $upggherror >> sourceuncs/ggh$sources.txt
		else
	    #ERROR IS SYMMETRIC FOR SIGNAL
		    echo $mass sym $rawggherror >> sourceuncs/ggh$sources.txt
		fi
	    fi
	fi

    done
done

#GET INFO AT MASSES WE WANT CARDS FOR

rm -r $TARGETDIR
mkdir $TARGETDIR

echo Making new cards for:
newmasses="110 125 150 200 300 400" #`cat couplingsmasses.txt` #"110 125 150 200 300 400" #
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
      echo $newmass $gghxs > outputgghxsinfo.txt
      rm gghxstmp.txt
  fi
  
  
#MAKE NEW CARDS
  #FIRST 12 LINES ARE UNCHANGED
  grep -m 12 "" ${CARDDIR}vbfhinv_125_8TeV.txt >$TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.txt 
  sed -i "s:# Invisible Higgs analysis for mH=125 GeV:# Invisible Higgs analysis for mH=$newmass GeV:" $TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.txt
  
  #PUT NEW RATE IN
  root -l -b -q newyield.cpp"("'"'vbf'"'")" > vbfyieldtmp.txt
  vbfrate=`cat vbfyieldtmp.txt | grep "rate" | awk '{print $2}'`
  rm vbfyieldtmp.txt

  if [ "$DOGGH" = "1" ]
      then
      root -l -q newyield.cpp"("'"'ggh'"'")" > gghyieldtmp.txt
      gghrate=`cat gghyieldtmp.txt | grep "rate" | awk '{print $2}'`
      rm gghyieldtmp.txt
  fi
  
  if [ "$DOGGH" = "1" ]
      then
      oldvbfrate=`grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | awk '{print $3}'`                                                                      
      grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | sed "s:$oldvbfrate:$vbfrate:" >ratetmp.txt
      oldgghrate=`grep "rate" ${CARDDIR}vbfhinv_125_8TeV.txt | awk '{print $2}'`                                                                                
      grep "rate" ratetmp.txt | sed "s:$oldgghrate:$gghrate:" >>$TARGETDIR/$newmass/vbfhinv_${newmass}_8TeV.txt
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
    if [ `grep -m 1 "" sourceuncs/vbf$sources.txt | awk '{print $2}'` = "noeff" ]
        then
        #ERROR DOESN'T AFFECT SIGNAL                                                                                                                   
	vbftype=noeff
    elif [ `grep -m 1 "" sourceuncs/vbf$sources.txt | awk '{print $2}'` = "asym" ]
        then
            #ERROR IS ASYMMETRIC FOR SIGNAL                                                                                                            
	vbftype=asym
    elif [ `grep -m 1 "" sourceuncs/vbf$sources.txt | awk '{print $2}'` = "sym" ]
	then
            #ERROR IS SYMMETRIC FOR SIGNAL                                                                                                              
	vbftype=sym
    fi

    if [ "$DOGGH" = "1" ]
	then
	if [ `grep -m 1 "" sourceuncs/ggh$sources.txt | awk '{print $2}'` = "noeff" ]
	    then
        #ERROR DOESN'T AFFECT SIGNAL                                                                                                                   
	    gghtype=noeff
	elif [ `grep -m 1 "" sourceuncs/ggh$sources.txt | awk '{print $2}'` = "asym" ]
	    then
            #ERROR IS ASYMMETRIC FOR SIGNAL                                                                                                            
	    gghtype=asym
	elif [ `grep -m 1 "" sourceuncs/ggh$sources.txt | awk '{print $2}'` = "sym" ]
	    then
            #ERROR IS SYMMETRIC FOR SIGNAL                                                                                                              
	    gghtype=sym
    fi
    fi


    
    fileforrootmacro=sourceuncs/vbf$sources.txt
    root -l -b -q newunc.cpp"("'"'$fileforrootmacro'"','"'$vbftype'"',$newmass")" > vbfunctmp.txt
    vbferr=`cat vbfunctmp.txt | grep "newerror" |awk '{print $2}'` #SET ERR EQUAL TO APPROPRIATE BIT OF CPP OUTPUT
    rm vbfunctmp.txt

    if [ "$DOGGH" = "1" ]
	then
	fileforrootmacro=sourceuncs/ggh$sources.txt
	root -l -b -q newunc.cpp"("'"'$fileforrootmacro'"','"'$gghtype'"',$newmass")" > gghunctmp.txt
	ggherr=`cat gghunctmp.txt | grep "newerror" |awk '{print $2}'` #SET ERR EQUAL TO APPROPRIATE BIT OF CPP OUTPUT
	rm gghunctmp.txt
	if [ "$sources" = "CMS_VBFHinv_ggH_norm" ]
	    then
	    fileforrootmacro=gghnmcs.txt
	    root -l -b -q newunc.cpp"("'"'$fileforrootmacro'"','"'"sym"'"',$newmass")" | tee gghnmctmp.txt
	    gghnmc=`cat gghnmctmp.txt | grep "newerror" |awk '{print $2}'` #SET ERR EQUAL TO APPROPRIATE BIT OF CPP OUTPUT
	    rm gghnmctmp.txt
	fi
	
    fi
    
    if [ "$DOGGH" = "1" ]
	then
	if [ `grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $2}'` = "lnN" ]
	    then
	    oldvbferr=`grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $4}'`
	    oldggherr=`grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $3}'`
        elif [ `grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $2}'` = "gmN" ]
	    then
	    oldvbferr=`grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $5}'`
	    oldggherr=`grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $4}'`
	    if [ "$sources" = "CMS_VBFHinv_ggH_norm" ]
		then
		oldgghnmc=`grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $3}'`
	    fi
	else
	    echo ERROR: UNRECOGNISED ERROR TYPE SHOULDN"'"T HAVE GOT THIS FAR
	    exit 1
	fi
	if [ "$sources" = "CMS_VBFHinv_ggH_norm" ]
	    then
	    grep "$sources" ${CARDDIR}vbfhinv_125_8TeV.txt | sed "s:$oldggherr:$ggherr:" >>sourcetmp.txt
	    grep "$sources" sourcetmp.txt | sed "s:$oldgghnmc:$gghnmc:" >>sourcetmp2.txt
	    rm sourcetmp.txt
	else
	    grep "$sources" ${CARDDIR}vbfhinv_125_8TeV.txt | sed "s:$oldggherr:$ggherr:" >>sourcetmp2.txt
	fi
	grep "$sources" sourcetmp2.txt | sed "s:$oldvbferr:$vbferr:" >>${TARGETDIR}/$newmass/vbfhinv_${newmass}_8TeV.txt
	rm sourcetmp2.txt
    else
	if [ `grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $2}'` = "lnN" ]
	    then
	    oldvbferr=`grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $3}'`
	    
        elif [ `grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $2}'` = "gmN" ]
	    then
	    oldvbferr=`grep "$sources" $CARDDIR/vbfhinv_125_8TeV.txt | awk '{print $4}'`
	else
	    echo ERROR: UNRECOGNISED ERROR TYPE SHOULDN"'"T HAVE GOT THIS FAR
	    exit 1
	fi
	if [ "$newmass" = "125" ]
	    then
	    echo $oldvbferr $vbferr
	fi
	grep "$sources" ${CARDDIR}vbfhinv_125_8TeV.txt | sed "s:$oldvbferr:$vbferr:" >>${TARGETDIR}/$newmass/vbfhinv_${newmass}_8TeV.txt
    fi
    
    echo $vbferr >>newvbferrors.txt
  done
  
  
  rm outputvbfxsinfo.txt
done
rm vbfxsinfo.txt
rm vbfinputinfo.txt
rm gghinputinfo.txt
rm gghxsinfo.txt
rm gghnmcs.txt
rm -r sourceuncs
echo Interpolated datacards successfully created at: $TARGETDIR