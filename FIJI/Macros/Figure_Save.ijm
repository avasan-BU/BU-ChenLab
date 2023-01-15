list = getList("image.titles");
outputfolder = "G:\\My Drive\\Boston University\\Chen Lab\\Prospectus\\Working Files\\Sen - Figs\\2D\\"
for (i=0; i<list.length; i++){
	selectWindow(list[i]);
	print(list[i]);
	
	run("Split Channels");
	run("Merge Channels...", " c3=C1-"+list[i]+ " c2=C4-"+list[i] +" c6=C3-"+list[i] +  " create");
	
	run("Scale Bar...", "width=100 height=100 thickness=15 font=30 color=White background=None location=[Lower Right] horizontal bold overlay label");
	saveAs("TIF", outputfolder + list[i]);
	run("Duplicate...", "duplicate");
	run("Flatten");
	saveAs("TIF", outputfolder+ "COMP"+substring(list[i],0,lengthOf(list[i])-4));
	close();
	
	
	selectWindow(list[i]);
	Stack.setActiveChannels("100");
	run("Duplicate...", "duplicate");
	Stack.setChannel(1);
	run("Grays");
	run("Flatten");
	saveAs("TIF", outputfolder+ "C1-"+substring(list[i],0,lengthOf(list[i])-4));
	close();
	
	selectWindow(list[i]);
	Stack.setActiveChannels("010");
	run("Duplicate...", "duplicate");
	Stack.setChannel(2);
	run("Grays");
	run("Flatten");
	saveAs("TIF", outputfolder+ "C2-"+substring(list[i],0,lengthOf(list[i])-4));
	close();
	
	selectWindow(list[i]);
	Stack.setActiveChannels("001");
	run("Duplicate...", "duplicate");
	Stack.setChannel(3);
	run("Grays");
	run("Flatten");
	saveAs("TIF", outputfolder+ "C3-"+substring(list[i],0,lengthOf(list[i])-4));
	close();
	
	selectWindow("C2-"+list[i]);
	run("Scale Bar...", "width=100 height=100 thickness=15 font=30 color=White background=None location=[Lower Right] horizontal bold overlay label");
	run("Flatten");
	saveAs("TIF", outputfolder+ "C4-"+substring(list[i],0,lengthOf(list[i])-4));
	close();
}