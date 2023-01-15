// This code converts open stacks to max projections
// - change sections indicated to control which channels you want active

// Get names of all open windows
list = getList("image.titles");
print(list[0]);
// rename windows based on order open - workaround for inconsistent
// naming conventions
for (i=0; i<list.length; i++){
 selectWindow(list[i]);

// split channels 
run("Split Channels");


//Insert scale bar - change properties as desired 
// **don't forget scale definition in ImageJ**
// (Leica automatically provides scale info)
run("Scale Bar...", "width=100 height=12 font=20 color=White background=None location=[Lower Right] bold overlay");

for (n1=0; n1<4; n1++){
// Image is flattened and saved as Tiff - you can choose the direction to save in
run("Flatten");
// To automate save folder - please modify this line with directory and filename
saveAs("Tiff");

// closes flattened image 
// - will not close rearranged stack file in case you want more outputs
close();
close();
}
}