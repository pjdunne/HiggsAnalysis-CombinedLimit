#!/usr/bin/python
import os
import sys
import argparse as a

cardmakerpath='./scripts/cardmaker.py'
combinecommand='combine -M Asymptotic'
outfilename='gridinfo'

parser=a.ArgumentParser(description='Make and run over grid of cards for pheno studies')
parser.add_argument('-i','--infile',required=True)
parser.add_argument('--xname',default='mH')
parser.add_argument('--yname',default='mchi')
parser.add_argument('-l','--lumi',default='300')
args=parser.parse_args()


xvarname=args.xname
yvarname=args.yname
infilename=args.infile
lumi=args.lumi

print 'xvar: '+xvarname+' yvar: '+yvarname+' lumi: '+lumi

print 'Getting grid from '+infilename
infile=open(infilename)

points=infile.readlines()
vals=[]
for iPoint in range(len(points)):
    thisPoint=points[iPoint].split()
    if(len(thisPoint)!=3):
        print 'Error input format should be: xval yval yield, not '+points[iPoint]
    xvarval=thisPoint[0]
    yvarval=thisPoint[1]
    vals.append([yvarval,xvarval])
    yield_19_2fb=thisPoint[2]

    os.system(cardmakerpath+' -s '+yield_19_2fb+' -l '+lumi+' -n extsyst'+xvarname+xvarval+yvarname+yvarval+' -b True')
    os.system(cardmakerpath+' -s '+yield_19_2fb+' -l '+lumi+' --systlumiscale True -n extsystlumiscale'+xvarname+xvarval+yvarname+yvarval+' -b True')
    os.system(combinecommand+' -m '+xvarval+' -n syst'+yvarname+yvarval+xvarname+xvarval+' ext_vbfhinv_extsyst'+xvarname+xvarval+yvarname+yvarval+'_13TeV_'+lumi+'fb.txt')
    os.system(combinecommand+' -m '+xvarval+' -n systlumiscale'+yvarname+yvarval+xvarname+xvarval+' ext_vbfhinv_extsystlumiscale'+xvarname+xvarval+yvarname+yvarval+'_13TeV_'+lumi+'fb.txt')

#Check grid is complete
xvals=[]
yvals=[]
for i in range(len(vals)):
    if vals[i][1] not in xvals:
          xvals.append(vals[i][1])
    if vals[i][0] not in yvals:
          yvals.append(vals[i][0])
for i in range(len(xvals)):
    for j in range(len(yvals)):
        if [yvals[j],xvals[i]] not in vals:
            print 'Error: you must have a value for all points in the grid'
            exit()

#make input for exclusion plotter
outfilesyst=open(outfilename+'syst.txt','w')
outfilesystlumiscale=open(outfilename+'systlumiscale.txt','w')
for i in range(len(yvals)):
        outfilesyst.write(yvals[i]+' '+os.getcwd()+'/extsyst_'+yvarname+yvals[i]+'combineresults.root\n')
        outfilesystlumiscale.write(yvals[i]+' '+os.getcwd()+'/extsystlumiscale_'+yvarname+yvals[i]+'combineresults.root\n')
        os.system('hadd -f extsyst_'+yvarname+yvals[i]+'combineresults.root higgsCombinesyst'+yvarname+yvals[i]+xvarname+'*.root')
        os.system('hadd -f extsystlumiscale_'+yvarname+yvals[i]+'combineresults.root higgsCombinesystlumiscale'+yvarname+yvals[i]+xvarname+'*.root')
