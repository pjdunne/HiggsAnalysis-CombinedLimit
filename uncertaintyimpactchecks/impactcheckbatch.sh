cd /vols/cms04/pjd12/invcmssws/CMSSW_7_1_5/src/HiggsAnalysis/CombinedLimit/uncertaintyimpactchecks
source /vols/cms/grid/setup.sh
export SCRAM_ARCH=slc6_amd64_gcc481
eval `scramv1 runtime -sh`
eval ./uncertaintyimpact.sh &> uncertaintyimpact.log