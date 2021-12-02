#Set variables
#@ ImagePlus imp
#@ double (label = "Spot diameter", stepSize=0.2) diameter
#@ double (label = "Quality threshold") threshold
#@ int (label = "Target channel") target_channel
#@ int (label = "Max frame gap") frameGap
#@ double (label = "Linking max distance") linkingMax
#@ double (label = "Gap-closing max distance") closingMax
radius=0.5*diameter;

# This Python/ImageJ2 script shows how to use TrackMate for multi-channel
# analysis. It is derived from a Groovy script by Jan Eglinger, and uses
# the ImageJ2 scripting framework to offer a basic UI / LCI interface 
# for the user.
# You absolutely need the `TrackMate_extras-x.y.z.jar` to be in Fiji plugins
# or jars folder for this to work. Check here to download it: 
# https://imagej.net/TrackMate#Downloadable_jars


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
				
	# Show table and save
	table.show("Results")
	IJ.saveAs("Results","/Users/kevinsuh/Documents/Research/JulieVision_Final/Result.csv")