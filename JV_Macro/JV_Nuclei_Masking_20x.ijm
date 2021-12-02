//Run enhance contrast+Substract background
run("Subtract Background...", "rolling=50 stack");
run("Enhance Contrast...", "saturated=0.3 normalize process_all");
run("Gaussian Blur...", "sigma=5 stack");
//Findmaxima for stack
  tolerance = 40;
  type = "Single Points";
  exclude = false;
  light = false;
  options = "";
  if (exclude) options = options + " exclude";
  if (light) options = options + " light";
  setBatchMode(true);
  input = getImageID();
  n = nSlices();
  for (i=1; i<=n; i++) {
     showProgress(i, n);
     selectImage(input);
     setSlice(i);
     run("Find Maxima...", "noise="+ tolerance +" output=["+type+"]"+options);
     if (i==1)
        output = getImageID();
    else if (type!="Count") {
       run("Select All");
       run("Copy");
       close();
       selectImage(output);
       run("Add Slice");
       run("Paste");
    }
  }
  run("Select None");
  setBatchMode(false);

 for (j=1; j<7 ; j++){
run("Dilate", "stack");
  }

