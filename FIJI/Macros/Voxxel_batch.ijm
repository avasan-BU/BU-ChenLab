list = getList("image.titles");
//selectWindow("11A");
//run("Split Channels");

// rename windows based on order open - workaround for inconsistent
// naming conventions

for (i=0; i<list.length; i++){
 
 if(list[i]=="11A"){
 	i++;
 	if(i>list.length){
 		exit("end of script");
 	}
 }
 selectWindow(list[i]);
 print(list[i]);
 run("Split Channels");
	print("split");
 run("Flat Field Correction (2D/3D)", "originalimageplus=C2-"+list[i]+" flatfieldimageplus=C2-11A darkfieldimagename=None");
saveAs("Tiff", "C2-"+list[i]);
 run("Flat Field Correction (2D/3D)", "originalimageplus=C3-"+list[i]+" flatfieldimageplus=C3-11A darkfieldimagename=None");
saveAs("Tiff", "C3-"+list[i]);
// Max projection!
//run("Z Project...", "projection=[Max Intensity]");
//Stack.setChannel(3);
//run("cb bluishgreen");\
//Stack.setChannel(4);
//run("Enhance Contrast", "saturated=.05");
//Stack.setChannel(2);
//run("Enhance Contrast", "saturated=.05");
// c1: red, c2: green, c3: blue, c4: grey, c5: cyan, c6: mag, c7: yellow
 selectWindow("C1-"+list[i]);
//run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None*");
//run("Merge Channels...", " c1=C3-"+list[i] +" c3=C1-"+list[i] +" c5=C2-"+list[i] +  " create");
//saveAs("Tiff", list[i]);
//run("Sharpen", "stack");
//saveAs("Tiff", list[i]+"-sharp");
}