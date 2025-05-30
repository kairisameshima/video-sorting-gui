export const defaultKeyboardMappings = {
  default: {
    name: "Default",
    description: "Standard keyboard mapping for video sorting",
    mappings: {
      moveToFolder: {
        a: "Action",
        c: "Comedy",
        d: "Drama",
        h: "Horror",
        s: "SciFi"
      },
      actions: {
        space: "Skip video",
        enter: "Confirm move",
        backspace: "Undo last action",
        "-": "Prepend hyphen",
        p: "Play in native player"
      }
    }
  },
  numpad: {
    name: "Numpad",
    description: "Numeric keypad-focused mapping",
    mappings: {
      moveToFolder: {
        "1": "Action",
        "2": "Comedy",
        "3": "Drama",
        "4": "Horror",
        "5": "SciFi"
      },
      actions: {
        "0": "Skip video",
        enter: "Confirm move",
        ".": "Undo last action",
        "-": "Prepend hyphen",
        "+": "Play in native player"
      }
    }
  },
  vim: {
    name: "Vim-style",
    description: "Vim-inspired keyboard shortcuts",
    mappings: {
      moveToFolder: {
        "shift+a": "Action",
        "shift+c": "Comedy",
        "shift+d": "Drama",
        "shift+h": "Horror",
        "shift+s": "SciFi"
      },
      actions: {
        "j": "Skip video",
        "k": "Confirm move",
        "u": "Undo last action",
        "h": "Prepend hyphen",
        "p": "Play in native player"
      }
    }
  }
}; 