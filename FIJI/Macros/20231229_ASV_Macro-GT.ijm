/* Author: Anish Vasan
 * Description: Macro to process multiple images in a folder for Dr. Sudong Kim
 * Date: 2023/11/30
 * Version: 1.0
 */
// Batch code definitions
#@ File (label = "Input directory", style = "directory") input


//Initiate processFolder function
processFolder(input);


// Function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	print("starting");
	list = getFileList(input);
	list = Array.sort(list);
	for (i=0; i<list.length; i++){
		print("Processing... "+list[i]);
		processSub(input+ File.separator + list[i]);
	}
}
function processSub(input) {
	list2 = getFileList(input + File.separator + "Good/Closed/");
	if(list2.length!=0){
		print("Processing subs... ");
		processFile(input + File.separator + "Good/Closed/", list2);
	}
	list2 = getFileList(input + File.separator + "Good/Not-closed/");
	if(list2.length!=0){
		processFile(input + File.separator + "Good/Not-closed/", list2);
	}
}

// Function to do what you need the code to do
function processFile(input, list_in) {
	//Import all series and save as stack
	for (i=0; i<list_in.length; i++){
	//Make subdirectory for output
	if(endsWith(list2[i],"/")){
		File.makeDirectory(input + File.separator +list_in[i] + File.separator +"Manual_mask" );
		File.openSequence(input + File.separator +list_in[i] + File.separator + "ph1_images/","sort");
		selectImage("ph1_images");
		fname = split(list_in[i],"/");
		print("Processing "+fname[0]);
		saveAs("Tiff", input + File.separator +list_in[i] + File.separator +"Manual_mask/"+fname[0]);
		close("*");
		}
	}
}