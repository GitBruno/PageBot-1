# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#     P A G E B O T
#
#     Copyright (c) 2016+ Type Network, www.typenetwork.com, www.pagebot.io
#     Licensed under MIT conditions
#     Made for usage in DrawBot, www.drawbot.com
# -----------------------------------------------------------------------------
#
#     polygon.py
#
from pagebot.elements.element import Element
from pagebot.style import XXXL

class Polygon(Element):
    u"""The Polygon element is a simple implementation of the polygon DrawBot function.
    More complex path-like elements inherit from the Path element."""
    def __init__(self, fs, points=None, **kwargs):
        Element.__init__(self, **kwargs)
        if points is None:
            points = []
        self.points = points[:] # Force copy, so caller cannot change and not change size cache.

    def _get_points(self):
        return self._points
    def _set_points(self, points):
        self._points = points
        self._size = None # Cached propertions, will reset by self.w, self.h and self.size

    def _get_size(self):
        if self._size is None:
            if not self.points:
                self._size = 0, 0
            else:
                maxX = maxY = -XXXL
                minX = minY = XXXL
                w = h = None
                for point in self.points:
                    maxX = max(maxX, point[0])
                    minX = min(minX, point[0])
                    maxY = max(maxY, point[1])
                    minY = min(minY, point[1])
                self._size = maxX - minX, maxY - minY
        return self._size
    size = property(_get_size)

    def _get_w(self):
        return self.size[0] # Calculate cache self._size if undefined.
    w = property(_get_w)

    def _get_h(self):
        return self.size[1] # Calculate cache self._size if undefined.

    def draw(self, origin, view):

        p = pointOffset(self.oPoint, origin)
        p = self._applyScale(p)    
        px, py, _ = p, self._applyAlignment(p) # Ignore z-axis for now.
        setFillColor(self.css('fill'))
        setStrokeColor(self.css('stroke', NO_COLOR), self.css('strokeWidth'))
        newPath()
        for index, (ppx, ppy) in enumerate(self.points):
            if index == 0:
                moveTo((px + ppx, py + ppy))
            else:
                lineTo((px + ppx, py + ppy))
        drawPath()

        # If there are child elements, draw them over the polygon.
        self._drawElements(p, view)

        # Draw optional bouning box.
        self.drawFrame(origin, view)
 
        self._restoreScale()
        view.drawElementMetaInfo(self, origin) # Depends on css flag 'showElementInfo'

