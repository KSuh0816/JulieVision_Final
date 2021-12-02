#@ double (label = "Spot radius", stepSize=0.1) radius
#@ double (label = "Quality threshold") threshold
#@ double (label = "Target channel") target_channel
#@ int (label = "Max frame gap") frameGap
#@ double (label = "Linking max distance") linkingMax
#@ double (label = "Gap-closing max distance") closingMax

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
import fiji.plugin.trackmate.extra.spotanalyzer.SpotMultiChannelIntensityAnalyzerFactory as SpotMultiChannelIntensityAnalyzerFactory

import ij. IJ as IJ
import java.io.File as File
import java.util.ArrayList as ArrayList


