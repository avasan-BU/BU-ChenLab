/* Author: Anish Vasan
 * Description: Macro to process multiple images in a folder for Dr. Sudong Kim
 * Date: 2023/11/30
 * Version: 1.0
 */
// Batch code definitions
#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".lif") suffix
#@ String(choices={"C1","C2","C3","C4"}, style="radioButtonHorizontal") ref_channel
//Default channels to process. Change value to false if you want default to not process this channel
#@ Boolean (label = "Channels to process: C1", value = true) isC1
#@ Boolean (label = "                     C2", value = true) isC2
#@ Boolean (label = "                     C3", value = true) isC3
#@ Boolean (label = "                     C4", value = true) isC4
#@ Boolean (label = "Close all windows after processing", value = false) isCloseall


//Initiate processFolder function
processFolder(input);


// Function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	cb = newArray(isC1,isC2,isC3,isC4);
	list = getFileList(input);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], ".lif")){
			processFile(input, output, list[i],cb);
			
			// Save all results in a new csv	
			n1=0;
			
			name_result = output + File.separator + File.getNameWithoutExtension(list[i]) + File.separator +"Results_"+n1+".csv";
			//Find new result filename to prevent overwrites
			while(File.exists(name_result)){
				n1=n1+1;
				name_result = output + File.separator + File.getNameWithoutExtension(list[i]) + File.separator +"Results_"+n1+".csv";
			}
			saveAs("Results", name_result);
			
			// Close all images if isCloseall is ticked
			if(isCloseall){
				close("*");
				close("ROI Manager");
				close("Results");
			}
		}
	}
}

// Function to do what you need the code to do
function processFile(input, output, file, channel_bool) {
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
			
			//select reference channel, threshold and create ROI for measurement
			selectImage(ref_channel+"-MAX_"+openlist[i]);
			run("Duplicate...", " ");
			run("Subtract Background...", "rolling=50");
			run("Despeckle");
			setAutoThreshold("Default dark no-reset");
			//run("Threshold...");
			//setThreshold(26, 255);
			setOption("BlackBackground", true);
			run("Convert to Mask");
			run("Create Selection");
			roiManager("Add");
			
			//check if channel was selected to be processed, if true, measure channel properties in ROI
			for (i2 = 0; i2 < channel_bool.length; i2++) {
				if (channel_bool[i2]) {
					selectImage("C"+i2+1+"-MAX_"+openlist[i]);
					roiManager("Select", 0);
					run("Measure");
					setResult("File", nResults-1, openlist[i]);
					setResult("Channel",nResults-1, i2+1);
				}
				
			}
			
			//Save and clear ROI manager
			roiManager("Select", 0);
			File.makeDirectory(output + File.separator + File.getNameWithoutExtension(openlist[i]) + File.separator + "ROIs");
			roiManager("Save", output + File.separator + File.getNameWithoutExtension(openlist[i]) + File.separator + "ROIs"+ File.separator + "ROI_" + openlist[i] + ".zip");
			roiManager("Deselect");
			roiManager("Delete");	
	
		}
	}
}