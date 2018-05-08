# Masonic Charity Page Crawler

![Masonic Maps](/demo/pictures/masonic_maps.png "Masonic Maps")

This is a tool that was used to gather information on charitable organizations within the regions of
England, Scotland, and Ireland from MasonicMaps.com. 

It uses peewee and SQLite for data management; Selenium, Chrome, and pyvirtualdisplay for headless browsing
(since Masonic doesn't have its own API); and xlrd and xlwt for outputting the data to CSV and Excel.

Utilizing Selenium, the script has four steps: 

- Navigate to Masonic's national listing page which has links to all of its regional pages, seen [here](http://masonicmaps.com/Home/How-to-Add-an-Organisation,-Province-or-District.aspx)
- Once obtained, navigate to each regional page to gather each organization's page link, example [here](http://masonicmaps.com/Maps/Grand-Lodge-of-Scotland/PGL-Aberdeen-City.aspx)
- Then, navigate to each organization's page and parse out the specific information for each charity, example [here](http://masonicmaps.com/Maps/Grand-Lodge-of-England/Metropolitan-Grand-Lodge-of-London/5175-New-Zealand.aspx)
- Finally, output the results to CSV and/or Excel

Every page parsed using Selenium is downloaded and saved to a database via SQLite for safe-keeping,
and the script should restart the browser automatically to forgo any crawling protection

This project utilizes two other projects of mine: [python-utilities](https://github.com/kelmore5/python-utilities) and [SeleniumBrowser](https://github.com/kelmore5/SeleniumBrowser), both of which
should already be uploaded within this git repository.

*Note: SQLite was chosen over MySQL or Postgres to improve portability of the script, but any database could be 
adopted if need be.

This has been checked and was working on **May 7, 2018**, but I have no plans to maintain the project.

## Install

### Dependencies

- python 3.6
- pyvirtualdisplay
- xlrd
- xlwt
- [selenium](http://selenium-python.readthedocs.io/installation.html)
- [Xvfb](https://www.x.org/archive/X11R7.6/doc/man/man1/Xvfb.1.xhtml) (May not be necessary - check install of pyvirtualdisplay)
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/)
- [peewee](https://github.com/coleifer/peewee)

*pyvirtualdisplay and Xvfb are used to create the headless display, selenium and chromedriver are used for the actual browsing

### Run

First, download the repo

    git clone --recurse-submodules -j8 https://github.com/kelmore5/masonic-web-parser
    
Once downloaded and dependencies are installed, you can run it via

    python3 lib/MasonicParser.py

## Similar Projects

- [Ebay Keyword Crawler](https://github.com/kelmore5/ebay-keyword-crawler)

## Extra Links

- [Selenium](https://www.seleniumhq.org/)
- [Selenium Python Docs](http://selenium-python.readthedocs.io/)
- [Peewee Documentation](http://docs.peewee-orm.com/en/latest/)

## Proof of Concept

You can see a demo from a slideshow I've created [here](https://docs.google.com/presentation/d/17Cx1q3SoYaDH2dW3P5Y7aai8Q85VXepRMGrTtllWXRw/edit?usp=sharing)
or you can look at the sample output from [this](https://github.com/kelmore5/masonic-web-parser/raw/master/demo/output_sample.xlsx) Excel sheet, screenshotted below.

Either way here are some pictures to give a proof of concept.

Masonic's national page, where the script starts

![Masonic National Page](/demo/pictures/national_page.png "Masonic National Page")

Example of regional page to be parsed

![Masonic Regional Page](/demo/pictures/regional_page.png "Masonic Regional Page")

Regional links now residing in a database after being parsed

![Regional Link Database](/demo/pictures/regional_database.png "Regional Link Database")

Example of Organization page to be parsed

![Masonic Organization Page](/demo/pictures/organization_page.png "Masonic Organization Page")

The Organization database with columns filled in (as much as possible)

![Organization Database 1](/demo/pictures/organization_database_1.png "Organization Database 1")

![Organization Database 2](/demo/pictures/organization_database_2.png "Organization Database 2")

![Organization Database 3](/demo/pictures/organization_database_3.png "Organization Database 3")

* Note: Most of the organization pages do not have contact information

Output everything to Excel:

![Excel Output](/demo/pictures/excel_output.png "Excel Output")
