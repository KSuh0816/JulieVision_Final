//Convert images to 8bit
run("8-bit");
//Run enhance contrast+Substract background
run("Enhance Contrast...", "saturated=0.3 normalize process_all");
run("Subtract Background...", "rolling=50 stack");

//Findmaxima for stack
  tolerance = 10;
  type = "Segmented Particles";
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

 