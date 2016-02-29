import ROOT as r
import sys
import CMS_lumi
outf = r.TFile('PlotCanvas.root','RECREATE')
def makePlot():

  # CMS_lumi.lumi_8TeV = "19.2 fb^{-1}"
  # CMS_lumi.writeExtraText = 1
  # CMS_lumi.extraText = "Preliminary"
  ipos=33
  
  canv = r.TCanvas()
  canv.Clear()
  canv.SetLogy(False)
  canv.SetLogx(True)
  mg = r.TMultiGraph()
  leg = r.TLegend(0.15, 0.55, 0.52, 0.89)
  leg.SetFillColor(0)
  leg.SetBorderSize(0)
  leg.SetTextFont(62)

  dummyHist = r.TH1D("dummy","",1,2,3000)
  dummyHist.GetXaxis().SetTitle('L [fb^{-1}]')
  dummyHist.GetYaxis().SetTitle('#sigma x B(H_{125}#rightarrow inv)/#sigma_{VBF}(SM)')
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

  

  tf = r.TFile(sys.argv[1])
  tfscale = r.TFile(sys.argv[2])
  tree = tf.Get('limit')
  treescale = tfscale.Get('limit')
  values=[]
  valuesscale=[]
  for i in range(tree.GetEntries()):
      tree.GetEntry(i)
      values.append([tree.mh, tree.limit])
  values.sort(key=lambda x: x[0])
  # make graph from values
  graph = r.TGraphAsymmErrors()
  exp = r.TGraphAsymmErrors()
  oneSigma = r.TGraphAsymmErrors()
  twoSigma = r.TGraphAsymmErrors()

  for i in range(treescale.GetEntries()):
      treescale.GetEntry(i)
      valuesscale.append([treescale.mh, treescale.limit])
  valuesscale.sort(key=lambda x: x[0])
  # make graph from values
  graphscale = r.TGraphAsymmErrors()
  expscale = r.TGraphAsymmErrors()
  oneSigmascale = r.TGraphAsymmErrors()
  twoSigmascale = r.TGraphAsymmErrors()

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
      graph.SetPoint(point_counter,mh,obs)
      exp.SetPoint(point_counter,mh,median)
      oneSigma.SetPoint(point_counter,mh,median)
      oneSigma.SetPointError(point_counter,0,0,abs(median-down68),abs(up68-median))
      twoSigma.SetPoint(point_counter,mh,median)
      twoSigma.SetPointError(point_counter,0,0,abs(median-down95),abs(up95-median))

      point_counter+=1

  point_counter=0
  for j in range(len(valuesscale)):
    if (j%6==0):
      mh = valuesscale[j][0]
      down95 = valuesscale[j][1]
      down68 = valuesscale[j+1][1]
      median = valuesscale[j+2][1]
      up68 = valuesscale[j+3][1]
      up95 = valuesscale[j+4][1]
      obs = valuesscale[j+5][1]

      #FILL XS*BF/XS_SM graph
      graphscale.SetPoint(point_counter,mh,obs)
      expscale.SetPoint(point_counter,mh,median)
      oneSigmascale.SetPoint(point_counter,mh,median)
      oneSigmascale.SetPointError(point_counter,0,0,abs(median-down68),abs(up68-median))
      twoSigmascale.SetPoint(point_counter,mh,median)
      twoSigmascale.SetPointError(point_counter,0,0,abs(median-down95),abs(up95-median))

      point_counter+=1
    
  graph.SetMarkerStyle(21)
  graph.SetMarkerSize(0.5)
  graph.SetLineColor(1)
  graph.SetLineWidth(2)
  exp.SetLineColor(2)
  exp.SetLineStyle(1)

  expscale.SetLineColor(4)
  expscale.SetLineStyle(1)

  oneSigma.SetLineColor(r.kGreen)
  twoSigma.SetLineColor(r.kYellow)
  oneSigma.SetFillColor(r.kGreen)
  twoSigma.SetFillColor(r.kYellow)
  exp.SetLineColor(2)
  exp.SetLineStyle(1)
  exp.SetLineWidth(3)

  expscale.SetLineColor(4)
  expscale.SetLineStyle(2)
  expscale.SetLineWidth(3)
#  leg.SetHeader('95% CL limits')
#  leg.AddEntry(graph,'Observed limit','L')
  leg.AddEntry(exp,'Constant syst expected limit','L')
  leg.AddEntry(expscale,'#sqrt{L} syst expected limit','L')
#  leg.AddEntry(oneSigma,'Expected limit (1#sigma)','F') 
#  leg.AddEntry(twoSigma,'Expected limit (2#sigma)','F')
  
#  mg.Add(twoSigma)
#  mg.Add(oneSigma)
  mg.Add(exp)
  mg.Add(expscale)
#  mg.Add(graph)
  
  # draw dummy hist and multigraph
  mg.Draw("A")
  dummyHist.SetMinimum(mg.GetYaxis().GetXmin())
  dummyHist.SetMaximum(1.4)#mg.GetYaxis().GetXmax())
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
  dummyHist.Draw("AXIS")
  mg.Draw("3")
  mg.Draw("LPX")
  dummyHist.Draw("AXIGSAME")
 
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
  leg.Draw()
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  canv.Print('vbflimit.pdf')
  outf.cd()
  canv.SetName("limit_cavas")
  canv.Write()

makePlot()
