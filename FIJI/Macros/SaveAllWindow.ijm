list = getList("image.titles");
print(list[0]);
// rename windows based on order open - workaround for inconsistent
// naming conventions
for (i=0; i<list.length; i++){
 selectWindow(list[i]);
 Stack.setChannel(4);
 setMinAndMax(494, 9077);
  Stack.setChannel(3);
 setMinAndMax(494, 13366);
 run("8-bit");
 
 Stack.setChannel(4);
 setMinAndMax(0, 135);
 Stack.setChannel(3);
// split channels 
//run("Split Channels");
//("Invert LUT");
 //run("Flatten");
 //run("Enhance Contrast", "saturated=.05");
 //saveAs("JPEG");
 //close();
}