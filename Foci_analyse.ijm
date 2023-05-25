// Count number of foci and and foci size per nucleus. And saves it as csv files.
// Input folder with image stack with DAPI segmentation, foci segmetnation and foci input image

if (isOpen("Log")) { 
     selectWindow("Log"); 
     run("Close"); 
} 
run("Clear Results");
run("Close All");
if (isOpen("ROI Manager")) {
     selectWindow("ROI Manager");
     run("Close");
}


// Define variables here

macroName="Batch_";

print("Macro: "+macroName);
print("---------------------------------------------------------");

getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
print("Date:",dayOfMonth,"-",month+1,"-",year," Time:",hour,":",minute,"h");
dir=getDirectory("Select the input (Stacks) directory");
print("Input directory: "+dir);
print("");

File.makeDirectory(dir+"\ResultImages");
File.makeDirectory(dir+"\Results");
fileNames=getFileList(dir);
Array.sort(fileNames);


// MAIN LOOP
imageNr=0;
for (ii=0; ii<fileNames.length; ii++){
	if(endsWith(fileNames[ii],".tif")){
		open(dir+fileNames[ii]);
		run("Select None");
		print(fileNames[ii]);
		name=getTitle();
		imageNr++;
		
// Nuclei post-processing
run("RGB Stack");
Stack.setChannel(1);
roiManager("Reset");
name = getTitle();

// selected segmented regions
setThreshold(1,255);
run("Convert to Mask", "method=Default background=Dark slice");
run("Invert", "slice");
// fill holes inside segmentations
run("Fill Holes", "slice");
// split merged nuclei
run("Adjustable Watershed", "tolerance=4 slice");

// select ROI for each nuclei with size above the size exclusion cut-off
rename("MAX");
Stack.setSlice(1);
run("Set Measurements...", "area mean integrated standard stack redirect=None decimal=3");
run("Analyze Particles...", "size=311-20000000 circularity=0-1.00 exclude include add slice");
roiManager("Remove Channel Info");
run("Clear Results");

// Foci analysis
Stack.setSlice(2);

roiManager("Measure");
Area = newArray(nResults);
Mean = newArray(nResults);
Std = newArray(nResults);
nSpots = newArray(nResults);
areaSpots = newArray(nResults);
avgIntensitySpots = newArray(nResults);
intDenSpots=newArray(nResults);
for (i=0;i<nResults;i++){
	Area[i] = getResult("Area",i);
	Mean[i] = getResult("Mean",i);
	Std[i] = getResult("StdDev",i);
}
run("Clear Results");
start =0;
end=roiManager("Count");
selectWindow("MAX");
run("Set Measurements...", "area standard shape integrated limit display redirect=None decimal=3");
// Mask the foci input image using the foci segmentation image
run("Stack to Images");
selectWindow("Green");
selectWindow("Blue");
imageCalculator("AND", "Blue","Green");
run("Merge Channels...", "c1=Red c2=Green c3=Blue");
run("RGB Stack");
for (i=0; i<end; i++){
	roiManager("Select", i);
	start = nResults;
	Stack.setChannel(3);
	// Select the semgented foci
	setThreshold(1,255);
	run("Analyze Particles...", "size=0.1-60000 display include slice add");
    count = 0;
	summeanSpots = 0;
	sumareaSpots = 0;
	for (j=start; j<nResults; j++){
		setResult("nCel",j,i+1);
		setResult("CellID",j,(imageNr*1000)+i+1);
		count++;
		sumareaSpots = sumareaSpots + getResult("Area",j);
		summeanSpots = summeanSpots + getResult("Mean",j);
		intDenSpots[i]=intDenSpots[i]+getResult("IntDen");
		
	}

	nSpots[i] = count;
	areaSpots[i] = sumareaSpots/count;
	avgIntensitySpots[i] = summeanSpots/count; 
	
}
saveAs("Results", dir+"Results/ResultsSpots"+name+".csv");
run("Clear Results");

for (i=0; i<end; i++){
	setResult("CellID",i,(imageNr*1000)+i+1);
	setResult("nCel",i,i+1);
	setResult("AreaNuclei",i, Area[i]);
	setResult("MeanNuclei", i, Mean[i]);
	setResult("StdNuclei",i, Std[i]);
	setResult("nSpots",i, nSpots[i]);
	setResult("AvgAreaSpots",i, areaSpots[i]);
	setResult("AvgIntensitySpots",i, avgIntensitySpots[i]);
	setResult("IntDenSpots",i,intDenSpots[i]);

}
saveAs("Results", dir+"Results/ResultsNuclei"+name+".csv");
roiManager("Show All without labels");
run("From ROI Manager");
saveAs("Tiff", dir+"ResultImages/Result_"+name);


		run("Close All");
		run("Clear Results");
		roiManager("Reset");

	} // END IF MAIN LOOP
}// END FOR MAIN LOOP


// End log file and save in result images directory
getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
print("End: ",hour+":"+minute+":"+second);
print("---------------------------------------------------------");
print("Macro ended correctly");
selectWindow("Log");
getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
saveAs("Text",dir+"ResultImages\\Log_"+macroName+"_"+dayOfMonth+"_"+month+1+"_"+year+".txt");
