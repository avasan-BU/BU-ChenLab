/* Author: Anish Vasan
 * Description: Macro to process multiple images in a folder for Dr. Sudong Kim
 * Date: 2023/11/30
 * Version: 1.0
 */
// Batch code definitions
#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output

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
	list2 = getFileList(input + "Good/Closed/");
	if(list2.length!=0){
		print("Processing subs...Closed ");
		processFile(input + "Good/Closed/", list2);
	}
	list2 = getFileList(input +  "Good/Not-closed/");
	if(list2.length!=0){
		print("Processing subs...Not-closed ");
		processFile(input + "Good/Not-closed/", list2);
	}
}

// Function to do what you need the code to do
function processFile(input, list_in) {
	//Import all series and save as stack
	for (i=0; i<list_in.length; i++){
	//Make subdirectory for output
	if(endsWith(list_in[i],"/")){
		d1 = lastIndexOf(input, "_NHCF");
		dest = substring(input, d1+5, input.length);
		dest2 = split(dest, "\\/");
		d2 = output;
		for (n1 = 0; n1 < dest2.length; n1++) {
			print("d2..."+d2);
			print("i..."+dest2[n1]);
			File.makeDirectory(d2 +File.separator+dest2[n1] );
			d2 = d2+File.separator+dest2[n1];
		
		
		File.makeDirectory(output +dest+list_in[i] );
		File.makeDirectory(output +dest+list_in[i] +"Manual_mask" );
		print(output +dest+list_in[i] +"Manual_mask" );
		}
		
		fname = split(list_in[i],"/");
		print("Processing "+fname[0]);
		File.copy(input + File.separator +list_in[i] + File.separator + "Manual_mask/"+fname[0]+".tif",output +dest+list_in[i] +"Manual_mask/"+fname[0]+".tif");
		
		}
	}
}
