import ROOT as r
import sys
import subprocess
import CMS_lumi
outf = r.TFile('PlotCanvas.root','RECREATE')
def makePlot():

  CMS_lumi.lumi_8TeV = "19.2 fb^{-1}"
  CMS_lumi.writeExtraText = 1
  CMS_lumi.extraText = "Preliminary"
  iPos=11

  canv = r.TCanvas()
  canv.Clear()
  canv.SetLogy(False)
  mg = r.TMultiGraph()
  leg = r.TLegend(0.5, 0.49, 0.87, 0.89)
  leg.SetFillColor(0)
  leg.SetBorderSize(0)
  leg.SetTextFont(62)

  dummyHist = r.TH1D("dummy","",1,100,410)
  dummyHist.GetXaxis().SetTitle('m_{H} [GeV]')
  dummyHist.GetYaxis().SetTitle('#sigma x B(H#rightarrow inv) [pb]')
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
  graphxs = r.TGraphAsymmErrors()
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

      #FILL XS*BF graph
      #!!NEED TO MULTIPLY BY XS_SM
      command="root"
      args1="-l"
      args2="-q"
      args3="-b"
      args4="xs.cpp(\"vbfxsinfo.txt\","+repr(mh)+")"
      args5="xserrors.cpp(\"vbfxsinfowitherrors.txt\","+repr(mh)+",true)"
      args6="xserrors.cpp(\"vbfxsinfowitherrors.txt\","+repr(mh)+",false)"
      cmd=subprocess.Popen([command,args1,args2,args3,args4],stdout=subprocess.PIPE)
      for line in cmd.stdout:
        if "double" in line:
          xs=float(line[8:])
      cmd2=subprocess.Popen([command,args1,args2,args3,args5],stdout=subprocess.PIPE)
      for line in cmd2.stdout:
        if "double" in line:
          uperr=float(line[8:])
      cmd3=subprocess.Popen([command,args1,args2,args3,args6],stdout=subprocess.PIPE)
      for line in cmd3.stdout:
        if "double" in line:
          downerr=float(line[8:])
          
      graphxs.SetPoint(point_counter,mh,xs)
      graphxs.SetPointError(point_counter,0,0,abs(downerr*0.01*xs),abs(uperr*0.01*xs))
      graph.SetPoint(point_counter,mh,obs*xs)
      exp.SetPoint(point_counter,mh,median*xs)
      oneSigma.SetPoint(point_counter,mh,median*xs)
      oneSigma.SetPointError(point_counter,0,0,abs(median-down68)*xs,abs(up68-median)*xs)
      twoSigma.SetPoint(point_counter,mh,median*xs)
      twoSigma.SetPointError(point_counter,0,0,abs(median-down95)*xs,abs(up95-median)*xs)

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
  graphxs.SetLineColor(r.kBlue)
  graphxs.SetLineWidth(1)
  graphxs.SetMarkerSize(0.)
  graphxs.SetFillStyle(3254)
  graphxs.SetFillColor(r.kRed)
  exp.SetLineColor(1)
  exp.SetLineStyle(2)
  exp.SetLineWidth(2)
  leg.SetHeader('95% CL limits')
  leg.AddEntry(graph,'Observed limit','L')
  leg.AddEntry(exp,'Expected limit','L')
  leg.AddEntry(oneSigma,'Expected limit (1#sigma)','f') 
  leg.AddEntry(twoSigma,'Expected limit (2#sigma)','f')
  leg.AddEntry(graphxs,'#sigma_{VBF} (SM)','Lf')
  
  
  mg.Add(twoSigma)
  mg.Add(oneSigma)
  mg.Add(exp)
  mg.Add(graph)
  mg.Add(graphxs)
  
  # draw dummy hist and multigraph
  mg.Draw("A")
  dummyHist.SetMinimum(0.)
  dummyHist.SetMaximum(2.5)
  #dummyHist.SetMinimum(mg.GetYaxis().GetXmin())
  #dummyHist.SetMaximum(mg.GetYaxis().GetXmax())
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
  dummyHist.Draw("AXIS")
  mg.Draw("3")
  mg.Draw("LPX")
  dummyHist.Draw("AXIGSAME")
 
  # draw line at y=1 only for /xs_SM plot
  #l = r.TLine(100.,1.,400.,1.)
  #l.SetLineColor(r.kRed)
  #l.SetLineWidth(2)
  #l.Draw()

  CMS_lumi.CMS_lumi(canv, 2, iPos)

  # draw text
  #lat.DrawLatex(0.14,0.85,"CMS VBF H #rightarrow invisible")
  #lat.DrawLatex(0.14,0.78,"#sqrt{s} = 8 TeV, L = 19.2 fb^{-1}")
  lat.DrawLatex(0.14,0.68,"VBF H #rightarrow invisible")
    
  
  # draw legend
  leg.Draw()
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  canv.Print('vbfxslimit.pdf')
  outf.cd()
  canv.SetName("limit_cavas")
  canv.Write()

makePlot()
