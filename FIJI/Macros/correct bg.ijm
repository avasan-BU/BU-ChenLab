my_path=getDirectory("Choose a Directory");
my_output_path=getDirectory("Choose a Directory");
for(s=1;s<31;s++){
	for(t=1;t<48;t++){ 
		
		my_file="In1__s";
		open(my_path+my_file+s+"_t"+t+".tif");
		run("Subtract Background...", "rolling=50 light stack");
		run("Enhance Local Contrast (CLAHE)", "blocksize=64 histogram=256 maximum=2 mask=*None* fast_(less_accurate)");
		saveAs("Tiff", my_output_path+my_file+s+"_t"+t+".tif");
		close();
	}
}