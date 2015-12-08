import ROOT as r
import sys
import CMS_lumi
import math as m
import numpy as np
from array import array

col_store=[]
def CreateTransparentColor(color, alpha):
  adapt   = r.gROOT.GetColor(color)
  new_idx = r.gROOT.GetListOfColors().GetSize() + 1
  trans = r.TColor(new_idx, adapt.GetRed(), adapt.GetGreen(), adapt.GetBlue(), '', alpha)
  col_store.append(trans)
  trans.SetName('userColor%i' % new_idx)
  return new_idx

def fillTH2(hist2d, graph):
    for x in xrange(1, hist2d.GetNbinsX()+1):
        for y in xrange(1, hist2d.GetNbinsY()+1):
            xc = hist2d.GetXaxis().GetBinCenter(x)
            yc = hist2d.GetYaxis().GetBinCenter(y)
            val = graph.Interpolate(xc, yc)
            hist2d.SetBinContent(x, y, val)

def makeHist(name, xbins, ybins, graph2d):
    len_x = graph2d.GetXmax() - graph2d.GetXmin()
    binw_x = (len_x * 0.5 / (float(xbins) - 1.)) - 1E-5
    len_y = graph2d.GetYmax() - graph2d.GetYmin()
    binw_y = (len_y * 0.5 / (float(ybins) - 1.)) - 1E-5
    hist = r.TH2F(name, '', xbins, graph2d.GetXmin()-binw_x, graph2d.GetXmax()+binw_x, ybins, graph2d.GetYmin()-binw_y, graph2d.GetYmax()+binw_y)
    return hist

def OnePad():
    pad = r.TPad('pad', 'pad', 0., 0., 1., 1.)
    pad.Draw()
    pad.cd()
    result = [pad]
    return result

def frameTH2D(hist, threshold, mult = 1.0,frameValue=1000):
  # NEW LOGIC:
  #   - pretend that the center of the last bin is on the border if the frame
  #   - add one tiny frame with huge values
  #frameValue = 1000
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

  #h2 = h2in.Clone()
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
  yvalues.sort(key=lambda x: float(x[0]))

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
    xvalues.sort(key=lambda x: float(x[0]))

    # get limits for all x values for this y value
    for j in range(len(xvalues)):
      if i==0:
        print xvalues[j]
      if (j%6==0):
        down95values.append([xvalues[j][0],yvalues[i][0],xvalues[j][1]])
        down68values.append([xvalues[j][0],yvalues[i][0],xvalues[j+1][1]])
        medianvalues.append([xvalues[j][0],yvalues[i][0],xvalues[j+2][1]])
        up68values.append([xvalues[j][0],yvalues[i][0],xvalues[j+3][1]])
        up95values.append([xvalues[j][0],yvalues[i][0],xvalues[j+4][1]])
        obsvalues.append([xvalues[j][0],yvalues[i][0],xvalues[j+5][1]])
        if(i==0):
          xbincenters.append(xvalues[j][0])
            
  print xbincenters
  print ybincenters

  graph_minus2sigma=r.TGraph2D()
  graph_minus1sigma=r.TGraph2D()
  graph_exp=r.TGraph2D()
  graph_plus1sigma=r.TGraph2D()
  graph_plus2sigma=r.TGraph2D()
  graph_obs=r.TGraph2D()

  #Populate TGraph with points
  n=0
  for j in range(len(ybincenters)):
    for i in range(len(xbincenters)):
      graph_minus2sigma.SetPoint(n,xbincenters[i],ybincenters[j],down95values[j*len(xbincenters)+i][2])
      graph_minus1sigma.SetPoint(n,xbincenters[i],ybincenters[j],down68values[j*len(xbincenters)+i][2])
      graph_exp.SetPoint(n,xbincenters[i],ybincenters[j],medianvalues[j*len(xbincenters)+i][2])
      graph_plus1sigma.SetPoint(n,xbincenters[i],ybincenters[j],up68values[j*len(xbincenters)+i][2])
      graph_plus2sigma.SetPoint(n,xbincenters[i],ybincenters[j],up95values[j*len(xbincenters)+i][2])
      graph_obs.SetPoint(n,xbincenters[i],ybincenters[j],obsvalues[j*len(xbincenters)+i][2])
      n=n+1

  #Make histogram out of TGraph
  #axis = makeHist('hist2d', 5*len(xbincenters), 5*len(ybincenters), graph_exp)
  axis = r.TH2D('hist2d','', len(xbincenters), graph_exp.GetXmin(), graph_exp.GetXmax(), len(ybincenters), graph_exp.GetYmin(), graph_exp.GetYmax())

  h_exp = makeHist("h_exp", len(xbincenters), len(ybincenters), graph_exp)
  h_obs = makeHist("h_obs", len(xbincenters), len(ybincenters), graph_obs)
  h_minus1sigma = makeHist("h_minus1sigma", len(xbincenters), len(ybincenters), graph_minus1sigma)
  h_plus1sigma = makeHist("h_plus1sigma", len(xbincenters), len(ybincenters), graph_plus1sigma)
  h_minus2sigma = makeHist("h_minus2sigma", len(xbincenters), len(ybincenters), graph_minus2sigma)
  h_plus2sigma = makeHist("h_plus2sigma", len(xbincenters), len(ybincenters), graph_plus2sigma)

  fillTH2(h_exp, graph_exp)
  fillTH2(h_obs, graph_obs)
  fillTH2(h_minus1sigma, graph_minus1sigma)
  fillTH2(h_plus1sigma, graph_plus1sigma)
  fillTH2(h_minus2sigma, graph_minus2sigma)
  fillTH2(h_plus2sigma, graph_plus2sigma)

  #call getcontour function
  cont_minus2sigma=contourFromTH2(h_minus2sigma, 1, minPoints=1, mult = 1.0)
  cont_minus1sigma=contourFromTH2(h_minus1sigma, 1, minPoints=1, mult = 1.0)
  cont_exp=contourFromTH2(h_exp, 1, minPoints=1, mult = 1.0)
  cont_plus1sigma=contourFromTH2(h_plus1sigma, 1, minPoints=1, mult = 1.0)
  cont_plus2sigma=contourFromTH2(h_plus2sigma, 1, minPoints=1, mult = 1.0)


  canv = r.TCanvas()
  pads=OnePad()
  pads[0].Draw()
#  canv.Clear()
#  canv.SetLogy(False)
  pads[0].SetLogx(True)
  leg = r.TLegend(0.15, 0.55, 0.52, 0.89)
  leg.SetFillStyle(0)
  leg.SetBorderSize(0)
  leg.SetTextFont(62)

  axis.GetXaxis().SetTitle('m_{H} [GeV]')
  axis.GetYaxis().SetTitle('m_{DM} [GeV]')
  axis.SetTitleSize(.05,"X")
  axis.SetTitleOffset(0.75,"X")
  axis.SetTitleSize(.05,"Y")
  axis.SetTitleOffset(0.75,"Y")
  axis.SetStats(0)
  axis.GetXaxis().SetRangeUser(xbincenters[0],xbincenters[len(xbincenters)-1])
  axis.GetXaxis().SetRangeUser(xbincenters[0],xbincenters[len(xbincenters)-1])
  axis.Draw()

  # make text box
  lat = r.TLatex()
  lat.SetNDC()
  #lat.SetTextSize(0.06)
  lat.SetTextFont(42);

  lat2 = r.TLatex()
  lat2.SetNDC()
  lat2.SetTextSize(0.04)
  lat2.SetTextFont(42);

  # for i, p in enumerate(cont_exp):
  #   p.SetLineColor(0)
  #   p.SetLineWidth(2)
  #   p.SetLineStyle(1)
  #   p.SetFillColor(r.kBlue)
  #   p.Draw("F SAME")


  for i, p in enumerate(cont_minus2sigma):
    p.SetLineColor(0)
    p.SetFillColor(r.kGray+1)
    p.SetFillStyle(1001)
    p.Draw("F SAME")

  for i, p in enumerate(cont_minus1sigma):
    p.SetLineColor(0)
    p.SetFillColor(r.kGray+2)
    p.SetFillStyle(1001)
    p.Draw("F SAME")

  for i, p in enumerate(cont_plus1sigma):
    p.SetLineColor(0)
    p.SetFillColor(r.kGray+1)
    p.SetFillStyle(1001)
    p.Draw("F SAME")

  for i, p in enumerate(cont_plus2sigma):
    p.SetLineColor(0)
    p.SetFillColor(r.kWhite)
    p.SetFillStyle(1001)
    p.Draw("F SAME")

    #h_exp.Draw("colz")


  for i, p in enumerate(cont_exp):
    p.SetLineColor(r.kBlack)
    p.SetLineWidth(2)
    p.SetLineStyle(2)
    p.SetFillStyle(1001)
    p.SetFillColor(CreateTransparentColor(r.kAzure+6,0.5))
    p.Draw("F SAME")
    p.Draw("L SAME")


  leg.SetHeader('95% CL exclusion limits')
  
  if cont_minus1sigma[0] : leg.AddEntry(cont_minus1sigma[0], "#pm 1#sigma Expected", "F")
  if cont_exp[0] : leg.AddEntry(cont_exp[0],"Expected exclusion", "F")
  if cont_minus2sigma[0] : leg.AddEntry(cont_minus2sigma[0], "#pm 2#sigma Expected", "F")

  # draw dummy hist and multigraph
  # dummyHist.SetMinimum(ybinedges[0])
  # dummyHist.SetMaximum(ybinedges[len(ybinedges)-1])
  # dummyHist.SetLineColor(0)
  # 

  # draw text
  lat.DrawLatex(0.61,0.68,"VBF H #rightarrow invisible")

    
  
  # draw legend
  leg.Draw("same")
  #canv.RedrawAxis()
  
  #r.gPad.GetFrame().Draw()
  r.gPad.RedrawAxis()

  # print canvas
  canv.Update()
  canv.Print('vbflimit.pdf')
  outf.cd()
  canv.SetName("limit_cavas")
  canv.Write()

makePlot()


