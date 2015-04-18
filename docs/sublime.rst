asd asdf asdf

Both

* Soure code Pro font makes it easier for eyes

* Twighlight Theme. A lot of themes available.

* Not open source. Looking forward for Atom to mature to be the editor.

* Fast toggle line wrap

* Indentation help lines


PyCharm pros
PyCharm is Java based. Though they hide this really well, it doesn't feel like those clunky Swing applications from 2000s and I did not need to click or see Java-anything during install. But still feel free to hate it for religious reasons. Also writing plugins won't be a joy with all that enterprisey internals pouring upon you.

* More comprehensive run/debug system with a console output that works with process reloading

* Integrated debugger with real breakpoints through IDE - no more import ipdb ; ipdb.set_trace(). Just set a breakpoint and reload the page in the browser.

* Clickable tracebacks in project run output. You instantly get where the error is happening in the source code, instead of alt-tabbing and starting file navigation.

* It allows you to drop into very powerful IPython session after hitting the breakpoint, besides having Expression evalution window. Though took a little while to find out how to do this.

* Better window switcher (CTRL+TAB)

* Powerful autocomplete without the need to install and configure dozens of plugins first

* Spellchecking docstrings, text files, when you type

* Auto import - for a missing highlighted function or class press ALT+Enter, choose from the list and PyCharm will add the import for you

* You can find JetBrains guys in Python conferences and cry.

* Power save mode - disables background tasks like code intel which are really CPU drainage for large projects. Makes digital nomading much more fun as you don't need to fight over the single power plug in the hostel.

* More robust Python code Refactoring tools

* Better VCS (Git) Integration

* Integrated terminal

Sublime Text pros

* Starts like *zap*

* Sooo smooth UI - as it is OpenGL accelerated

* Minimap over scrollbar highlighted hints

* Single click to open file / folder in the explorer

* Smoother "Go To Anywhere". If you type CMD+R "m p m" you get to "my/package/models.py". In PyCharm, looks like you can accomplish with CMD + E "m/ p/ mo"

* Very easy to write plugins in Python. It's a self-contained Python file. In fact you even have a menu entry "Create plugin".

* Integrated plugin installer (Package Control)

* More vibrant plugin community

* Plays more nicely with ecosystem around Python

    * Vastly bestter Restructured Text syntax highlighting

    * Live Restructed text and Markdown preview

    * Django template syntax highlighting, tab completion and snippets: Djaneiro

PyCharm open questions

* Put autoimported names one per line instead of comma separated

* Single click to open files and folders in the project explorer

* The debugger slows down the application (startup) significantly, 5 - 10 seconds. This is especially cumbersome on autoreloading web server development model - I don't want to wait half a minute to see my changes.

* Antialiasing for bold text is in the editor is horrible, making it unreadable. PyCharm is using some whacky-crappy Java software font rendering instead of the OSX default?

* How to stop debugger run of a reloadable web server to jump into exceptions when you are editing the files.