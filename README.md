# net.lugsole.bible_gui

## File formats
This app supports multiple different bible formats to varying extents.

* **SPB** -- These are soft projector bible files.
* **SQLite3** -- as designed by MyBible
* **tsv** -- These files have 6 columns with the data separated by 
* **xml** -- This file 

These files should be installed  in `XDG_DATA_HOME` which would likely be at `$HOME/.var/app/net.lugsole.bible_gui/data`.
In settings, there is an option to add a new translation file to the list.

ToDo:

* Different text rendering engines

settings to add:

* Select rendering engines

## About the file formats
This app supports multiple different bible formats to varying extents.

### SPB
These files have 4 main fields

* **spDataVersion** This is the data type version number. This is 1 in most cases.
* **Title** This it the title of the bible translation.
* **Abbreviation** This is the bible's abbreviation
* **Information** This usually contains information about copyright.
* **RightToLeft** The lines that follow this field contains a list of the books of the Bible.


Then after all the `----`, each line represents a bible verse.
The first piece of data would be a string that represents where this verse belongs in the bible.
The next piece of data is the boon number, the chapter number, then the verse number, then the text of that verse.
All the pieces of data in the line are separated by a tab.


### SQLite3
These files contain multiple tables of which the app only uses two of the tables.
The data they have for each verse is in an HTML kind of format.
This means that there is a lot of data that could be parsed. 
With that being said, not all of the data currently is being processed.

### tsv -- These files have 6 columns with the data separated by 
These files ate a giant table of bible verses. It thas 5 columns

* Book name
* Book name short
* Book number
* Chapter
* Verse
* Verse text

### xml
 
These files contain a root node `XMLBIBLE`.
This has many children named `BIBLEBOOK`
These represent the different books in the Bible. 
These books have attributes `bname` and  `bnumber`.
These are the book mane and book number respectively. 
The books all have children called `CHAPTER`, which has attributes named `cnumber` 
The chapters all have children called `VERS`, which has attributes named `vnumber`.
The data inside this would be the text of that verse.