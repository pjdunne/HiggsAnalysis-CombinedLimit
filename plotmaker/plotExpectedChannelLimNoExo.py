import ROOT as r
import sys
import CMS_lumi
outf = r.TFile('PlotCanvas.root','RECREATE')
def makePlot():

  CMS_lumi.lumi_13TeV = "2.26 fb^{-1}"
  CMS_lumi.writeExtraText = 1
  CMS_lumi.extraText = "Preliminary"
  iPos=33
  
  canv = r.TCanvas()
  canv.Clear()
  canv.SetLogy(False)
  mg = r.TMultiGraph()
  leg = r.TLegend(0.15, 0.55, 0.47, 0.89)
  leg.SetFillColor(0)
  leg.SetBorderSize(0)
  leg.SetTextFont(62)

  dummyHist = r.TH1D("dummy","",3,0,150.15)
  dummyHist.GetXaxis().SetTitle()
  dummyHist.GetYaxis().SetTitle('#sigma x B(H#rightarrow inv)/#sigma(SM)')
  dummyHist.SetTitleSize(.05,"X")
  dummyHist.SetLabelSize(.05,"X")
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

  dir=('../moriond2016invcomb/125/')

  tfvbf = r.TFile(dir+'higgsCombineVBF.Asymptotic.mH125.root')
  tfvh = r.TFile(dir+'higgsCombineVH.Asymptotic.mH125.root')
  tfcomb = r.TFile(dir+'higgsCombineComb.Asymptotic.mH125.root')
  treevbf = tfvbf.Get('limit')
  treevh = tfvh.Get('limit')
  treecomb = tfcomb.Get('limit')
  values=[]

  vbfcenter=75
  vhcenter=125
  combcenter=25

  for i in range(treevbf.GetEntries()):
      treevbf.GetEntry(i)
      values.append([vbfcenter, treevbf.limit])
  for i in range(treevh.GetEntries()):
      treevh.GetEntry(i)
      values.append([vhcenter, treevh.limit])
  for i in range(treecomb.GetEntries()):
      treecomb.GetEntry(i)
      values.append([combcenter, treecomb.limit])

  values.sort(key=lambda x: x[0])
  # make graph from values
  graph = r.TGraphAsymmErrors()
  exp = r.TGraphAsymmErrors()
  oneSigma = r.TGraphAsymmErrors()
  twoSigma = r.TGraphAsymmErrors()

  point_counter=0
  for j in range(len(values)):
    if (j%6==0):
      mh = values[j][0]
      down95 = values[j][1]
      down68 = values[j+1][1]
      median = values[j+2][1]
      up68 = values[j+3][1]
      up95 = values[j+4][1]
      obs = values[j+5][1]

      #FILL XS*BF/XS_SM graph
      #if not (mh==combcenter or mh==vhcenter):
      if(mh==combcenter):
        print obs
      graph.SetPoint(point_counter,mh,obs)
      exp.SetPoint(point_counter,mh,median)
      graph.SetPointError(point_counter,25,25,0,0)
      exp.SetPointError(point_counter,25,25,0,0)
      oneSigma.SetPoint(point_counter,mh,median)
      oneSigma.SetPointError(point_counter,25,25,abs(median-down68),abs(up68-median))
      twoSigma.SetPoint(point_counter,mh,median)
      twoSigma.SetPointError(point_counter,25,25,abs(median-down95),abs(up95-median))

      point_counter+=1
    
  graph.SetMarkerStyle(21)
  graph.SetMarkerSize(0.5)
  graph.SetLineColor(1)
  graph.SetLineWidth(2)
  exp.SetLineColor(1)
  exp.SetLineStyle(2)
  oneSigma.SetLineColor(r.kGreen)
  twoSigma.SetLineColor(r.kYellow)
  oneSigma.SetFillColor(r.kGreen)
  twoSigma.SetFillColor(r.kYellow)
  exp.SetLineColor(1)
  exp.SetLineStyle(2)
  exp.SetLineWidth(2)
  leg.SetHeader('95% CL limits')
  leg.AddEntry(graph,'Observed limit','L')
  leg.AddEntry(exp,'Expected limit','L')
  leg.AddEntry(oneSigma,'Expected limit (1#sigma)','F') 
  leg.AddEntry(twoSigma,'Expected limit (2#sigma)','F')
  
  mg.Add(twoSigma)
  mg.Add(oneSigma)
  mg.Add(exp)
  mg.Add(graph)
  
  # draw dummy hist and multigraph
  mg.Draw("A")
  dummyHist.SetMinimum(mg.GetYaxis().GetXmin())
  dummyHist.SetMaximum(3.6)#mg.GetYaxis().GetXmax())
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
  dummyHist.Draw("AXIS")
  xax = dummyHist.GetXaxis()
  vbf_bin_index = xax.FindBin(vbfcenter)
  vh_bin_index = xax.FindBin(vhcenter)
  comb_bin_index = xax.FindBin(combcenter)
  xax.SetBinLabel(vbf_bin_index,"VBF" )
  xax.SetBinLabel(vh_bin_index,"Z(ll)H" )
  xax.SetBinLabel(comb_bin_index,"Combined" )


  mg.Draw("2")
  mg.Draw("P")
  dummyHist.Draw("AXIGSAME")
 
  # draw line at y=1 
  l = r.TLine(0.,1.,200.,1.)
  l.SetLineColor(r.kBlue)
  l.SetLineWidth(2)
  l.Draw()

  # draw text
  #lat.DrawLatex(0.52,0.85,"CMS VBF H #rightarrow invisible")
  #lat.DrawLatex(0.52,0.78,"#sqrt{s} = 8 TeV, L = 19.2 fb^{-1}")
  #lat.DrawLatex(0.61,0.68,"VBF H #rightarrow invisible")

  CMS_lumi.CMS_lumi(canv, 4, iPos)
    
  
  # draw legend
  leg.Draw()
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  canv.Print('channellimit.pdf')
  outf.cd()
  canv.SetName("limit_cavas")
  canv.Write()

makePlot()
