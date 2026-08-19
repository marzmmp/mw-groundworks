# -*- coding: utf-8 -*-
"""Inline stroke icons. No emoji, no icon font, no external request."""

_A = ('fill="none" stroke="currentColor" stroke-width="1.6" '
      'stroke-linecap="round" stroke-linejoin="round"')

_P = {
    # ---- services -------------------------------------------------------
    "trees": '<path d="M12 3 6.5 11h3L5 18h14l-4.5-7h3L12 3Z"/><path d="M12 18v3"/>'
             '<path d="M3.5 21h17"/>',
    "brush": '<path d="M4 20c3-1 4.5-3.5 5-6"/><path d="M9 20c1.5-2 2-4.5 2-7"/>'
             '<path d="M14 20c0-3.5.8-6.5 2.5-9"/><path d="M19 20c-.4-2.6.2-5 1.6-7"/>'
             '<path d="M2.5 20h19"/><path d="M6 8 4 5m2 3 2.5-2"/>',
    "water": '<path d="M3 8c3-2 6-2 9 0s6 2 9 0"/><path d="M3 14c3-2 6-2 9 0s6 2 9 0"/>'
             '<path d="M3 20c3-2 6-2 9 0s6 2 9 0"/>',
    "wall": '<rect x="3" y="5" width="18" height="4" rx=".5"/>'
            '<rect x="3" y="10" width="8" height="4" rx=".5"/>'
            '<rect x="13" y="10" width="8" height="4" rx=".5"/>'
            '<rect x="3" y="15" width="18" height="4" rx=".5"/>',
    "brick": '<rect x="2.5" y="4" width="19" height="16" rx="1"/>'
             '<path d="M2.5 9.3h19M2.5 14.7h19M12 4v5.3M7 9.3v5.4M17 9.3v5.4M12 14.7V20"/>',
    "deck": '<path d="M3 20V9l9-5 9 5v11"/><path d="M3 12h18"/><path d="M8 20v-8M16 20v-8"/>'
            '<path d="M12 20v-8"/>',
    "mower": '<circle cx="6" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>'
             '<path d="M3.5 15v-3h9v3"/><path d="M12.5 12 20 6"/><path d="M17 5h4v3"/>'
             '<path d="M8.5 15h9"/>',
    "truck": '<path d="M2.5 6h11v10h-11z"/><path d="M13.5 9.5H18l3 3.5v3h-7.5z"/>'
             '<circle cx="6.5" cy="18" r="1.8"/><circle cx="17" cy="18" r="1.8"/>',
    "shield": '<path d="M12 3 4.5 6v6c0 4.4 3.1 7.9 7.5 9 4.4-1.1 7.5-4.6 7.5-9V6L12 3Z"/>'
              '<path d="m9 12 2.2 2.2L15.5 10"/>',
    # ---- ui -------------------------------------------------------------
    "check": '<path d="m4.5 12.5 5 5 10-11"/>',
    "phone": '<path d="M6.5 3.5h3l1.5 4-2 1.5a12 12 0 0 0 6 6l1.5-2 4 1.5v3a2 2 0 0 1-2.2 2 '
             'A17.5 17.5 0 0 1 4.5 5.7 2 2 0 0 1 6.5 3.5Z"/>',
    "msg": '<path d="M4 4.5h16v12H8l-4 3.5z"/><path d="M8 9h8M8 12.5h5"/>',
    "arrow": '<path d="M4 12h15"/><path d="m13 6 6 6-6 6"/>',
    "pin": '<path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11Z"/>'
           '<circle cx="12" cy="10" r="2.6"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5.2l3.2 2"/>',
    "alert": '<path d="M12 3.5 21 19H3l9-15.5Z"/><path d="M12 10v4"/><path d="M12 16.6v.1"/>',
    "image": '<rect x="3" y="4.5" width="18" height="15" rx="1.5"/>'
             '<circle cx="8.5" cy="9.5" r="1.6"/><path d="m4 17 5-4.5 4 3.5 3-2.5 4 3.5"/>',
    "star": '<path d="m12 3.5 2.6 5.4 5.9.8-4.3 4.2 1 5.9-5.2-2.8-5.2 2.8 1-5.9L3.5 9.7l5.9-.8Z"/>',
    "camera": '<path d="M3 7.5h4L8.5 5h7L17 7.5h4v12H3z"/><circle cx="12" cy="13" r="3.6"/>',
    "cal": '<rect x="3.5" y="5" width="17" height="15" rx="1.5"/><path d="M3.5 9.5h17"/>'
           '<path d="M8 3v4M16 3v4"/>',
    "leaf": '<path d="M4 20c0-9 5-14 16-14 0 11-5 14-11 14a5 5 0 0 1-5-5Z"/>'
            '<path d="M8.5 15.5 19 6.5"/>',
    "hammer": '<path d="m14 6 4-2 2 2-2 4-4-4Z"/><path d="m13.5 6.5-9 9 2.5 2.5 9-9"/>',
    "scale": '<path d="M12 4v16"/><path d="M5 8h14"/><path d="M8 8 5 15h6L8 8Z"/>'
             '<path d="M16 8l-3 7h6l-3-7Z"/>',
}


def ico(name, size=24, cls=""):
    p = _P.get(name, _P["check"])
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" width="{size}" height="{size}" '
            f'aria-hidden="true" focusable="false" {_A}>{p}</svg>')
