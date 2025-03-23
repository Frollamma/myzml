## Introduction

Google My Maps allows you to export a map as a KML file, but without including images, `mykml` fixes this. `mykml` exports images as [data URLs](https://developer.mozilla.org/en-US/docs/Web/URI/Schemes/data) in the KML file, this format is compatible with [umap](https://umap-project.org/) and allows for portability.

## Usage

- Export map data:
  - Open your map in Google My Maps
  - Open the browser console
  - Copy-paste `exportPageData.js` and press enter
  - Save the downloaded file `pageData.json` to the `exports` directory in this repo
  - Export the map as KML (you should find an option `Export to KML/KMZ` in the three dots menu, but these instructions can change, check online) and save it as `input.kml` in the `exports` directory in this repo
- Convert map data:
  - If you followed exactly the instructions above run `python mykml.py` and you will get an `output.kml` file in the `exports` directory of this repo
  - If you save the files with different names or paths than suggested, then run `python mykml.py --help` to see the different options

## Known issues

- Try to make some maps in uMap and see the resulting format, because I don't think it fully supports the Google KML export file, so you could recreate entirely, without using Google's KML export
- Looks like that in the description field Google adds sometimes some HTML (not only text) and that's a problem, I used beautifulsoup to overcome it, but maybe I'm doing something wrong. Look also at "CDATA". - CHECK
- I think uMap has a limit of characters or something in the description field, so you can't have too big images, otherwise in base64 they take all the characters and the image is not rendered.
- The FastKML library has some problems with comparisons with strings... If have a comparison of a placemark value and a string, like this `placemark.name == "Test"` you could get that the two strings are different even tho printing them, they look the same.

## Future improvements

- Either rely on pageData or on the KML export, not on both
- The program assumes that the structure of your map is "folders -> placemarks", while in general it doesn't have to be like that
- Convert the code to Javascript to run in the browser
