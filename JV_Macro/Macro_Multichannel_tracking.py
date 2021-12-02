import os
from ij import ImagePlus
from ij.gui import GenericDialog
import fiji.plugin.trackmate.Spot as Spot
import fiji.plugin.trackmate.Model as Model
import fiji.plugin.trackmate.Settings as Settings
import fiji.plugin.trackmate.TrackMate as TrackMate

import fiji.plugin.trackmate.detection.LogDetectorFactory as LogDetectorFactory

import fiji.plugin.trackmate.tracking.LAPUtils as LAPUtils
import fiji.plugin.trackmate.tracking.sparselap.SparseLAPTrackerFactory as SparseLAPTrackerFactory
#import fiji.plugin.trackmate.extra.spotanalyzer.SpotMultiChannelIntensityAnalyzerFactory as SpotMultiChannelIntensityAnalyzerFactory
import fiji.plugin.trackmate.features.spot.SpotIntensityMultiCAnalyzerFactory as SpotIntensityMultiCAnalyzerFactory

import ij. IJ as IJ
import java.io.File as File
import java.util.ArrayList as ArrayList
from ij.measure import ResultsTable  
 
def run(threshold, target_channel, frameGap, linkingMax, closingMax, radius):
  srcDir = IJ.getDirectory("Input_directory")
  if not srcDir:
	return
  dstDir = IJ.getDirectory("Output_directory")
  if not dstDir:
	return
  gd = GenericDialog("Process Folder")
  gd.addStringField("File_extension", ".tif")
  gd.addStringField("File_name_contains", "")
  gd.addCheckbox("Keep directory structure when saving", True)
  gd.showDialog()
  if gd.wasCanceled():
	return
  ext = gd.getNextString()
  containString = gd.getNextString()
  keepDirectories = gd.getNextBoolean()
    
  for root, directories, filenames in os.walk(srcDir):
	for filename in filenames:
	  # Check for file extension
	  if not filename.endswith(ext):
		continue
	  # Check for file name pattern
	  if containString not in filename:
		continue
	
	  process(srcDir, dstDir, root, filename, keepDirectories, threshold, target_channel, frameGap, linkingMax, closingMax, radius)

def process(srcDir, dstDir, currentDir, fileName, keepDirectories, threshold, target_channel, frameGap, linkingMax, closingMax, radius):
  print "Processing:"
  
  # Opening the image
  print "Open image file", fileName
  imp = IJ.openImage(os.path.join(currentDir, fileName))

  # Run the Tracking
  Tracking(imp, threshold, target_channel, frameGap, linkingMax, closingMax, radius)
  
  # Saving the image
  saveDir = currentDir.replace(srcDir, dstDir) if keepDirectories else dstDir
  if not os.path.exists(saveDir):
	os.makedirs(saveDir)
  print "Saving to", saveDir
  IJ.saveAs("Results", os.path.join(saveDir, "Tracking_" + fileName[:-4] + ".csv"));
  imp.close()
  IJ.selectWindow("Results"); 
  IJ.run("Close");


def Tracking(imp, threshold, target_channel, frameGap, linkingMax, closingMax, radius):
  # Swap Z and T dimensions if T=1
  dims = imp.getDimensions() # default order: XYCZT
  if (dims[4] == 1):
    imp.setDimensions( dims[2],dims[4],dims[3] )

  # Get the number of channels 
  nChannels = imp.getNChannels()

  # Setup settings for TrackMate
  settings = Settings()
  settings.setFrom( imp )
  settings.dt = 0.05

  # Spot analyzer: we want the multi-C intensity analyzer.
  #settings.addSpotAnalyzerFactory( SpotMultiChannelIntensityAnalyzerFactory() )
  settings.addSpotAnalyzerFactory( SpotIntensityMultiCAnalyzerFactory() )

  # Spot detector.
  settings.detectorFactory = LogDetectorFactory()
  settings.detectorSettings = settings.detectorFactory.getDefaultSettings()
  settings.detectorSettings['RADIUS'] = radius
  settings.detectorSettings['THRESHOLD'] = threshold
  settings.detectorSettings['TARGET_CHANNEL'] = target_channel
  # Spot tracker.
  settings.trackerFactory = SparseLAPTrackerFactory()
  settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
  settings.trackerSettings['MAX_FRAME_GAP']  = frameGap
  settings.trackerSettings['LINKING_MAX_DISTANCE']  = linkingMax
  settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE']  = closingMax

  # Run TrackMate and store data into Model.
  model = Model()
  trackmate = TrackMate(model, settings)

  if not trackmate.checkInput() or not trackmate.process():
    IJ.log('Could not execute TrackMate: ' + str( trackmate.getErrorMessage() ) )
  else:
    IJ.log('TrackMate completed successfully.' )
    IJ.log( 'Found %d spots in %d tracks.' % ( model.getSpots().getNSpots( True ) , model.getTrackModel().nTracks( True ) ) )
    tm = model.getTrackModel()
    trackIDs = tm.trackIDs( True )

    #Display result on Result table
    table = ResultsTable()
    for trackID in trackIDs:
      spots = tm.trackSpots( trackID )

      ls = ArrayList( spots );
      for spot in ls:			
        table.incrementCounter()  
        table.addValue("Spot_ID", spot.ID())  
        table.addValue("Track_ID", trackID)  
        table.addValue("Frame", spot.getFeature('FRAME'))
        table.addValue("POSITION_X", spot.getFeature('POSITION_X'))
        table.addValue("POSITION_Y", spot.getFeature('POSITION_Y'))
        table.addValue("POSITION_Z", spot.getFeature('POSITION_Z'))
        for i in range( nChannels ):
          table.addValue('MEAN_INTENSITY_CH%d' % (i+1), spot.getFeature( 'MEAN_INTENSITY_CH%d' % (i+1) ) )

    # Show table
    table.show("Results")

#Set variables
#@ double (label = "Spot diameter", stepSize=0.2) diameter
#@ double (label = "Quality threshold") threshold
#@ int (label = "Target channel") target_channel
#@ int (label = "Max frame gap") frameGap	
#@ double (label = "Linking max distance") linkingMax
#@ double (label = "Gap-closing max distance") closingMax
radius=0.5*diameter;

run(threshold, target_channel, frameGap, linkingMax, closingMax, radius)
print "Job is done!"