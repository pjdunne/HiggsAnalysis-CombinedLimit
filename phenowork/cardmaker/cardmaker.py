#!/usr/bin/python
import sys
import math as m
import argparse as a

#Estimates of backgrounds and uncertainties
bkg_yield_13TeV_20fb=862
bkg_stat_13TeV_20fb=0.062
bkg_syst_13TeV_20fb=0.099

bkg_yield_8TeV_20fb=439.4
bkg_stat_8TeV_20fb=0.093
bkg_syst_8TeV_20fb=0.099

sig_syst_20fb=0.114

#Get options
parser=a.ArgumentParser(description='Make cards for pheno studies')
parser.add_argument('-s','--sig_yield_20fb',required=True)
parser.add_argument('-l','--targetlumi',required=True)
parser.add_argument('--systlumiscale',default=False)
parser.add_argument('-n','--name',default='125')
parser.add_argument('--sqrts',default=13)
args=parser.parse_args()

sig_yield_20fb=args.sig_yield_20fb
targetlumi=args.targetlumi
systlumiscale=args.systlumiscale
signalname=args.name
signalroots=args.sqrts

print 'Model name is: '+str(signalname)
if not systlumiscale:
    print 'Not scaling systematics assuming constant'
else:
    print 'Scaling systematics with sqrt(L)'
print 'Extrapolating signal yield '+str(sig_yield_20fb)+' at 20 fb^{-1} to ',targetlumi,' fb^{-1} for root s ',signalroots,' TeV'

#Set correct background estimate and uncertainties for 20fb
if signalroots==13:
    bkg_yield_20fb=bkg_yield_13TeV_20fb
    bkg_stat_20fb=bkg_stat_13TeV_20fb
    bkg_syst_20fb=bkg_syst_13TeV_20fb
elif signalroots==8:
    bkg_yield_20fb=bkg_yield_8TeV_20fb
    bkg_stat_20fb=bkg_stat_8TeV_20fb
    bkg_syst_20fb=bkg_syst_8TeV_20fb
else:
    print "Centre of mass energy ",signalroots," not supported"
    sys.exit()

#!!scale to target lumi
bkg_yield=float(targetlumi)/20*float(bkg_yield_20fb)
sig_yield=float(targetlumi)/20*float(sig_yield_20fb)
bkg_stat=m.sqrt(20/float(targetlumi))*float(bkg_stat_20fb)
if systlumiscale:
    bkg_syst=m.sqrt(20/float(targetlumi))*float(bkg_syst_20fb)
    sig_syst=m.sqrt(20/float(targetlumi))*float(sig_syst_20fb)
else:
    bkg_syst=bkg_syst_20fb
    sig_syst=sig_syst_20fb

#Open output file
cardname='ext_vbfhinv_'+str(signalname)+'_'+str(signalroots)+'Tev_'+str(targetlumi)+'fb.txt'
print cardname
card=open(cardname,'w')

card.write('# Invisible Higgs analysis for '+str(signalname)+'\n')#Next few lines are admin stuff at beginning of card
card.write('imax 1 number of bins\n')
card.write('jmax 1 number of backgrounds\n')
card.write('kmax * number of nuisance parameters (sources of systematic uncertainties)\n')
card.write('shapes * ch1 FAKE\n')
card.write('bin ch1\n')
card.write('observation '+str(bkg_yield)+'\n')#set observation equal to expected background
card.write('------------\n')
card.write('bin\t\t\tch1\tch1\n')
card.write('process\t\t\tsig\tbkg\n')
card.write('process\t\t\t0\t1\n')
card.write('rate\t\t\t'+str(sig_yield)+'\t'+str(bkg_yield)+'\n')
card.write('------------\n')
card.write('bkg_stat\tlnN\t-\t'+str(bkg_stat+1)+'\n')
card.write('bkg_syst\tlnN\t-\t'+str(bkg_syst+1)+'\n')
card.write('sig_syst\tlnN\t'+str(sig_syst+1)+'\t-\n')
