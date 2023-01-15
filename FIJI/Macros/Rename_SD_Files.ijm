list = getList("image.titles");

// rename windows based on order open - workaround for inconsistent
// naming conventions
for (i=0; i<list.length; i++){
	selectWindow(list[i]);
	if(i<5){
		rename(substring(list[i],lengthOf(list[i])-3,lengthOf(list[i])-1));
	}
	else{
 	rename(substring(list[i],lengthOf(list[i])-4,lengthOf(list[i])-1));
 }
}