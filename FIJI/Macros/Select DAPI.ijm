// This code converts open stacks to max projections
// - change sections indicated to control which channels you want active

// Get names of all open windows
list = getList("image.titles");
print(list[0]);
// rename windows based on order open - workaround for inconsistent
// naming conventions
for (i=0; i<list.length; i++){
 selectWindow(list[i]);
// rename(i);

run("8-bit");
//run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None*");
// split channels 
run("Make Composite");
Stack.setChannel(1);
run("cb skyblue");
Stack.setChannel(2);
run("cb orange");
Stack.setChannel(3);
run("cb reddishpurple");
Stack.setChannel(4);
run("cb yellow");

//run("Split Channels");
// *** USER CHANGE REQUIRED HERE ***
// rearrange channels according to desired colours
// c1: red, c2: green, c3: blue, c4: grey, c5: cyan, c6: mag, c7: yellow
// Leica generally outputs blue channel as C1 , so reassign to c3*
// *(actually order determined by order you add channels in LASX)
//run("Merge Channels...", " c1=C1-"+i +" c2=C3-"+i +  " create");
//selectWindow("Composite");

// rename composite back to original name
//rename(list[i]);

// Max projection!
//run("Z Project...", "projection=[Max Intensity]");
//run("Channels Tool...");

// *** USER CHANGE REQUIRED HERE ***
// Choose active channels(change to 1) for max projection - colour will match assigned channels 
//Stack.setActiveChannels("1110000");
//setMinAndMax(470, 1000);
//Insert scale bar - change properties as desired 
// **don't forget scale definition in ImageJ**
// (Leica automatically provides scale info)

//saveAs("Tiff");

run("Scale Bar...", "width=100 height=20 font=20 color=White background=None location=[Lower Right] bold overlay");

// Image is flattened and saved as Tiff - you can choose the direction to save in
run("Flatten");
// To automate save folder - please modify this line with directory and filename
saveAs("JPEG");

// closes flattened image 
// - will not close rearranged stack file in case you want more outputs

}