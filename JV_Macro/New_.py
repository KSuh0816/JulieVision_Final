#@ ImagePlus imp
dims = imp.getDimensions() # default order: XYCZT
print dims
imp.setDimensions( dims[2,4,3] )
dims = imp.getDimensions() # default order: XYCZT
print dims