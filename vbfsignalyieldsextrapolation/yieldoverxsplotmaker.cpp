{

  Double_t inmass[6]={110,125,150,200,300,400};
  Double_t inyields[6]={213.95,209.453,197.105,148.524,96.1604,69.2748};
  Double_t inxs[6]={1.809,1.578,1.280,0.8685,0.4408,0.2543};
  Double_t xerrup[6]={0,0,0,0,0,0};
  Double_t xerrdown[6]={0,0,0,0,0,0};
  Double_t inyieldoverxs[6];
  for(int i=0;i<6;i++){
    inyieldoverxs[i]=inyields[i]/inxs[i];
    std::cout<<inyieldoverxs[i]<<std::endl;
  }

  Double_t yerrsdown[6][6]={{0.026,0.077,0.0004,0.006,0.041,0.04},{0.026,0.121,0.0337,0.007,0.046,0.04},{0.026,0.094,0.019,0.005,0.043,0.04},{0.026,0.111,0.026,0.007,0.047,0.04},{0.026,0.081,0.023,0.009,0.054,0.04},{0.026,0.11,0.035,0.0009,0.055,0.04}};

  Double_t yerrsup[6][6]={{0.026,0.109,0.034,0.004,0.041,0.04},{0.026,0.096,0.024,0.004,0.046,0.04},{0.026,0.083,0.019,0.002,0.043,0.04},{0.026,0.121,0.02,0.0006,0.047,0.04},{0.026,0.053,0.004,0.004,0.054,0.04},{0.026,0.1,0.024,0.004,0.055,0.04}};

  Double_t yerrup[6];
  Double_t yerrdown[6];
  
  Double_t squaredyerrup[6];
  Double_t squaredyerrdown[6];

  for(int i=0;i<6;i++){
    for(int j=0;j<6;j++){
      squaredyerrup[i]+=yerrsup[i][j]*yerrsup[i][j];
      squaredyerrdown[i]+=yerrsdown[i][j]*yerrsdown[i][j];
    }
    yerrup[i]=sqrt(squaredyerrup[i])*inyieldoverxs[i];
    yerrdown[i]=sqrt(squaredyerrdown[i])*inyieldoverxs[i];
    std::cout<<yerrup[i]<<" "<<yerrdown[i]<<std::endl;
  }

  TGraphAsymmErrors* yieldoverxs = new TGraphAsymmErrors(6,inmass,inyieldoverxs,xerrup,xerrdown,yerrup,yerrdown);

  //MAKE PLOTS                                                                                                                                               
  TCanvas c1;
  yieldoverxs->SetTitle("Yield/XS");
  yieldoverxs->GetXaxis()->SetTitle("Mass [GeV]");
  yieldoverxs->GetYaxis()->SetTitle("(Yield/XS) [pb^{-1}]");
  yieldoverxs->SetMarkerColor(4);
  yieldoverxs->SetMarkerStyle(21);
  yieldoverxs->Draw("ALP");
  
  c1->SaveAs("yieldoverxs.pdf");

} 
