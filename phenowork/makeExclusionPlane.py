import ROOT as r
r.gROOT.SetBatch(True)
from array import array
import optparse
from collections import defaultdict
import numpy as np
import re
import os
import pickle
from tdrStyle import setTdrStyle
from tdrStyle import SetPalette

def parse_args():
    parser = optparse.OptionParser()
    parser.add_option('-i','--inDir', default="output_optimisation", help="Output directory for datacards and root output files")
    parser.add_option('-o','--outputDir',default = "gridOut",help = "Output file with grid")
    parser.add_option('--noContour',action="store_true",help = "Don't make contours")
    parser.add_option('--mode',default="ul",help = "Run mode (ul or pv)")

    options,args = parser.parse_args()
    return options 

def main(inDir,outputDir,noContour,mode):
    # bjoernPoints = np.loadtxt("bjoernLimit.txt",delimiter=",")
    # x = bjoernPoints[:,0]
    # y = bjoernPoints[:,1]
    # overlayScorpion = False
    # if os.path.exists("bjoernLimit.txt"):        
    #     bjoernPoints = np.loadtxt("bjoernLimit.txt",delimiter=",")
    #     x = bjoernPoints[:,0]
    #     y = bjoernPoints[:,1]
    #     overlayScorpion = True
    gluinoXsFile = "/home/hep/mc3909/AlphaTools/analysis/XS/gluino13.pkl"
    gluinoXsDict = pickle.load(open(gluinoXsFile,"r"))
    vectorModelXs = pickle.load(open("/home/hep/mc3909/vectorModelXs.pkl","r"))
    scalarModelXs = pickle.load(open("/home/hep/mc3909/scalarModelXs.pkl"))
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    plotVar = "limit"
    treeName = "limit"

    if mode == "ul":
        quantiles = ["down2","down1","central","up1","up2"]
    elif mode == "pv":
        quantiles = ["central"]
    else:
        raise AttributeError, "Mode either ul or pv"
    
    outputFile = r.TFile(outputDir+"/gridOut.root","RECREATE")
    modelResults = {}
    #excludePoints = [(10,500),(50,500)]
    excludePoints = []
    with open(inDir+"/signalModels.txt") as f:
        models = f.read().splitlines()
    for model in models:
        #inputs = os.listdir(os.path.join(inDir))
        inputs = os.listdir(os.path.join(inDir,model))
        for inName in inputs:
            if mode == "ul":
                if "combineOut"+model+"_" in inName and "ASCLS" in inName and ("mht_card" in inName or "10DC" in inName):
                    break
            elif mode == "pv":
                if "combineOut"+model+"_" in inName and "ASPL" in inName and  ("mht_card" in inName or "10DC" in inName):
                    break
        else:
            print "Didn't find file for model: ",model
            continue
        fileIn = r.TFile("/".join([inDir,model,inName]))
        #fileIn = r.TFile("/".join([inDir,inName]))
        if not fileIn.GetListOfKeys().Contains(treeName): continue
        treeIn = fileIn.Get(treeName)
        rValues = {}
        if mode == "ul":
            if treeIn.GetEntries() != 5: continue
        elif mode == "pv":
            if treeIn.GetEntries() != 1: continue
        for i,event in enumerate(treeIn):
            rValues[quantiles[i]] = getattr(event,plotVar)
            
        if "DM" in model:
            if len(re.findall('(?<=Mchi-)\d+',model)) > 1:
                m1=float(re.findall('(?<=Mchi-)\d+',model)[0])
                m2=float(re.findall('(?<=Mchi-)\d+',model)[1])
            else:
                m1=float(re.findall('(?<=Mphi-)\d+',model)[0])
                m2=float(re.findall('(?<=Mchi-)\d+',model)[0])
            if "V" in model:
                if "V" not in modelResults.keys():
                    modelResults["V"] = defaultdict(dict)
                modelResultsDict = modelResults["V"]
            elif "S" in model:
                if "S" not in modelResults.keys():
                    modelResults["S"] = defaultdict(dict)
                modelResultsDict = modelResults["S"]
        elif "T1bbbb" in model:
            m2=float(model.split("_")[-1])
            m1=float(model.split("_")[-3])
            if "T1bbbb" not in modelResults.keys():
                modelResults["T1bbbb"] = defaultdict(dict)
            modelResultsDict = modelResults["T1bbbb"]

        for key,rValue in rValues.iteritems(): 
            modelResultsDict[key].update({(m1,m2): rValue})

    for modelType,modelTypeDict in modelResults.iteritems():
        outDir = outputFile.mkdir(modelType)
        outDir.cd()
        outHist = {} 
        outHistToWrite = {} 
        outHistXs = {} 
        # if overlayScorpion:
        #     bgraph = r.TGraph(len(x),array('d',x),array('d',y))
        #     bgraph.SetTitle("bjoern points")
        #     bgraph.SetName("bjoern points")
        #     bgraph.Write()
        for quantile,points in modelTypeDict.iteritems():
            xPoints = [point[0] for point in points]
            yPoints = [point[1] for point in points]
            xPoints = sorted(list(set(xPoints)))
            yPoints = sorted(list(set(yPoints)))
            xPoints.append(xPoints[-1]+100)
            yPoints.append(yPoints[-1]+100)
            xPoints.insert(0,0)
            yPoints.insert(0,0)
            # xPoints = [xPoints[i]+0.5*(xPoints[i+1]-xPoints[i]) for i in range(len(xPoints)-1)]
            # yPoints = [yPoints[i]+0.5*(yPoints[i+1]-yPoints[i]) for i in range(len(yPoints)-1)]
            outHist[quantile] = r.TH2D(quantile,";m_{Gluino} (GeV/c^{2});m_{LSP} (GeV/c^{2}); 95% C.L. limit on #mu",200,0,2000,150,0,1500)
            if mode == "ul":
                outHistXs[quantile] = r.TH2D(quantile+"xs",";m_{Gluino} (GeV/c^{2});m_{LSP} (GeV/c^{2}); 95% C.L. limit on #mu",200,0,2000,150,0,1500)
            outHistToWrite[quantile] = r.TH2D(quantile+"temp",";m_{Gluino} (GeV/c^{2});m_{LSP} (GeV/c^{2}); 95% C.L. limit on #mu",len(xPoints)-1,array('d',xPoints),len(yPoints)-1,array('d',yPoints))
            rValueMin = 100000
            xsValueMin = 1
            for point,rValue in points.iteritems():
                if point in excludePoints: continue
                rValueMin = min(rValueMin,rValue)
                if modelType == "T1bbbb":
                    outHistToWrite[quantile].Fill(point[0]+0.1,point[1]+0.1,rValue)
                    outHist[quantile].Fill(point[0]+0.1,point[1]+0.1,rValue)
                    if mode == "ul":
                        outHistXs[quantile].Fill(point[0]+0.1,point[1]+0.1,rValue*gluinoXsDict[int(point[0])].n)
                    xsValueMin = min(xsValueMin,rValue*gluinoXsDict[int(point[0])].n)
                elif modelType == "V":
                    # if quantile == "central":
                    #     print modelType,point[0],point[1],rValue/vectorModelXs[(int(point[0]),int(point[1]))],vectorModelXs[(int(point[0]),int(point[1]))]
                    outHistToWrite[quantile].Fill(point[0]+0.1,point[1]+0.1,rValue/vectorModelXs[(int(point[0]),int(point[1]))])
                    outHist[quantile].Fill(point[0]+0.1,point[1]+0.1,rValue/vectorModelXs[(int(point[0]),int(point[1]))])
                    if mode == "ul":
                        outHistXs[quantile].Fill(point[0]+0.1,point[1]+0.1,rValue)
                elif modelType == "S":
                    #if quantile == "central":
                        #print modelType,point[0],point[1],rValue/scalarModelXs[(int(point[0]),int(point[1]))],scalarModelXs[(int(point[0]),int(point[1]))]
                    outHistToWrite[quantile].Fill(point[0]+0.1,point[1]+0.1,rValue/scalarModelXs[(int(point[0]),int(point[1]))])
                    outHist[quantile].Fill(point[0]+0.1,point[1]+0.1,rValue/scalarModelXs[(int(point[0]),int(point[1]))])
                    if mode == "ul":
                        outHistXs[quantile].Fill(point[0]+0.1,point[1]+0.1,rValue)
                    xsValueMin = min(xsValueMin,rValue)
            outHistToWrite[quantile].Write()        

        if not noContour:
            if mode == "ul":
                contours = getContours(outHist)
                interpHistLimit = interpolate(outHist["central"]) 

                interpHistXs = interpolate(outHistXs["central"]) 
                interpHistXs.SetMinimum(1E-3)
                drawContours(contours,interpHistXs,"xs",outputDir)
                interpHistLimit.SetMinimum(1E-3)
                drawContours(contours,interpHistLimit,"mu",outputDir)
            elif mode == "pv":
                contours = getContours(outHist,["central"],3.)
                contours5Sigma = getContours(outHist,["central"],5.)
                interpHistSigma = interpolate(outHist["central"]) 
                interpHistSigma.SetMaximum(6)
                drawContours([(contours,"3"),(contours5Sigma,"5")],interpHistSigma,"sigma",outputDir,logz=False)
        else:
            r.gStyle.SetPaintTextFormat("0.2f")
            c2 = r.TCanvas("histOnly","histOnly")
            outHist["central"].Draw("colz")
            c2.SaveAs(outputDir+"/centralHist.pdf")
            c2.Close()
            # c2.Write()

def getContour(inHistTemp,contourLine =1.):
    inHist = inHistTemp.Clone()
    tg2dExp = r.TGraph2D(inHist)
    contours = [1.0]
    contourExp = 0
    contourExpPlus = 0
    contourExpMinus = 0

    tg2dExp.GetHistogram().SetContour(1,array('d',contours))
    tg2dExp.Draw("cont list")
    contLevel = tg2dExp.GetContourList(contourLine)
    if contLevel.GetSize()>0:
        contourExp = contLevel.First()
    if type(contourExp) != int: contourExp.SetName(inHist.GetName()+"r1Contour")
    return contourExp

def interpolate(inHist):
    interpIn = inHist.Clone()
    interpIn.Reset()
    tg2dExpTemp = r.TGraph2D(inHist)
    for x in range(1,interpIn.GetNbinsX()+1):
        for y in range(1,interpIn.GetNbinsY()+1):
            interpIn.SetBinContent(x,y,tg2dExpTemp.Interpolate(inHist.GetXaxis().GetBinCenter(x),inHist.GetYaxis().GetBinCenter(y)))
    interpIn.SetName(interpIn.GetName()+"interp")
    return interpIn
def getContours(outHist,quants = ["central","up1","down1"],contourLine = 1.):
    contours = {}
    for quant in quants:
        contours[quant] = getContour(outHist[quant],contourLine)
        contours[quant].SetLineWidth(2)
    return contours
def drawContours(contourList,hist,name,outputDir,logz=True):
    if type(contourList) != list:
        contourList = [(contourList,None)]
    if name == "mu":
        hist.GetZaxis().SetTitle("95% C.L. upper limit on #sigma/#sigma_{theory}")
    elif name == "xs":
        hist.GetZaxis().SetTitle("95% C.L. upper limit on #sigma")
    elif name == "sigma":
        hist.GetZaxis().SetTitle("Expected sensitivity (#sigma)")

    leg = r.TLegend(0.2,0.76,0.49,0.90)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.04)
    leg.SetHeader("T1bbbb 3/fb")
    c2 = r.TCanvas("Contour","Contour")
    c2.SetRightMargin(0.16)
    if logz:
        c2.SetLogz()
    c2.cd()
    hist.Draw("colz")
    for i,(contours,detail) in enumerate(contourList):
        if name != "sigma":
            leg.AddEntry(contours["central"],"Expected limit",'l')
        else:
            leg.AddEntry(contours["central"],"Contour of {}#sigma".format(detail),'l')
        #outHistToWrite["central"].Draw("colz")
        contours["central"].Draw("same")
        contours["central"].SetLineStyle(i+1)
        if "up1" in contours:
            contours["up1"].SetLineStyle(2)
            leg.AddEntry(contours["up1"],"Expected limit #pm 1 #sigma",'l')
            contours["up1"].Draw("same")
        if "down1" in contours:
            contours["down1"].SetLineStyle(2)
            contours["down1"].Draw("same")
    leg.Draw("same")
    c2.Modified()
    c2.Update()
    c2.SaveAs(outputDir+"/"+name+"_contour_withHisto.pdf")
    c2.Close()


if __name__ == "__main__":
    myStyle = setTdrStyle()
    setPalette = SetPalette(style=myStyle)
    setPalette()
    main(**vars(parse_args()))
