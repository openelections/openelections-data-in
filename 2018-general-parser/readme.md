# openelections
This parser was created as part of a capstone project for a Smith College senior capstone course. Below is a description of the parser, including explanations of the choices made and the various inputs that will be asked for.

# Author
Karen Santamaria

# Data location
https://github.com/openelections/openelections-data-in

# Using the Parser 
 - Go to directory of 2018-general-parser
 - `2018-general-parser$ pip install .` 
 - `2018-general-parser$ python parser.py`
 - Input directories as prompted

# Using the Parser (detailed)

 - Create a folder where you want your csv(s) to be
 - Open Terminal.app
 - Type into terminal and type `cd` (don't click enter) 
 - Drag the folder 2018-general-parser onto the terminal app
 - Press enter
 - onto the terminal the folder where the parser is located
 - Type `pip install .` on the Terminal and click enter
 - Type `python parser.py` and click enter (if you know computer defaults to Python 2,type in `python3 parser.py`)
 - Drag in the file or folder of files you want to parse onto the terminal, click enter
 - Drag in the folder where you want to keep the csv(s), click enter
 - The csv files(s) that were parsed will appear in output folder, there pdf(s) that could not be parsed will have it's filename displayed on the terminal

# Using the Validator
 - Check the filenames of the parsed csv's to make sure they are in the proper format
 - `$ python validator.py`
 - Input directories as prompted
 - Output will be displayed in desired directory. Even if the accuracy is less than 100% this may be due to typos or the need for more fine-tuning of the validator


# About Parser Output

**This parser have been validated successfully for:**
1. Clay 
2. Morgan
3. Randolph
4. Blackford 
5. Dekalb
6. Noble (errors in PDF present in parsed output)
7. Greene (errors in PDF present in parsed output)

**Close to working:**
1. Whitley (need to fix `get_party()` )
2. Bartholomew
3. Marshall (poor image quality, need to fix `get_precinct()`)
4. Hendricks (need to fix `get_precinct()`)
5. Pulaski
6. Dubios (need to fix `get_precinct()`)

Other counties may be close to accurate but remain to be investigated due to time.
