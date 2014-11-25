import ROOT as r
import sys
outf = r.TFile('PlotCanvas.root','RECREATE')
def makePlot():
  canv = r.TCanvas()
  canv.Clear()
  canv.SetLogy(False)
  mg = r.TMultiGraph()
  leg = r.TLegend(0.5,0.55,0.89,0.89)
  leg.SetFillColor(0)
  leg.SetBorderSize(0)

  dummyHist = r.TH1D("dummy","",1,104,146)
  dummyHist.GetXaxis().SetTitle('m_{H} [GeV]')
  dummyHist.GetYaxis().SetTitle('#sigma x B(H#rightarrow inv)/#sigma_{ZH}(SM)')
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
  tree = tf.Get('limit')
  values=[]
  for i in range(tree.GetEntries()):
      tree.GetEntry(i)
      values.append([tree.mh, tree.limit])
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
      graph.SetPoint(point_counter,mh,obs)
      exp.SetPoint(point_counter,mh,median)
      oneSigma.SetPoint(point_counter,mh,median)
      oneSigma.SetPointError(point_counter,0,0,abs(median-down68),abs(up68-median))
      twoSigma.SetPoint(point_counter,mh,median)
      twoSigma.SetPointError(point_counter,0,0,abs(median-down95),abs(up95-median))

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
  dummyHist.SetMinimum(0.2)
  dummyHist.SetMaximum(3.0)
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
  dummyHist.Draw("AXIS")
  mg.Draw("3")
  mg.Draw("LPX")
  dummyHist.Draw("AXIGSAME")
 
  # draw line at y=1 
  l = r.TLine(104.,1.,146.,1.)
  l.SetLineColor(r.kBlue)
  l.SetLineWidth(2)
  l.Draw()

  # draw text
  lat.DrawLatex(0.14,0.85,"CMS")
  lat.DrawLatex(0.14,0.78,"Combination of Z(b#bar{b})H")
  lat.DrawLatex(0.14,0.73,"and Z(ll)H, H #rightarrow invisible")

  
  lat2.DrawLatex(0.14,0.665,"#sqrt{s} = 8 TeV (Both ZH channels)")
  lat2.DrawLatex(0.14,0.62,"L = 18.9-19.7 fb^{-1}")

  lat2.DrawLatex(0.14,0.555,"#sqrt{s} = 7 TeV (Z(ll)H only)")
  lat2.DrawLatex(0.14,0.515,"L = 4.9 fb^{-1}")

    
  
  # draw legend
  leg.Draw()
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  canv.Print('zhlimit.pdf')
  outf.cd()
  canv.SetName("limit_cavas")
  canv.Write()

makePlot()