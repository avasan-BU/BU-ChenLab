/* Author: Anish Vasan
 * Description: Macro to label ground truth
 * Date: 2024/06/11
 * Version: 1.1
 */
// Batch code definitions
#@ File (label = "Input directory", style = "directory") input1

//Initiate processFolder function
processFolder(input1);


// Function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	print("New Folder");
	list = getFileList(input);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
			//print("Processing sub");
		if(endsWith(list[i], ".tif")){
			//print("processing tif file");
			if(endsWith(list[i], ".tif")){
			processFile(input, list[i]);	
				}
		}
	}
}

function processFile(input, file) {
	
	//print(input+file);
	open(input + file);
	print(input+file);
	run("Split Channels");
	
	selectWindow("C1-"+file);
	fname = split(file,"-");
	fname = split(fname[0],".");
	save(input+fname[0]+"_MM");
	
	
	selectWindow("C2-"+file);
	save(input+fname[0]);
	close("*");
	//ok = File.delete(input + file);
}