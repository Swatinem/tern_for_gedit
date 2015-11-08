# tern_for_gedit

This is a simple gedit plugin that provides code completion results
based on [tern](https://github.com/marijnh/tern).

Simply type to get identifier completion. Or force a completion popup by
pressing `<Ctrl>+Space`.

Press `<Alt>+F3` to select all references of the identifier at the cursor
position. This hooks into the Multi-Edit gedit plugin, so that needs to be
activated. Also, gedits multi-edit mode leaves a lot to be desired, it is still
quite buggy.

Press `<Alt>+.` to jump to the definition of the identifier at the cursor
position.

## installation

Copy `tern.plugin` and `tern/` to `~/.local/share/gedit/plugins/`.

This plugin expects `tern` to be installed globally.
So if you haven’t already:

    $ sudo npm install --global tern

## TODO

* maybe a function definition popunder to show the expected parameters, like in
  the tern web demo

## License

LGPL-3.0
