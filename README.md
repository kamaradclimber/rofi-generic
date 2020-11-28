# Rofi-generic: A generic text picker using rofi

If you frequently want to paste ticket IDs from a list of tickets, this project is for you.
It tries to be generic and can take any file properly formated as input.

Documentation is limited to a how-to use:

```
rofi-generic --input-file <file>
```

Input file example:
```
A_WORD_THAT_WILL_PASTE anything, really any text that will be used for the search
A_NOTHER_WORD and some tags (label1, label2) or any free text
```

It uses [rofi](https://github.com/DaveDavenport/rofi/) and started as a fork of [rofimoji](https://github.com/fdw/rofimoji).

## Insertion method
It uses the same trick as [rofimoji](https://github.com/fdw/rofimoji), read their beautiful readme.

### Options

| long option | short option | possible values | description |
| --- | --- | --- | --- |
| `--prompt` | `-r` | any string | Define the prompt text for `rofi-generic`. |
| `--rofi-args` | | | Define arguments that `rofimoji` will pass through to `rofi`.<br/>Please note that you need to specify it as `--rofi-args="<rofi-args>"` or `--rofi-args " <rofi-args>"` because of a [bug in argparse](https://bugs.python.org/issue9334). |
| `--insert-with-clipboard` | `-p` | | Insert the selected characters through pasting from the clipboard, instead of directly typing them. See [Insertion Method](#insertion-method). |
| `--copy-only` | `-c` | | Only copy the selected characters to the clipboard without typing them. |
| `--max-recent` |  | 1-10 | Show at most this many recently picked characters. The number will be capped at 10. |
| `--clipboarder` | | `xsel`, `xclip`, `wl-copy` | Access the clipboard with this application. |
| `--typer` | | `xdotool`, `wtype` | Type the characters using this application. |
| `--input-files` | `-f` | | Absolute path to your text file. |
| `--seperator` | `-s` | any string | A string to seperate the input and description (space by default). |

### Dependencies
What else you need:
- Python 3
- A tool to programmatically type characters into applications. Either `xdotool` for X11 or `wtype` for Wayland
- A tool to copy the characters to the clipboard. `xsel` and `xclip` work on X11; `wl-copy` on Wayland
