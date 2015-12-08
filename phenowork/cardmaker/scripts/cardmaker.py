#!/usr/bin/python
import sys
import math as m
import argparse as a

#Estimates of backgrounds and uncertainties
bkg_yield_13TeV_19_2fb=741
bkg_stat_13TeV_19_2fb=0.062
bkg_syst_13TeV_19_2fb=0.099

bkg_yield_8TeV_19_2fb=439.4
bkg_stat_8TeV_19_2fb=0.093
bkg_syst_8TeV_19_2fb=0.099

sig_syst_19_2fb=0.114

#Get options
parser=a.ArgumentParser(description='Make cards for pheno studies')
parser.add_argument('-s','--sig_yield_19_2fb',required=True)
parser.add_argument('-l','--targetlumi',required=True)
parser.add_argument('--systlumiscale',default=False)
parser.add_argument('-n','--name',default='125')
parser.add_argument('--sqrts',default=13)
parser.add_argument('-b','--batchmode',default=False)
args=parser.parse_args()

sig_yield_19_2fb=args.sig_yield_19_2fb
targetlumi=args.targetlumi
systlumiscale=args.systlumiscale
signalname=args.name
signalroots=args.sqrts

if(args.batchmode==False):
    print 'Model name is: '+str(signalname)
    if not systlumiscale:
        print 'Not scaling systematics assuming constant'
    else:
        print 'Scaling systematics with sqrt(L)'
        print 'Extrapolating signal yield '+str(sig_yield_19_2fb)+' at 19.2 fb^{-1} to ',targetlumi,' fb^{-1} for root s ',signalroots,' TeV'

#Set correct background estimate and uncertainties for 19_2fb
if signalroots==13:
    bkg_yield_19_2fb=bkg_yield_13TeV_19_2fb
    bkg_stat_19_2fb=bkg_stat_13TeV_19_2fb
    bkg_syst_19_2fb=bkg_syst_13TeV_19_2fb
elif signalroots==8:
    bkg_yield_19_2fb=bkg_yield_8TeV_19_2fb
    bkg_stat_19_2fb=bkg_stat_8TeV_19_2fb
    bkg_syst_19_2fb=bkg_syst_8TeV_19_2fb
else:
    print "Centre of mass energy ",signalroots," not supported"
    sys.exit()

#!!scale to target lumi
bkg_yield=float(targetlumi)/19.2*float(bkg_yield_19_2fb)
sig_yield=float(targetlumi)/19.2*float(sig_yield_19_2fb)
bkg_stat=m.sqrt(19.2/float(targetlumi))*float(bkg_stat_19_2fb)
if systlumiscale:
    bkg_syst=m.sqrt(19.2/float(targetlumi))*float(bkg_syst_19_2fb)
    sig_syst=m.sqrt(19.2/float(targetlumi))*float(sig_syst_19_2fb)
else:
    bkg_syst=bkg_syst_19_2fb
    sig_syst=sig_syst_19_2fb

#Open output file
cardname='ext_vbfhinv_'+str(signalname)+'_'+str(signalroots)+'Tev_'+str(targetlumi)+'fb.txt'
if systlumiscale:
    cardname='ext_vbfhinv_'+str(signalname)+'_'+str(signalroots)+'Tev_'+str(targetlumi)+'fb_scaleL.txt'
if(args.batchmode==True):
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
