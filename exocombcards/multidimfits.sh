# combine -M MultiDimFit -m 125 --rMax=2 --algo=grid --points=100 -t -1 --toysFrequentist -n ZHExp 125/zhcombinedcard.txt
# combine -M MultiDimFit -m 125 --rMax=2 --algo=grid --points=100 -n ZHObs 125/zhcombinedcard.txt

# combine -M MultiDimFit -m 125 --rMax=2 --algo=grid --points=100 -t -1 --toysFrequentist -n VBFExp 125/vbfhinv_125_8TeV.txt
# combine -M MultiDimFit -m 125 --rMax=2 --algo=grid --points=100 -n VBFObs 125/vbfhinv_125_8TeV.txt

# combine -M MultiDimFit -m 125 --rMax=2 --algo=grid --points=100 -t -1 --toysFrequentist -n ExoExp 125/combined_hinv.txt
# combine -M MultiDimFit -m 125 --rMax=2 --algo=grid --points=100 -n ExoObs 125/combined_hinv.txt

# combine -M MultiDimFit -m 125 --rMax=2 --algo=grid --points=100 -t -1 --toysFrequentist -n CombExp 125/hinvcombinedcard.txt
combine -M MultiDimFit -m 125 --rMax=2 --algo=grid --points=100 -n CombObs 125/hinvcombinedcard.txt

