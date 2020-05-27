# COMPSCI-715: Procedural City Generation

All source code for the **generator module** is available in this repository. 

Please refer to [https://github.com/LEChaney/ProceduralCitiesUnity](https://github.com/LEChaney/ProceduralCitiesUnity) for the road and building visualisation modules.

### Dependencies
* Python 3.6.x +
* geojson 2.5.0
* numpy 1.13.3
* scikit_image 0.15.0
* scipy 1.3.1
* osmnx 0.10
* Shapely 1.6.4.post2
* pandas 0.24.2
* matplotlib 2.1.1
* Pillow 6.2.1
* gdal 3.0.1
* skimage 0.0

To install dependencies, use `pip install -r /path/to/requirements.txt`.

Note that for some Windows machines, unofficial binaries from Christoph Gohlke might be needed. Please refer to [https://www.lfd.uci.edu/~gohlke/pythonlibs/](https://www.lfd.uci.edu/~gohlke/pythonlibs/) for more informmation. 

### Getting Started

Please `git clone https://github.com/x775/citygenerator.git` to get started. 

In order to generate cities, a dedicated configuration file must be devised. These are positioned in the `/input/configs/` folder. To change which configuration file is loaded, line 108 in `citygenerator.py` needs to be updated accordingly. By default, the included `auckland.json` configuration file will be loaded. Note that a new configuration file must include all relevant parameters; the generator currently does not account for incorrect configuration files.

In addition to a configuration file, the generator expects a selection of real-world maps as input. The path to each is specified in the configuration file itself. Currently the generator expects the following real-world maps:

* waterways (.png)
* population density (.tif)
* land use (.tif)

The generator, moreover, requires a dedicated road rule map (.png), the path to which is also specified in the configuration file.

Using the `auckland.json` configuration file, the input images will default to images from Auckland CBD and an organic road rule map. This configuration generates at most 100 major road iterations, and at most 10,000 minor road iterations. If a faster generation time is desirable, please lower the number of allowed iterations.

To generate a city, call `python citygenerator.py`. By default, `show_city`, `show_time`, and `show_stats` are set to `True`, outputting a visualisation of the intermediate representation, the time it took to generate, and evaluation metrics, respectively. To change this behaviour, modify line 108 in `citygenerator.py` accordingly.
