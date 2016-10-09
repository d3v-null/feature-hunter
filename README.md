Feature Hunter
====

A python module for trawling music websites that detects changes in lists of feature albums and sends notifications by email

Installation
====

Clone this repository

```bash
git clone https://github.com/derwentx/feature-hunter
```

install the python package

```bash
python setup.py install
```

play with some databases (an example databse is provided)

```bash
cp /example_db.json ~
cd ~
python -m feature_hunter --db example_db.json
```

Configuration
====
Targets are configured by modifying the target table of the database file. Here's the example DB which reads feature albums of the Triple J website:

```json
{
    "targets": {
        "1": {
            "url": "http://www.abc.net.au/triplej/music/featurealbums/",
            "record_spec": "{\"css\": \"div.podlist_item\"}",
            "field_specs": "{\"album\": {\"regex\": \" - \\\\s*(\\\\S[\\\\s\\\\S]+\\\\S)\\\\s*$\", \"css\": \"div.text div.title::text\"}, \"artist\": {\"regex\": \"^\\\\s*(\\\\S[\\\\s\\\\S]+\\\\S)\\\\s* - \", \"css\": \"div.text div.title::text\"}}",
            "name": "triplej"
        }
    }
}

```

it's JSON within JSON (JSON all the way down) so quote chars have to be backslash-escaped, which means it's easier to create your own database using feature_hunter.db.DBWrapper.insert_target(), but if I get enough interest in this repo, I'll add something to make the targets easier to enter into the database.

In this example, our target webpage looks something like this
```html
<!-- ... -->
<div id="two_col">
    <h2 id="latest">latest feature albums</h2>

    <!--item start-->
    <div class="podlist_item">
        <a href="http://www.abc.net.au/triplej/review/album/s4547791.htm"><img width="300" height="300" alt="Banks - The Altar" src="http://www.abc.net.au/triplej/review/album/img/banks_thealtar.jpg"></a>
        <div class="text" style="height: 66px;">
            <div class="title">Banks - The Altar</div>
            Following up her 2013 debut <i>Goddess</i>, the L.A. singer pushes personal boundaries with her alt-pop R&amp;B sound.
        </div>
        <a href="http://www.abc.net.au/triplej/review/album/s4547791.htm" class="more">More</a>
        <div class="clear"></div>
    </div>
    <!--item end-->
    <!-- ... -->

</div>
<!-- ... -->
```

we want to target every `<div class="podlist_item">`  using the css target spec: `div.podlist_item` as our records (it also supports xpath targeting), then to obtain the fields `album` and `artist` from each record we're going to do another css target spec on `div.text div.title::text`. Now since the format of the title is `<artist> - <album>` we're going to further target the fields within this text element by selecting them with a regular expression which is ` - \s*(\S[\s\S]+\S)\s*$` for the album and `^\s*(\S[\s\S]+\S)\\s* - ` for the artist.

That's all you need to specify a target. a css or xpath target spec for each record and a css or xpath target spec for each field. The regex is optional, and not needed if your fields are separated in the html.

Mail
----
You may need to dick around with mail settings to get mail to work. At the moment it connects to localhost as a plaintext SMTP server, so if you're using macOS you'll have to floow this guide: http://www.developerfiles.com/how-to-send-emails-from-localhost-mac-os-x-el-capitan/

If I get enough interest I'll write an SSL SMTP client, because plaintext creds r bad


Roadmap
====
 - [x] Correctly identify changes in targets specified in database
 - [ ] Interface to easily add targets to database
 - [ ] Send alerts when changes are detected
