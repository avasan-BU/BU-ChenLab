setOption(“ScaleConversions”, true);
run(“8-bit”);
percentVal = 96; 
nBins = 256; 
resetMinAndMax(); 
getHistogram(values, counts, nBins); 
// find culmulative sum 
nPixels = 0; 
percentage = newArray(counts.length); 
for (i = 0; i<counts.length; i++){ 
 nPixels += counts[i]; 
 nForgroundPixels = nPixels - counts[255]; 
 } 
for (i = 0; i<255; i++){ 
  sum = sum + counts[i]; 
  percentage[i] = sum*100/nForgroundPixels; 
  if (percentage[i] > percentVal) { 
    idealT = i; 
    i = 999999; 
  } 
} 
print(“T is: ” + idealT); 
setThreshold(idealT, 255)
run(“Convert to Mask”);
run(“Analyze Particles...“, “size=5-Infinity show=Outlines clear summarize”);
close();
close();