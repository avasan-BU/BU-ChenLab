dir = getDirectory("Choose a Directory");
basename = "tissue_1";
s=1;
S = 30;
T=48;

for (s; s<=S; s++) {
	for (t=1; t<=T;t++) {
		filename = dir+basename+"_s"+s+"_t"+t+".tif";
		open(filename);	
	}
	name = s;
	run("Images to Stack", "name=name title=[] use");
}
	