double xs(string inputfile,double outmass){

  std::vector<double> *inmass = new std::vector<double>();
  std::vector<double> *inxs = new std::vector<double>();
  
  //READ IN INPUT MASS POINT INFO
  std::ifstream inputinfofile( inputfile.c_str());  
  std::string line;
  std::getline(inputinfofile,line);
  while(std::getline(inputinfofile,line)){
    double imass,ixs;
    std::istringstream iss(line);
    iss >> imass >> ixs;
    inmass->push_back(imass);
    inxs->push_back(ixs);
  }
  
  //MAKE TGRAPHS
  TGraph* xs = new TGraph(inmass->size(),&(inmass->at(0)),&(inxs->at(0)));
  
  //GET VALUES FOR NEW MASS POINTS
  double outxs = xs->Eval(outmass);
  //std::cout<<"newxs "<<outxs<<std::endl;
  return outxs;
}

