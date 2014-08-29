![Silhouette and Python together](https://raw.githubusercontent.com/vishnubob/silhouette/master/extra/cameo_python.png)

Python driver for silhouette vinyl cutters
==========================================

I have two Silhouette vinyl cutters, the Cameo and the Portrait.  I really like them, they are versatile cutters and plotters.  For a recent project, I needed to cut discs from 1/32" thick neoprene rubber, and this presented an array of challenges.  It was impossible to cut the rubber with just one or two passes with the knife.  Correct and accurate cutting requires many passes of the knife, stepping the pressure up every few passes.  Silhouette Studio, the software that is bundled with the cutter shines in some areas and is dreadful in others.   Proving to be tedious and laborious, the bundled software was a poor fit for the parameters of this task.  There had to be a better way!

Through a combination of reverse-engineering and scrounging of the internet, I was able to piece together enough technical information such that I could move, draw, and alter speed and pressure from python code.  This video demonstrates how my code solved the problem of cutting rubber.  I have written the beginnings of a framework, but I need your help!  If you are interested in controlling Silhouette cutters with Python, perhaps you would like to assist in fleshing out this library.  I need help with documentation, testing, and other features like support SVG and DXF files.

Check out the following video:

[![Link to the video](http://img.youtube.com/vi/OxYCJ1hTM2I/0.jpg)](http://www.youtube.com/watch?v=OxYCJ1hTM2I)
