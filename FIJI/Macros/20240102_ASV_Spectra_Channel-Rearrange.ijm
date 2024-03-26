
list = getList("image.titles");
for (i=0; i<list.length; i++){
	imageName = list[i];
	imageName = split(imageName,"_");
	IN1= imageName[(imageName.length-1)];
	if(IN1=="DICN1.tif"){
	imageName = imageName[1];
	run("Merge Channels...", "c1=img_"+imageName+"_RFP_new.tif c4=img_"+imageName+"_DICN1.tif create");
	run("Arrange Channels...", "new=21");
	saveAs("Tiff","G:/My Drive/Boston University/Chen Lab/Shared Files/To Emma/20231127_Closure_NHDFneo_NHCF/Nikon-Eclipse-Ti2-Spectra/10X/20231218_NHDFneo-H2B-mCh_SurfTr/"+imageName+".tif");
}
}