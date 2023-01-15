// Use this code to convert images to stack - in case .nd import doesn't work

// Choose input directory
dir = getDirectory("Choose a Directory");

// *** USER INPUT REQUIRED ***
// Change file basename accordingly
basename = "tissue_ai";

// Define stage postions: s=first position, S= last position
s=1;
S = 23;

// Define timepoints: t= first time point, T = last time point, 
t_init = 1;
T=73;

for (s; s<=S; s++) {
	for (t=t_init; t<=T;t=t+4) {
		filename = dir+basename+"_s"+s+"_t"+t+".tif";
		open(filename);	
	}
	name = s;
	run("Images to Stack", "name=name title=[]");
}

// Stacks are not saved in this code!