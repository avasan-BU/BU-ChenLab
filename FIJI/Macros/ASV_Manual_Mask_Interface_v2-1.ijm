/* Author: Anish Vasan
 * Description: Macro to label ground truth
 * Date: 2024/03/19
 * Version: 2.1
 */
// Batch code definitions
#@ File (label = "Input directory", style = "directory") input
#@ Boolean (label = "Convert images to stack?", value = true) isim2stack

output = input + File.separator + "Stacks";
//Rearrange stacks
if(isim2stack){
	Dialog.create("Fill experiment parameters");
	Dialog.addDirectory("Output directory", output);
	Dialog.addString(".nd filename", "tissue_ai");
	Dialog.addMessage("Stage postions: s = first position , S = last position");
	Dialog.addNumber( "s = ", 1);
	Dialog.addNumber( "S = ", 96);
	Dialog.addMessage("Time points: t = first time point , T = last time point");
	Dialog.addNumber( "t = ", 1);
	Dialog.addNumber( "T = ", 48);
	Dialog.addNumber( "Time interval (number of frames to skip)", 4);
	Dialog.show();
	
	output = Dialog.getString();
	basename = Dialog.getString();
	s_in = Dialog.getNumber();
	S_in = Dialog.getNumber();
	t_in = Dialog.getNumber();
	T_in = Dialog.getNumber();
	t_skip = Dialog.getNumber();
	
	if(File.isDirectory(output)){
	}
	else {
		File.makeDirectory(output);
	}
	im2stack(s_in,S_in,t_skip,input,output,basename);
	processFolder(output);
}
else {
	processFolder(input);
}
//ProcessFolder



// Function to scan folders/subfolders/files to find files with correct suffix

function im2stack(s_in,S_in,t_skip,input,output,basename){
	for (s=s_in; s<=S_in; s++) {
		for (t=t_in; t<=T_in;t=t+t_skip) {
			filename = input+ File.separator + basename+"_s"+s+"_t"+t+".tif";
			open(filename);	
		}
		name = "s"+ String.pad(s, 2);
		run("Images to Stack", "name=name title=[]");
		saveAs("tiff", output+ File.separator + name);
		close();
}
}

function processFolder(location) {
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
	open(location + file);
	Stack.getDimensions(width, height, channels, slices, frames);
	if(channels<2){
		fname = split(file,".");
		run("Duplicate...", "duplicate");
		selectWindow(fname[0]+"-1.tif");
		run("Select All");
		run("Clear", "stack");
		run("Merge Channels...", "c4="+file+" c7="+fname[0]+"-1.tif create");
		selectWindow("Composite");
		run("Arrange Channels...", "new=21");
		saveAs("tiff",location+file);
	}
	Stack.setChannel(1);
	setTool("polygon");
	message = "Finish highlighting wound area for all time points, then click \"OK\".";
	waitForUser("Finish highlighting wound area for all time points, then click \"OK\".", "\n Ensure that all fill operations are completed in Channel 1 \n Use the polygon selection tool to outline the wound area and then press \"F\" to fill in the highlighted area \n To reset an area that was filled: Select all pixels (Ctrl+A or Cmd+A), and press \"Delete\"");
	//waitForUser("Waiting for input", message);
	saveAs(location+file);
	close();	
	
}
