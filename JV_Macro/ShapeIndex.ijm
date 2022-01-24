// Macro to measure Area, Intensity, Perimeter, and Shape of directory of images

run("Clear Results"); // clear the results table of any previous measurements

// The next line prevents ImageJ from showing the processing steps during 
// processing of a large number of images, speeding up the macro
setBatchMode(true); 

// Show the user a dialog to select a directory of images
inputDirectory = getDirectory("Choose a Directory of Images");
// Get the list of files from that directory
// NOTE: if there are non-image files in this directory, it may cause the macro to crash
fileList = getFileList(inputDirectory);

for (i = 0; i < fileList.length; i++)
{
    processImage(fileList[i]);
}

setBatchMode(false); // Now disable BatchMode since we are finished
updateResults();  // Update the results table so it shows the filenames

// Show a dialog to allow user to save the results file
outputFile = inputDirectory + "2021_11_23_FUCCI_Result.csv";
// Save the results data
saveAs("results",outputFile);

function processImage(imageFile)
{
    // Store the number of results before executing the commands,
    // so we can add the filename just to the new results
   
    
    open(imageFile);
    // Get the filename from the title of the image that's open for adding to the results table
    // We do this instead of using the imageFile parameter so that the
    // directory path is not included on the table
    filename = getTitle();
    input = getImageID();
  	n = nSlices();
  	for (j = 1; j <= nSlices; j++)
  	{
  	prevNumResults = nResults;  
    setSlice(j);
    run("Set Measurements...", "area perimeter redirect=None decimal=3");
	run("Analyze Particles...", "display exclude slice");
	for (row = prevNumResults; row < nResults; row++)
    {
        setResult("Filename", row, filename);
        setResult("Slice", row, j);
        
    }

	}
   
   
    close("*");  // Closes all images
}