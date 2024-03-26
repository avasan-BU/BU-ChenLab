// This code converts open stacks to max projections
// - change sections indicated to control which channels you want active

// Get names of all open windows
list = getList("image.titles");
print(list[0]);

for (i=0; i<list.length; i++){
 selectWindow(list[i]);

// split channels 
run("Split Channels");


//Insert scale bar - change properties as desired 
// **don't forget scale definition in ImageJ**
// (Leica automatically provides scale info)
//run("Scale Bar...", "width=100 height=12 font=20 color=White background=None location=[Lower Right] bold overlay");

//selectWindow("C1-"+list[i]);
//saveAs("Tiff");
//selectWindow("C2-"+list[i]);
//saveAs("Tiff");
//selectWindow("C3-"+list[i]);
//saveAs("Tiff");
//selectWindow("C4-"+list[i]);
//saveAs("Tiff");
selectWindow("C5-"+list[i]);
saveAs("Tiff");
}
close("*");