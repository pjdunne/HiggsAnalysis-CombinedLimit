import ROOT as r
import sys
import CMS_lumi
outf = r.TFile('PlotCanvas.root','RECREATE')
blind=False
def makePlot():

  CMS_lumi.lumi_13TeV = "2.09 fb^{-1}"
  CMS_lumi.writeExtraText = 1
  CMS_lumi.extraText = "Preliminary"
  iPos=33
  
  canv = r.TCanvas()
  canv.Clear()
  canv.SetLogy(False)
  mg = r.TMultiGraph()
  leg = r.TLegend(0.15, 0.55, 0.52, 0.89)
  leg.SetFillColor(0)
  leg.SetBorderSize(0)
  leg.SetTextFont(62)

  dummyHist = r.TH1D("dummy","",1,100,510)
  dummyHist.GetXaxis().SetTitle('m_{H} [GeV]')
  dummyHist.GetYaxis().SetTitle('#sigma x B(H#rightarrow inv)/#sigma_{VBF}(SM)')
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
  print values#!!
  for j in range(len(values)):
      #FILL XS*BF/XS_SM graph
      if(blind==True):
        if (j%5==0):
          mh = values[j][0]
          down95 = values[j][1]
          down68 = values[j+1][1]
          median = values[j+2][1]
          up68 = values[j+3][1]
          up95 = values[j+4][1]
          exp.SetPoint(point_counter,mh,median)
          oneSigma.SetPoint(point_counter,mh,median)
          oneSigma.SetPointError(point_counter,0,0,abs(median-down68),abs(up68-median))
          twoSigma.SetPoint(point_counter,mh,median)
          twoSigma.SetPointError(point_counter,0,0,abs(median-down95),abs(up95-median))
          point_counter+=1
          print "New mass:"
          print mh
          print down95
          print down68
          print median
          print up68
          print up95

      else:
        if (j%6==0):
          mh = values[j][0]
          down95 = values[j][1]
          down68 = values[j+1][1]
          median = values[j+2][1]
          up68 = values[j+3][1]
          up95 = values[j+4][1]
          obs = values[j+5][1]

          graph.SetPoint(point_counter,mh,obs)
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
  if(blind!=True):
    leg.AddEntry(graph,'Observed limit','L')
  leg.AddEntry(exp,'Expected limit','L')
  leg.AddEntry(oneSigma,'Expected limit (1#sigma)','F') 
  leg.AddEntry(twoSigma,'Expected limit (2#sigma)','F')
  
  mg.Add(twoSigma)
  mg.Add(oneSigma)
  mg.Add(exp)
  if(blind!=True):
    mg.Add(graph)
  
  # draw dummy hist and multigraph
  mg.Draw("A")
  dummyHist.SetMinimum(mg.GetYaxis().GetXmin())
  dummyHist.SetMaximum(7)#mg.GetYaxis().GetXmax())
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
  dummyHist.Draw("AXIS")
  mg.Draw("3")
  mg.Draw("LPX")
  dummyHist.Draw("AXIGSAME")
 
  # draw line at y=1 
  l = r.TLine(110.,1.,500.,1.)
  l.SetLineColor(r.kBlue)
  l.SetLineWidth(2)
  l.Draw()

  # draw text
  #lat.DrawLatex(0.52,0.85,"CMS VBF H #rightarrow invisible")
  #lat.DrawLatex(0.52,0.78,"#sqrt{s} = 8 TeV, L = 19.2 fb^{-1}")
  lat.DrawLatex(0.61,0.68,"VBF H #rightarrow invisible")

  CMS_lumi.CMS_lumi(canv, 4, iPos)
    
  
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
