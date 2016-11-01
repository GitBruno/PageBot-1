# from https://github.com/fonttools/fonttools/blob/master/Lib/fontTools/varLib/mutator.py
from fontTools.misc.py23 import *
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.varLib import _GetCoordinates, _SetCoordinates
from fontTools.varLib.models import VariationModel, supportScalar, normalizeLocation
import os

def generateInstance(varfilename, location, targetDirectory=None):
	u"""
	Instantiate an instance of a variation font at the specified location.
	Keyword arguments:
	    varfilename -- a variation font file path
	    location -- a dictionary of axis tag and value {"wght": 0.75, "wdth": -0.5}
	"""
	# make a custom file name from the location e.g. VariationFont-wghtXXX-wdthXXX.ttf
	instanceName = ""
	for k,v in location.items():
		# TODO better way to normalize the location name to (0, 1000)
		v = min(v, 1.0)
		v = max(v, -1.0)
		v = int((v*1000+1000)/2)
		instanceName += "-%s%s" % (k, v)
	
	outfile = os.path.splitext(varfilename)[0] + instanceName + '.ttf'
	
	if targetDirectory:
		if not os.path.exists(targetDirectory):
			os.makedirs(targetDirectory)
		outfile = os.path.join(targetDirectory, outfile)

	print "Loading GX font"
	varfont = TTFont(varfilename)

	fvar = varfont['fvar']
	axes = {a.axisTag:(a.minValue,a.defaultValue,a.maxValue) for a in fvar.axes}
	# TODO Round to F2Dot14?
	location = normalizeLocation(location, axes)
	# Location is normalized now
	print "Normalized location:", location

	gvar = varfont['gvar']
	for glyphname,variations in gvar.variations.items():
		coordinates,_ = _GetCoordinates(varfont, glyphname)
		for var in variations:
			scalar = supportScalar(location, var.axes)
			if not scalar: continue
			# TODO Do IUP / handle None items
			varcoords = []
			for coord in var.coordinates:
				# TODO temp hack to avoid NoneType
				if coord is None:
					varcoords.append((0, 0))
				else:
					varcoords.append(coord)
			coordinates += GlyphCoordinates(varcoords) * scalar
			#coordinates += GlyphCoordinates(var.coordinates) * scalar
		_SetCoordinates(varfont, glyphname, coordinates)

	print "Removing GX tables"
	for tag in ('fvar','avar','gvar'):
		if tag in varfont:
			del varfont[tag]

	print "Saving instance font", outfile
	varfont.save(outfile)