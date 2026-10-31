# ---------------- 2026-10-31 audit quick wins (docs/audit-2026-10-31.md) ----------------
# exec'd after more_status.py, before more_track.py. Prefix QW_/qw_.

# 1. Eligibility notes (e.g. Apex footer "intended for U.S. users only") override the country list.
_qw_prev_country_status = country_status
def country_status(f, aliases):
    if f.get("us_only") and "united states" not in aliases and "usa" not in aliases:
        return "partial", "Site footer: services intended for U.S. users only"
    return _qw_prev_country_status(f, aliases)

def qw_elig_html(f):
    if not f.get("eligibility_note"): return ""
    src = f'<a href="{e(f["eligibility_source"])}" rel="nofollow noopener" target="_blank">source</a>' if f.get("eligibility_source") else ""
    return f'<p class="note qwelig"><b>Eligibility.</b> {e(f["eligibility_note"])} {src}</p>'

_qw_prev_page = page
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head="", lang="en"):
    m = re.fullmatch(r"/firms/([^/]+)/", path)
    f = BY.get(m.group(1)) if m else None
    if f and f.get("eligibility_note") and "qwelig" not in body:
        body = body.replace('<div class="pgrid">', qw_elig_html(f) + '<div class="pgrid">', 1)
    return _qw_prev_page(path, title, desc, body, jsonld, og_type, extra_head, lang)
