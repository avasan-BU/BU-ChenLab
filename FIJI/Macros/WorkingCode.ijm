

list = getList("image.titles");
for (i=0; i<list.length; i++){
 selectWindow(list[i]);
 
//selectWindow(list[i]);
//makeRectangle(333, 81, 520, 726); //480 um x 670 um ROI
//run("Duplicate...", "duplicate");
//saveAs("Tiff");

run("Split Channels");

selectWindow("C1-"+list[i]);
run("Z Project...", "projection=[Max Intensity]");
run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None*");
//rename("SUM_C1-"+list[i]);
saveAs("Tiff", "E:/Spinning Disc/20220618_NHDFneo_SA-B-Gal-p21_MT/Cropped/Max_Channels/MAX_C1-"+list[i]);


selectWindow("C2-"+list[i]);
//run("Duplicate...", "title=C21-"+list[i]+" use");
//imageCalculator("Subtract create stack", "C2-"+list[i],"C21-"+list[i]);
run("Z Project...", "projection=[Max Intensity]");
saveAs("Tiff", "E:/Spinning Disc/20220618_NHDFneo_SA-B-Gal-p21_MT/Cropped/Max_Channels/MAX_C2-"+list[i]);
//rename("SUM_C2-"+list[i]);
//saveAs("Tiff", "E:/Spinning Disc/20220926_NHDFneo-Ad-HCF-ECMs/10X LO/BG-corr/SUM_C2-"+list[i]);

selectWindow("C3-"+list[i]);
run("Z Project...", "projection=[Max Intensity]");
saveAs("Tiff", "E:/Spinning Disc/20220618_NHDFneo_SA-B-Gal-p21_MT/Cropped/Max_Channels/MAX_C3-"+list[i]);
// green, blue, magenta
//run("Merge Channels...", "c2=MAX_C2-"+ list[i] +" c3=MAX_C1-"+list[i] +" c6=MAX_C3-"+list[i] +" create");
//saveAs("Tiff", "E:/Spinning Disc/20220618_NHDFneo_SA-B-Gal-p21_MT/Cropped/Max/MAX_"+list[i]);
//selectWindow(list[i]);
//makeRectangle(333, 81, 520, 726); //480 um x 670 um ROI
//run("Duplicate...", "duplicate");
//saveAs("Tiff");
//imageCalculator("Subtract create stack", list[i],list[i]+"-1");
//run("Z Project...", "projection=[Sum Slices]");
//saveAs("Tiff", "F:\\Microscope Images\\Spinning Disc\\20221003_NHDFneo-Ad-HCF_ECMs_Edited\\Sum Slices\\Voxxel_Corrected\\ROI\\SUM_"+list[i]);
//saveAS("Tiff");

}