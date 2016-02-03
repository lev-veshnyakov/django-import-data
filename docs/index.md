# Django data import

**Django data import** is a command-line tool for importing XML and HTML data to django models via XSLT mapping.

Source code is located here - [https://github.com/lev-veshnyakov/django-data-import](https://github.com/lev-veshnyakov/django-data-import).

## Basic features

Django data import can take any XML or HTML source file or URL as an input and save entities from it to the django models without need to modify an existing code.

It also supports saving of a related data in form one-to-many and many-to-many.

## Dependencies

It uses [lxml](http://lxml.de) library for all xml manipulations.

## Installation

First you need to install dependencies for lxml library:

```bash
sudo apt-get install libxml2-dev libxslt-dev python-dev
```

Then install django-data-import using pip:

```bash
pip install django-data-import
```

If you want the latest version you can install it from Github:

```bash
pip install git+https://github.com/lev-veshnyakov/django-data-import
```

## Usage

**Django data import** is a management command-line tool, that can be used from the code as well.

Too see the list of console commands type:

```bash
python manage.py help
```

In the output you will find data_import section like below:

```bash
[data_import]
    process_xslt
    validate_xml
```

To get help for the particular command type:

```bash
python manage.py help process_xslt
```

```bash
python manage.py help validate_xml
```

To call console commands from your code use [django.core.management.call_command](https://docs.djangoproject.com/es/1.9/ref/django-admin/#running-management-commands-from-your-code):

```python
from django.core.management import call_command

call_command('process_xslt', 'http://stackoverflow.com/', 'transform.xslt', '--save')
```

## How it works

In a few words it takes a source in either XML or HTML, then takes provided by you XSLT file, transforms the source into the specific XML representation, 
and then saves the data from this XML to the database using models.

The point is, that you don't need to write procedural code for saving data. You only need to write XSLT files, which is actually XML. One file for one source. 
By the source I mean a range of XML or HTML files in the same format. For example all google search result pages have one schema. That means that you can write 
only one XSLT transformation file to import all search pages data.

The difficult moment is that you have to be familiar with XSLT and Xpath.

### XSLT and XPath

XSLT is a language for transforming XML documents into XHTML documents or to other XML documents.

XSLT uses XPath to find information in an XML document. XPath is used to navigate through elements and attributes in XML documents.

If you are not familiar with that I reccomend you to read a [short tutorial on www.w3school.com](http://www.w3schools.com/xsl/xsl_intro.asp).

Moreover, you have to know what an XML Schema is and a particular schema language RELAX NG.

### XML Schema and RELAX NG

**Django data import** uses RELAX NG to validate resuls of transformations. That means if you write XSLT file wrong, it wouldn't be accepted.

But you dont have to write RELAX NG schema yoursef, it's already [included in the module](https://github.com/lev-veshnyakov/django-data-import/tree/master/data_import/schema.rng).

### Resulting XML

After XSLT transformation and schema validation the resulting XML file should be like following:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mapping>
    <model model="app.Author">
        <item key="1">
            <field name="name">Andrew Tanenbaum</field>
        </item>
        <item key="2">
            <field name="name">Donald Knuth</field>
        </item>
    </model>
    <model model="app.Book">
        <item key="1">
            <field name="name">Computer Networks</field>
            <field name="ISBN">0130661023</field>
            <fk model="app.Author" key="1"/>
        </item>
        <item key="2">
            <field name="name">The Art of Computer Programming</field>
            <field name="ISBN">0321751043</field>
            <m2mk model="app.Author" key="2"/>
        </item>
    </model>
</mapping>
```

This XML can be automatically saved to the models.

It contains the root element `<mapping/>`. Into it are nested `<model/>` elements. Each model element represents a particular django model. 
You must provide `model=""` attributes, in which specify a related model. Path to the model is in following format: application_name.ModelName,
the same format like `manage.py dumpdata` uses. 

Model elements don't have to be unique. If you specify several model elements with the same model attribute, they will be merged together. This 
concerns to item elements as well.

Model elements contain `<item/>` elements, representing particular records in the database. They have only one required attribute `name=""`,
which sets the name of a related model field.

### Foreign keys

**Django data import** supports import of related entities in the form one-to-many and many-to-many. To save such entities your models should have
appropriate foreign keys.

In a resulting XML you can use `<fk/>` and `<m2m/>` elements (see above). They have `model=""` and `key=""` attributes, pointing to the related `<item/>`
elements.

### Setting key attribute

The `key=""` attribute of `<item/>` elements must be unique by each unique record. It has not to be the same as a primary key value in the database.
It even will not be stored (if you want to store a primary key value, use `<field/>` element).

Therefore, the value of the `key=""` attribute not obliged to be integer. You can use any sring. Often it's convenient to use an URL as the key.

You can even omit filling that attribute if you don't have related items.

**But one case is special**. That's when you don't have any unique attributes in the source. In that case you can use `generate-id(..)` XPath function.
It will generate unique IDs for every separate XML node in the source.