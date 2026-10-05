# Brand fonts

The renderer looks up fonts by **role** (see `brand.json` → `fonts`), trying each path in order:

| role          | files tried, in order                                             |
|---------------|-------------------------------------------------------------------|
| condensed     | `condensed.ttf`, `condensed.otf`, `fallback-condensed-Anton.ttf`    |
| serif-italic  | `serif-italic.ttf`, `serif-italic.otf`, `fallback-serif-italic-PlayfairDisplay.ttf` |
| serif         | `serif.ttf`, `serif.otf`, fallback                                  |
| sans          | `sans.ttf`, `sans.otf`, fallback                                    |

Until the real files are here every render prints `WARNING font role ... is FALLBACK`.

## Put the real fonts in (one time, on the laptop that has them)

```
thumb fonts import "/path/to/XSPIRACY FONTS"   # copies every ttf/otf here, auto-links roles by filename
thumb fonts specimen                            # fonts/specimen.png — every font rendered with its filename
thumb fonts link condensed  "Druk-Black.otf"    # if auto-link picked wrong
thumb fonts link serif-italic "Tiempos-Italic.otf"
thumb fonts                                     # status: should say ok, not FALLBACK
```

Role files (`condensed.ttf` etc.) are copies, so the originals stay untouched. Commit them: the whole point is that
any machine (or a cloud session) can render on-brand without hunting for the font folder again.

Licensing: these are the fonts the channel already licenses. Keep the repo private.
