// This code converts open stacks to max projections
// - change sections indicated to control which channels you want active
// Batch code definitions
#@ File (label = "Input directory", style = "directory") input

list = getFileList(input);
// Get names of all open windows
for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i])){
			
		if(endsWith(list[i], ".ims")){
			run("Bio-Formats Importer", "open=["+input+File.separator+file+"] open_all_series color_mode=Default view=Hyperstack stack_order=XYCZT");	
			saveAs("Tiff");
			//Get max intensity projection of image
			run("Z Project...", "projection=[Max Intensity]");
			saveAs("Tiff");
			close("*");
		}
		}
	}
