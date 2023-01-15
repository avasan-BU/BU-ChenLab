list = getList("image.titles");
for (i=0; i<list.length/3; i++){
	selectWindow(list[i]);
	print(list[i]);
	run("Merge Channels...", " c1="+list[i] +" c2=C2-"+ substring(list[i],3,lengthOf(list[i]))+ " c3=C3-"+substring(list[i],3,lengthOf(list[i]))+  " create");
	run("Make Composite");
	Stack.setChannel(1);
	run("cb blue");
	Stack.setChannel(2);
	run("cb orange");
	Stack.setChannel(3);
	run("cb reddishpurple");
	//Stack.setChannel(4);
	//run("cb yellow");
	//run("Split Channels");	
	//selectWindow("C1-"+list[i]);
	//run("Despeckle");
	//run("Subtract Background...", "rolling=50 sliding");
	//run("Despeckle");
	//run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None*");
	//run("Sharpen");
	//saveAs("Tiff", "C:\\Users\\anish\\Desktop\\Stacks\\Stacked\\CROPPED\\Voxxeled\\For Poster\\C3-"+substring(list[i],0,lengthOf(list[i])-9));
	//selectWindow("C3-"+list[i]);
	saveAs("Tiff", "C:\\Users\\anish\\Desktop\\Stacks\\Stacked\\CROPPED\\Voxxeled\\For Poster\\Composite\\"+substring(list[i],3,lengthOf(list[i])));
	
}