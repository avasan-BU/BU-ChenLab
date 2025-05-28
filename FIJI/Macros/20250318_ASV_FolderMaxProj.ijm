/* Author: Anish Vasan
 * Description: Macro to process MAX projections of multiple images in a folder
 * Date: 2025/03/18
 * Version: 1.1
 */
// Batch code definitions
#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".tif") suffix
#@ Boolean (label = "Close all windows after processing", value = false) isCloseall


//Initiate processFolder function
processFolder(input);


// Function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	list = getFileList(input);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], suffix)){
			processFile(input, output, list[i]);
			
			if(isCloseall){
				close("*");
			}
		}
	}
}

// Function to do what you need the code to do
function processFile(input, output, file) {
	//Import all series in the .lif file
	if(endsWith(input, "/")){
		run("Bio-Formats Importer", "open=["+input+file+"] open_all_series color_mode=Default view=Hyperstack stack_order=XYCZT");	
	}

	else {
		run("Bio-Formats Importer", "open=["+input+File.separator+file+"] open_all_series color_mode=Default view=Hyperstack stack_order=XYCZT");	
	}
	
	//Make subdirectory for output
	File.makeDirectory(output + File.separator + File.getNameWithoutExtension(file));
	
	//Populate list of open windows
	openlist = getList("image.titles");
	openlist = Array.sort(openlist);
	//confirm window selected is most recently opened file
	for (i=0; i<openlist.length; i++){
		selectWindow(openlist[i]);
		
		//get stack dimensions
		Stack.getDimensions(width, height, channels, slices, frames);
		
		//only process files with multiple channels and slices
		if (channels > 1 && slices > 1) {
			
			//Get max intensity projection of image
			run("Z Project...", "projection=[Max Intensity]");
			
			//Split channels
			run("Split Channels");
			for (c1=0; c1<channels; c1++){
				run("Save");
				close();
			}
			}
			

	
		}
	
}