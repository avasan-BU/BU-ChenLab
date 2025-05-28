/* Author: Anish Vasan
 * Description: Macro to label ground truth
 * Date: 2024/05/23
 * Version: 2.6
 */
// Batch code definitions
#@ File (label = "Input directory", style = "directory") input
#@ Boolean (label = "Convert images to stack?", value = true) isim2stack



output = input + File.separator + "Stacks";
//Rearrange stacks
if(isim2stack){
	
	//Dialog box paramters and creation
	Dialog.create("Fill experiment parameters");
	Dialog.addDirectory("Output directory", output);
	Dialog.addNumber( "Time interval (number of frames to skip)", 4);
	Dialog.show();
	
	output = Dialog.getString();
	t_skip = Dialog.getNumber();


	if(File.isDirectory(output)){
	}
	else {
		File.makeDirectory(output);
		File.makeDirectory(output+File.separator+"Completed");
		File.makeDirectory(output+File.separator+"Processing");
		File.makeDirectory(output+File.separator+"Raw");
	}
	im2stack(t_skip,input,output);
	
}
//ProcessFolder
processFolder(input);


// Function to scan folders/subfolders/files to find files with correct suffix
function im2stack(t_skip, input, output) {
    // Get list of files in the input directory
    fileList = getFileList(input);
    print(fileList.length);
    // Create a dictionary to store image groups
    groups = newArray(0);
    
    // Group files by position name
    for (i = 0; i < fileList.length; i++) {
        fileName = fileList[i];
        //print(fileName.toLowerCase());
        
        if (endsWith(fileName.toLowerCase(), ".tif")) {
            parts = split(fileName, "_");
            if (parts.length >= 2) {
                groupName = parts[0] + "_" + parts[1] + "_" + parts[2];
                print("Group: "+groupName);
                if (!isInArray(groups, groupName)) {
                    groups = Array.concat(groups, groupName);
                }
            }
        }
    }
    
    print("Group length: "+groups.length);
    // Process each group
    for (g = 0; g < groups.length; g++) {
        groupName = groups[g];
        print("Opening");
        File.openSequence(input, " filter="+groupName+"_"+" step=4");
            
        // Save stack
        stackName = groupName + ".tif";
        saveAs("Tiff", output +File.separator +"Raw"+File.separator + stackName);
            
        // Close stack
        close();
        
    }
}

// Helper function to check if an element is in an array
function isInArray(arr, element) {
    for (i = 0; i < arr.length; i++) {
        if (arr[i] == element) {
            return true;
        }
    }
    return false;
}


function processFolder(location) {
	list = getFileList(location);
	list = Array.sort(list);
	flag_found_stacks = 0;
		for (i = 0; i < list.length; i++) {
			if(File.isDirectory(location + File.separator + list[i])){
				
				countFilesInSubfolders(location+File.separator+"Stacks");
				
				print("file is dir");
				if(list[i]=="Stacks/"){
					flag_found_stacks = 1;
					list_processing = getFileList(location+File.separator+"Stacks"+ File.separator +"Processing");
					list_processing = Array.sort(list_processing);
		
					for (n2 = 0; n2 < list_processing.length; n2++) {
						if(endsWith(list_processing[n2].toLowerCase(), ".tif")){
						print("processing tif file");
							countFilesInSubfolders(location+File.separator+"Stacks");
							processFile(location+ File.separator + "Stacks"+ File.separator +"Processing"+ File.separator, list_processing[n2]);	
						}
					}
					
					list_raw = getFileList(location+File.separator+"Stacks"+ File.separator +"Raw");
					list_raw = Array.sort(list_raw);
					for (n2 = 0; n2 < list_raw.length; n2++) {
						//print(list_raw[n2]);
						if(endsWith(list_raw[n2].toLowerCase(), ".tif")){
						print("processing tif file");
							countFilesInSubfolders(location+File.separator+"Stacks");
							processFile(location+File.separator+"Stacks"+ File.separator +"Raw"+ File.separator, list_raw[n2]);	
						}
					}
				}
				else{
					print("Else loop");
					processFolder(location+File.separator +list[i]);
				}

			}
		}
	if(flag_found_stacks==0){
		print("Stacks not found in "+location);
	}
}

function processFile(location, file) {
	
	
	
	print(location+file);
	open(location + file);
	
	Stack.getDimensions(width, height, channels, slices, frames);
	if(channels==1){
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
	Stack.getDimensions(width, height, channels, slices, frames);
	for(c1=channels; c1<4; c1++){
		run("Add Slice", "add=channel prepend");
	}
	Stack.setChannel(1);
	setTool("polygon");
	label = "\n Ensure that all fill operations are completed in Channel 1. \n Use the polygon selection tool to outline the wound area and then press \"F\" to fill in the highlighted area. \n To reset an area that was filled: Select all pixels (Ctrl+A or Cmd+A), and press \"Delete\" on your keyboard. \n Finish highlighting wound area for all time points, then tick the \"Complete\" checkbox. \n If you haven't finished analyzing all timepoints, do not tick the checkbox. \n Click \"Ok\" to save file or Click \"Cancel\" to stop code without saving. ";
	Dialog.createNonBlocking("Did you complete all time points?");
	Dialog.addMessage(label);	
	Dialog.addRadioButtonGroup("Feature being masked:", newArray("Channel 1", "Channel 2", "Channel 3", "Channel 4"), 1, 4, "Channel 1");
	Dialog.addCheckbox("Completed", "FALSE");
	Dialog.show();
	check_comp = Dialog.getCheckbox();
	if(check_comp){
		saveAs(location+File.separator +".."+File.separator +"Completed"+File.separator +file);
		ok = File.delete(location + file);
	}
	else{
		ok = File.delete(location + file);
		saveAs(location+File.separator +".."+File.separator +"Processing"+File.separator +file);
	}
	//waitForUser("Waiting for input", message);
	close();
	
	
}

function countFilesInSubfolders(parentDir) {
	print("\\Clear");
    subfolders = newArray("Raw", "Processing", "Completed");
    totalfiles = 0;
    for (i = 0; i < subfolders.length; i++) {
    	
        subfolder = parentDir + File.separator + subfolders[i];
        if (File.exists(subfolder) && File.isDirectory(subfolder)) {
            fileList = getFileList(subfolder);
            fileCount = fileList.length;
            totalfiles = totalfiles + fileCount;
            print(subfolders[i] + ": " + fileCount + " files");
        } else {
            print(subfolders[i] + ": Subfolder not found");
        }
        
    }
    print("Total: " + totalfiles);
}
