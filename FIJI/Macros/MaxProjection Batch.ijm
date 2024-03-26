// This code converts open stacks to max projections
// - change sections indicated to control which channels you want active

// Get names of all open windows
list = getList("image.titles");
// rename windows based on order open - workaround for inconsistent
// naming conventions
for (i=0; i<list.length; i++){
 selectWindow(list[i]);


// *** USER CHANGE REQUIRED HERE ***
// rearrange channels according to desired colours
// c1: red, c2: green, c3: blue, c4: grey, c5: cyan, c6: mag, c7: yellow
// Leica generally outputs blue channel as C1 , so reassign to c3*
// *(actually order determined by order you add channels in LASX)
//run("Merge Channels...", " c1=C1-"+i +" c3=C1-"+i + " c2=C2-"+i +" c5=C3-"+i +  " create");
//selectWindow("Composite");

// rename composite back to original name
//rename(list[i]);

// Max projection!
run("Z Project...", "projection=[Max Intensity]");
//run("Channels Tool...");


// split channels 
run("Split Channels");

// *** USER CHANGE REQUIRED HERE ***
// Choose active channels(change to 1) for max projection - colour will match assigned channels 
//Stack.setActiveChannels("1111000");
//setMinAndMax(470, 1000);
//Insert scale bar - change properties as desired 
// **don't forget scale definition in ImageJ**
// (Leica automatically provides scale info)
//run("Scale Bar...", "width=100 height=20 font=20 color=White background=None location=[Lower Right] bold overlay");
selectWindow("C1-MAX_"+list[i]);
saveAs("Tiff");
selectWindow("C2-MAX_"+list[i]);
saveAs("Tiff");
selectWindow("C4-MAX_"+list[i]);
saveAs("Tiff");
}
close("*");