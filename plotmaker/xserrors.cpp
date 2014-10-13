double xserrors(string inputfile,double outmass,bool upordown){

  std::vector<double> *inmass = new std::vector<double>();
  std::vector<double> *inxs = new std::vector<double>();
  std::vector<double> *inuperr = new std::vector<double>();
  std::vector<double> *indownerr = new std::vector<double>();
  
  //READ IN INPUT MASS POINT INFO
  std::ifstream inputinfofile( inputfile.c_str());  
  std::string line;
  std::getline(inputinfofile,line);
  while(std::getline(inputinfofile,line)){
    double imass,ixs,iuperr,idownerr;
    std::istringstream iss(line);
    iss >> imass >> ixs >> iuperr >> idownerr;
    inmass->push_back(imass);
    inxs->push_back(ixs);
    inuperr->push_back(iuperr);
    indownerr->push_back(abs(idownerr));
  }
  
  //MAKE TGRAPHS
  TGraph* xs = new TGraph(inmass->size(),&(inmass->at(0)),&(inxs->at(0)));
  TGraph* uperr = new TGraph(inmass->size(),&(inmass->at(0)),&(inuperr->at(0)));
  TGraph* downerr = new TGraph(inmass->size(),&(inmass->at(0)),&(indownerr->at(0)));
  

  //GET VALUES FOR NEW MASS POINTS
  double outerr;
  if(upordown) outerr=uperr->Eval(outmass);
  else outerr=downerr->Eval(outmass);
  //std::cout<<"newxs "<<outxs<<std::endl;
  return outerr;
}

