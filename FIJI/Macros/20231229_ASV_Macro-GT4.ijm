/* Author: Anish Vasan
 * Description: Macro to label ground truth
 * Date: 2023/12/31
 * Version: 1.0
 */
// Batch code definitions
#@ File (label = "Input directory", style = "directory") input

//Initiate processFolder function
processFolder(input);


// Function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	list = getFileList(input);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
			//print("Processing sub");
		if(endsWith(list[i], ".tif")){
			//print("processing tif file");
			processFile(input, list[i]);	
			}
	}
}

function processFile(input, file) {
	
	//print(input+file);
	open(input + file);
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
		save(input+file);
	}
	
	setTool("polygon");
	message = "Finish highlighting wound area for all time points, then click \"OK\".";
	waitForUser("Finish highlighting wound area for all time points, then click \"OK\".", "\n Ensure that all fill operations are completed in Channel 1 \n Use the polygon selection tool to outline the wound area and then press \"F\" to fill in the highlighted area \n To reset an area that was filled: Select all pixels (Ctrl+A or Cmd+A), and press \"Delete\"");
	//waitForUser("Waiting for input", message);
	save(input+file);
	close();	
	
}
