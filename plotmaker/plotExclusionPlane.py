import ROOT as r
import sys
import CMS_lumi
import math as m
import numpy as np
from array import array


def frameTH2D(hist, threshold, mult = 1.0):
  # NEW LOGIC:
  #   - pretend that the center of the last bin is on the border if the frame
  #   - add one tiny frame with huge values
  frameValue = 1000
  # if (TString(in->GetName()).Contains("bayes")) frameValue = -1000;

  xw = hist.GetXaxis().GetBinWidth(1)
  yw = hist.GetYaxis().GetBinWidth(1)

  nx = hist.GetNbinsX()
  ny = hist.GetNbinsY()

  x0 = hist.GetXaxis().GetXmin()
  x1 = hist.GetXaxis().GetXmax()

  y0 = hist.GetYaxis().GetXmin()
  y1 = hist.GetYaxis().GetXmax()
  xbins = array('d', [0]*999)
  ybins = array('d', [0]*999)
  eps = 0.1
  # mult = 1.0

  xbins[0] = x0 - eps * xw - xw * mult
  xbins[1] = x0 + eps * xw - xw * mult
  for ix in xrange(2, nx+1): xbins[ix] = x0 + (ix - 1) * xw
  xbins[nx + 1] = x1 - eps * xw + 0.5 * xw * mult
  xbins[nx + 2] = x1 + eps * xw + xw * mult

  ybins[0] = y0 - eps * yw - yw * mult
  ybins[1] = y0 + eps * yw - yw * mult
  for iy in xrange(2, ny+1): ybins[iy] = y0 + (iy - 1) * yw
  ybins[ny + 1] = y1 - eps * yw + yw * mult
  ybins[ny + 2] = y1 + eps * yw + yw * mult

  framed = r.TH2D('%s framed' % hist.GetName(), '%s framed' % hist.GetTitle(), nx + 2, xbins, ny + 2, ybins)

  # Copy over the contents
  for ix in xrange(1, nx+1):
    for iy in xrange(1, ny+1):
      framed.SetBinContent(1 + ix, 1 + iy, hist.GetBinContent(ix, iy))
  
  # Frame with huge values
  nx = framed.GetNbinsX()
  ny = framed.GetNbinsY()
  for ix in xrange(1, nx+1):
    framed.SetBinContent(ix, 1, frameValue)
    framed.SetBinContent(ix, ny, frameValue)

  for iy in xrange(2, ny):
    framed.SetBinContent(1, iy, frameValue)
    framed.SetBinContent(nx, iy, frameValue)

  return framed

def contourFromTH2(h2in, threshold, minPoints=10, mult = 1.0):
  # std::cout << "Getting contour at threshold " << threshold << " from "
  #           << h2in->GetName() << std::endl;
  # // http://root.cern.ch/root/html/tutorials/hist/ContourList.C.html
  contoursList = [threshold]
  contours = array('d', contoursList)
  if (h2in.GetNbinsX() * h2in.GetNbinsY()) > 10000: minPoints = 50
  if (h2in.GetNbinsX() * h2in.GetNbinsY()) <= 100: minPoints = 10

  # h2 = h2in.Clone()
  h2 = frameTH2D(h2in, threshold, mult)

  h2.SetContour(1, contours)

  # Draw contours as filled regions, and Save points
  backup = r.gPad
  canv = r.TCanvas('tmp', 'tmp')
  canv.cd()
  h2.Draw('CONT Z LIST')
  r.gPad.Update() # Needed to force the plotting and retrieve the contours in

  conts = r.gROOT.GetListOfSpecials().FindObject('contours')
  contLevel = None

  if conts is None or conts.GetSize() == 0:
    print '*** No Contours Were Extracted!'
    return None
  ret = r.TList()
  for i in xrange(conts.GetSize()):
    contLevel = conts.At(i)
    print 'Contour %d has %d Graphs\n' % (i, contLevel.GetSize())
    for j in xrange(contLevel.GetSize()):
      gr1 = contLevel.At(j)
      print'\t Graph %d has %d points' % (j, gr1.GetN())
      if gr1.GetN() > minPoints: ret.Add(gr1.Clone())
      # // break;
  backup.cd()
  return ret


outf = r.TFile('PlotCanvas.root','RECREATE')
def makePlot():

  # CMS_lumi.lumi_8TeV = "19.2 fb^{-1}"
  # CMS_lumi.writeExtraText = 1
  # CMS_lumi.extraText = "Preliminary"

  #Get y values and combine output files from input text file
  infile=open(sys.argv[1],"r")
  filestoread=infile.readlines()
  yvalues=[]
  print "Input y values and files:"
  for i in range(len(filestoread)):
    thisline=filestoread[i].split()
    print thisline
    yvalues.append([thisline[0],thisline[1]])
  yvalues.sort(key=lambda x: x[0])

  down95values=[]
  down68values=[]
  medianvalues=[]
  up68values=[]
  up95values=[]
  obsvalues=[]
  #loop over y values getting tfiles and extracting x values and limits
  ybincenters=[]
  xbincenters=[]
  for i in range(len(yvalues)):
    ybincenters.append(float(yvalues[i][0]))
    tf = r.TFile(yvalues[i][1])
    tree = tf.Get('limit')
    xvalues=[]
    for j in range(tree.GetEntries()):
      tree.GetEntry(j)
      xvalues.append([tree.mh, tree.limit])
    xvalues.sort(key=lambda x: x[0])

    # get limits for all x values for this y value
    for j in range(len(xvalues)):
      if (j%6==0):
        down95values.append([xvalues[j][0],yvalues[i][0],xvalues[j][1]])
        down68values.append([xvalues[j][0],yvalues[i][0],xvalues[j+1][1]])
        medianvalues.append([xvalues[j][0],yvalues[i][0],xvalues[j+2][1]])
        up68values.append([xvalues[j][0],yvalues[i][0],xvalues[j+3][1]])
        up95values.append([xvalues[j][0],yvalues[i][0],xvalues[j+4][1]])
        obsvalues.append([xvalues[j][0],yvalues[i][0],xvalues[j+5][1]])
        if(i==0):
          xbincenters.append(xvalues[j][0])
  
  #Make TH2D out of values with variable binning and value at centre of bin
  xbinedges=[]
  for i in range(len(xbincenters)):
    if(i==0):
      xbinedges.append(xbincenters[i]-m.fabs(xbincenters[i+1]-xbincenters[i])/2)
    if(i!=(len(xbincenters)-1)):
      xbinedges.append(xbincenters[i]+m.fabs(xbincenters[i+1]-xbincenters[i])/2)
    if(i==(len(xbincenters)-1)):
      xbinedges.append(xbincenters[i]+m.fabs(xbincenters[i]-xbincenters[i-1])/2)

  ybinedges=[]
  for i in range(len(ybincenters)):
    if(i==0):
      ybinedges.append(ybincenters[i]-m.fabs(ybincenters[i+1]-ybincenters[i])/2)
    if(i!=(len(ybincenters)-1)):
      ybinedges.append(ybincenters[i]+m.fabs(ybincenters[i+1]-ybincenters[i])/2)
    if(i==(len(ybincenters)-1)):
      ybinedges.append(ybincenters[i]+m.fabs(ybincenters[i]-ybincenters[i-1])/2)


  down95valueth2=r.TH2D("down95values","down95values",len(xbincenters),np.asarray(xbinedges),len(ybincenters),np.asarray(ybinedges))
  down68valueth2=r.TH2D("down68values","down68values",len(xbincenters),np.asarray(xbinedges),len(ybincenters),np.asarray(ybinedges))
  medianvalueth2=r.TH2D("medianvalues","medianvalues",len(xbincenters),np.asarray(xbinedges),len(ybincenters),np.asarray(ybinedges))
  up68valueth2=r.TH2D("up68values","up68values",len(xbincenters),np.asarray(xbinedges),len(ybincenters),np.asarray(ybinedges))
  up95valueth2=r.TH2D("up95values","up95values",len(xbincenters),np.asarray(xbinedges),len(ybincenters),np.asarray(ybinedges))
  obsvalueth2=r.TH2D("obsvalues","obsvalues",len(xbincenters),np.asarray(xbinedges),len(ybincenters),np.asarray(ybinedges))
  print len(down95values)
  for j in range(len(ybincenters)):
    for i in range(len(xbincenters)):
      #print xbincenters
      #print ybincenters
      #print down95values
      print j*len(xbincenters)+i
      down95valueth2.SetBinContent(down95valueth2.GetBin(i+1,j+1),down95values[j*len(xbincenters)+i][2])
      down68valueth2.SetBinContent(down68valueth2.GetBin(i+1,j+1),down68values[j*len(xbincenters)+i][2])
      medianvalueth2.SetBinContent(medianvalueth2.GetBin(i+1,j+1),medianvalues[j*len(xbincenters)+i][2])
      up68valueth2.SetBinContent(up68valueth2.GetBin(i+1,j+1),up68values[j*len(xbincenters)+i][2])
      up95valueth2.SetBinContent(up95valueth2.GetBin(i+1,j+1),up95values[j*len(xbincenters)+i][2])
      obsvalueth2.SetBinContent(obsvalueth2.GetBin(i+1,j+1),obsvalues[j*len(xbincenters)+i][2])

  #call getcontour function
  cont_exp=contourFromTH2(medianvalueth2, 1, minPoints=10, mult = 1.0)

  ipos=33
  
  canv = r.TCanvas()
  canv.Clear()
  canv.SetLogy(False)
  canv.SetLogx(True)
  leg = r.TLegend(0.15, 0.55, 0.52, 0.89)
  leg.SetFillColor(0)
  leg.SetBorderSize(0)
  leg.SetTextFont(62)

  dummyHist = r.TH2D("dummy","dummy",len(xbincenters),np.asarray(xbinedges),len(ybincenters),np.asarray(ybinedges))
  dummyHist.GetXaxis().SetTitle('m_{H} [GeV]')
  dummyHist.GetYaxis().SetTitle('m_{DM} [GeV]')
  dummyHist.SetTitleSize(.05,"X")
  dummyHist.SetTitleOffset(0.75,"X")
  dummyHist.SetTitleSize(.05,"Y")
  dummyHist.SetTitleOffset(0.75,"Y")
  # make text box
  lat = r.TLatex()
  lat.SetNDC()
  #lat.SetTextSize(0.06)
  lat.SetTextFont(42);

  lat2 = r.TLatex()
  lat2.SetNDC()
  lat2.SetTextSize(0.04)
  lat2.SetTextFont(42);
  dummyHist.Draw()
  cont_exp.Draw("F same")
      
  #plot
#   graph.SetMarkerStyle(21)
#   graph.SetMarkerSize(0.5)
#   graph.SetLineColor(1)
#   graph.SetLineWidth(2)
#   exp.SetLineColor(2)
#   exp.SetLineStyle(1)

#   oneSigma.SetLineColor(r.kGreen)
#   twoSigma.SetLineColor(r.kYellow)
#   oneSigma.SetFillColor(r.kGreen)
#   twoSigma.SetFillColor(r.kYellow)
#   exp.SetLineColor(2)
#   exp.SetLineStyle(1)
#   exp.SetLineWidth(2)

#   exp.SetLineWidth(2)
  leg.SetHeader('95% CL limits')
  leg.AddEntry(cont_exp,'Observed limit','L')
#   leg.AddEntry(exp,'Constant syst expected limit','L')
#  leg.AddEntry(oneSigma,'Expected limit (1#sigma)','F') 
#  leg.AddEntry(twoSigma,'Expected limit (2#sigma)','F')
  
#  mg.Add(twoSigma)
#  mg.Add(oneSigma)
#  mg.Add(exp)
#  mg.Add(graph)
  
  # draw dummy hist and multigraph
  #mg.Draw("A")
  dummyHist.SetMinimum(ybinedges[0])
  dummyHist.SetMaximum(ybinedges[len(ybinedges)-1])#mg.GetYaxis().GetXmax())
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
#!!  dummyHist.Draw("AXIS")
#  mg.Draw("3")
#  mg.Draw("LPX")
#!!  cont_exp.Draw("LPX")
#!!  dummyHist.Draw("AXIGSAME")
 
  # draw line at y=1 
  # l = r.TLine(110.,1.,400.,1.)
  # l.SetLineColor(r.kBlue)
  # l.SetLineWidth(2)
  # l.Draw()

  # draw text
  #lat.DrawLatex(0.52,0.85,"CMS VBF H #rightarrow invisible")
  #lat.DrawLatex(0.52,0.78,"#sqrt{s} = 8 TeV, L = 19.2 fb^{-1}")
  lat.DrawLatex(0.61,0.68,"VBF H #rightarrow invisible")

  #CMS_lumi.CMS_lumi(canv, 2, iPos)
    
  
  # draw legend
  leg.Draw("same")
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  canv.Print('vbflimit.pdf')
  outf.cd()
  canv.SetName("limit_cavas")
  canv.Write()

makePlot()



# def getContour(inHistTemp,contourLine =1.):
#     inHist = inHistTemp.Clone()
#     tg2dExp = r.TGraph2D(inHist)
#     contours = [1.0]
#     contourExp = 0
#     contourExpPlus = 0
#     contourExpMinus = 0

#     tg2dExp.GetHistogram().SetContour(1,array('d',contours))
#     tg2dExp.Draw("cont list")
#     contLevel = tg2dExp.GetContourList(contourLine)
#     if contLevel.GetSize()>0:
#         contourExp = contLevel.First()
#     if type(contourExp) != int: contourExp.SetName(inHist.GetName()+"r1Contour")
#     return contourExp

# def interpolate(inHist):
#     interpIn = inHist.Clone()
#     interpIn.Reset()
#     tg2dExpTemp = r.TGraph2D(inHist)
#     for x in range(1,interpIn.GetNbinsX()+1):
#         for y in range(1,interpIn.GetNbinsY()+1):
#             interpIn.SetBinContent(x,y,tg2dExpTemp.Interpolate(inHist.GetXaxis().GetBinCenter(x),inHist.GetYaxis().GetBinCenter(y)))
#     interpIn.SetName(interpIn.GetName()+"interp")
#     return interpIn

# def getContours(outHist,quants = ["central","up1","down1"],contourLine = 1.):
#     contours = {}
#     for quant in quants:
#         contours[quant] = getContour(outHist[quant],contourLine)
#         contours[quant].SetLineWidth(2)
#     return contours

# def drawContours(contourList,hist,name,outputDir,logz=True):
#     if type(contourList) != list:
#         contourList = [(contourList,None)]
#     if name == "mu":
#         hist.GetZaxis().SetTitle("95% C.L. upper limit on #sigma/#sigma_{theory}")
#     elif name == "xs":
#         hist.GetZaxis().SetTitle("95% C.L. upper limit on #sigma")
#     elif name == "sigma":
#         hist.GetZaxis().SetTitle("Expected sensitivity (#sigma)")

#     leg = r.TLegend(0.2,0.76,0.49,0.90)
#     leg.SetBorderSize(0)
#     leg.SetFillStyle(0)
#     leg.SetTextSize(0.04)
#     leg.SetHeader("T1bbbb 3/fb")
#     c2 = r.TCanvas("Contour","Contour")
#     c2.SetRightMargin(0.16)
#     if logz:
#         c2.SetLogz()
#     c2.cd()
#     hist.Draw("colz")
#     for i,(contours,detail) in enumerate(contourList):
#         if name != "sigma":
#             leg.AddEntry(contours["central"],"Expected limit",'l')
#         else:
#             leg.AddEntry(contours["central"],"Contour of {}#sigma".format(detail),'l')
#         #outHistToWrite["central"].Draw("colz")
#         contours["central"].Draw("same")
#         contours["central"].SetLineStyle(i+1)
#         if "up1" in contours:
#             contours["up1"].SetLineStyle(2)
#             leg.AddEntry(contours["up1"],"Expected limit #pm 1 #sigma",'l')
#             contours["up1"].Draw("same")
#         if "down1" in contours:
#             contours["down1"].SetLineStyle(2)
#             contours["down1"].Draw("same")
#     leg.Draw("same")
#     c2.Modified()
#     c2.Update()
#     c2.SaveAs(outputDir+"/"+name+"_contour_withHisto.pdf")
#     c2.Close()
