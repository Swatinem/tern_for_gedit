# tern_for_gedit

This is a simple gedit plugin that provides code completion results
based on [tern](https://github.com/marijnh/tern).

## installation

Copy `tern.plugin` and `tern/` to `~/.local/share/gedit/plugins/`.

This plugin expects `tern` to be installed globally.
So if you haven’t already:

    $ sudo npm install --global tern

## TODO

* *select all occurences* based on terns `refs` for easy renaming,
  based on gedits multi-edit
  (yes, I know tern has `rename` itself. but I would like to have gedit do that)
* *jump-to-definition* based on terns `definition` for jumping around
* maybe a function definition popunder to show the expected parameters, like in
  the tern web demo

