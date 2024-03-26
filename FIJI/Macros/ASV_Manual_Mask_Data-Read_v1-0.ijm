/* Author: Anish Vasan
 * Description: Macro to measure labeled ground truth
 * Date: 2024/03/24
 * Version: 1.0
 */
 
 // Batch code definitions
#@ File (label = "Input directory", style = "directory") input


processFolder(input);


function processFolder(location) {
	run("Set Measurements...", "area limit redirect=None decimal=3");
	list = getFileList(location);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(location + File.separator + list[i])) {
			processFolder(location + File.separator + list[i]);
		}
		
		if(endsWith(list[i], ".tif")){
			//print("processing tif file");
			processFile(location, list[i]);	
		}
	}
}

function processFile(location, file) {
	
	//print(input+file);
	open(location + File.separator + file);
	
	fname = split(file,".");
	Stack.getDimensions(width, height, channels, slices, frames);
	
	if(channels==2){
		Stack.getDimensions(width, height, channels, slices, frames);
		run("Duplicate...", "duplicate channels=1");
		setAutoThreshold("Default dark no-reset");
		//run("Threshold...");
		run("Select All");
		for(n1 = 1; n1 <= slices; n1++) {
			selectWindow(fname[0]+"-1.tif");
			Stack.setSlice(n1);
			run("Measure");
		}
	selectWindow("Results");	
	saveAs("Results", location + File.separator + "Results" + File.separator + fname[0] + ".csv");
	close("*");
	run("Clear Results");
	}
	else{
		Print("Incorrect input file format");
	}
}