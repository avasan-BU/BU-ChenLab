// This code converts timelapses into videos and saves them
// Open all the timelapse stacks you want to convert

//check for open images 
  if (nImages==0)
     exit("No images are open");

// Choose save location
  dir = getDirectory("Choose a Directory");

// Process timelapses
  for (n=1; n<=nImages; n++) {
     selectImage(n);
     title = getMetadata("Stage "+n);
     title1 = substring(title,lengthOf(title)-3,lengthOf(title)-1);
     print(title1+" Saved");
     saveAs("avi", dir+title1.replace("/","_"));
     //print("label:"+title[(lengthOf(title)-4):lengthOf(title)]);
  } 

// close all windows
  close("*");
