# backend/scraper/scrape_meals_full.py
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import json, re, time, pathlib, sys
from typing import Dict, List, Tuple, Any

URL = "https://www.bu.edu/dining/location/warren/#menu"

# ====== CONFIG (tweak selectors if BU markup differs) =======================
MEALS = ["Breakfast", "Lunch", "Dinner"]
TITLE_SELECTOR = "h4.js-nutrition-open-alias.menu-item-title"
CARD_SELECTOR  = ".menu-item, .DishCard, .item"      # adjust if your dish wrapper differs
HALL_SELECTOR  = "h1, .location-title, .page-title"
NUTRITION_BUTTON_TEXT = "Nutrition Facts"

#Constants for Dietary Restrictions Sub-Menu
DEFAULT_TIMEOUT_MS = 3000
NAV_TIMEOUT_MS     = 8000
SCROLL_PAUSE_MS    = 200
RETRIES_PER_TAB    = 1           # retry building the map once after a scroll
USE_MODAL_FALLBACK = False       # keep False for speed

IN_FILE  = pathlib.Path("data/meals.json")
OUT_FILE = pathlib.Path("data/meals.with_diet.json")  # change to IN_FILE to overwrite

#Constants for Ingredients Sub-Menu
CARD_SELECTOR_ING  = ".menu-item-wrapper, .menu-item, .DishCard, .item"

IN_FILE_ING  = pathlib.Path("data/meals.with_diet.json")
OUT_FILE_ING = pathlib.Path("data/meals.with_ingredients.json")

# ---- timing/behavior ----
DEFAULT_TIMEOUT_MS_ING       = 2400
NAV_TIMEOUT_MS_ING           = 30000
SCROLL_PAUSE_MS_ING          = 100
OPEN_MODAL_TIMEOUT_MS    = 1800
ING_APPEAR_TIMEOUT_MS    = 5000
PER_ITEM_BUDGET_SEC      = 6.0
MEAL_WATCHDOG_SEC        = 180
RELOAD_EVERY_N_ITEMS     = 40
FUZZY_THRESHOLD          = 0.60
NAV_RETRIES              = 3

MODAL_ROOT_SEL = "[role='dialog']:visible, .modal.is-open:visible, .dialog:visible, .nutrition-facts:visible, .nutrition-facts-modal:visible"
ING_SEL        = ".nutrition-facts-ingredients"

# ============================================================================

def slug(s: str) -> str:
    s = re.sub(r"\s+", " ", s.strip().lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def to_int_or_none(s):
    if not s:
        return None
    m = re.search(r"\d+", str(s))
    return int(m.group(0)) if m else None

# ---------- STRICT, BIDIRECTIONAL LABEL PARSER ------------------------------
def _grab_g_bidi(text: str, label_pat: str):
    """
    Return grams for a label, matching either:
      1) label ... <num>g     e.g., 'Saturated Fat: 3 g'
      2) <num>g ... label     e.g., '3g saturated fat'
    Enforces 'g' units and word-ish boundaries around label.
    """
    t = re.sub(r"\s+", " ", text.strip())
    # label first
    pat1 = rf"(?<![a-z])(?:{label_pat})(?![a-z])\s*[:\-]?\s*(?P<num>\d+)\s*g"
    m1 = re.search(pat1, t, flags=re.I)
    if m1:
        return int(m1.group("num"))
    # number first
    pat2 = rf"(?P<num>\d+)\s*g\s*(?:of\s+)?(?:{label_pat})(?![a-z])"
    m2 = re.search(pat2, t, flags=re.I)
    if m2:
        return int(m2.group("num"))
    return None

def _grab_cal_bidi(text: str):
    """
    Calories can appear as 'Calories 140' or '140 cals'.
    """
    t = re.sub(r"\s+", " ", text.strip())
    # label first
    m1 = re.search(r"(?<![a-z])calories?(?![a-z])\s*[:\-]?\s*(?P<num>\d+)", t, flags=re.I)
    if m1:
        return int(m1.group("num"))
    # number first
    m2 = re.search(r"(?P<num>\d+)\s*(?:k?cal(?:s)?|cals?)\b", t, flags=re.I)
    if m2:
        return int(m2.group("num"))
    return None

def extract_macros_from_text(text: str):
    """
    Extracts:
      - calories  -> 'Calories' / 'cals'
      - protein   -> 'Protein(s)'
      - carbs     -> 'Total Carbohydrate(s)' OR 'Carb(s)/Carbohydrate(s)'  (NEVER 'sugars')
      - fat       -> 'Saturated Fat' / 'Sat Fat' (this is the value we report as 'fat')
    All gram fields require a 'g' unit and use bidirectional matching.
    """
    calories = _grab_cal_bidi(text)
    protein  = _grab_g_bidi(text, r"protein(?:s)?")
    # Prefer Total Carbohydrate; fallback to generic carbs
    carbs = (_grab_g_bidi(text, r"total\s+carbohydrate(?:s)?")
             or _grab_g_bidi(text, r"carb(?:s)?|carbohydrate(?:s)?"))
    # Saturated fat only
    fat = (_grab_g_bidi(text, r"satur(?:ated)?"))
    return {"calories": calories, "protein": protein, "carbs": carbs, "fat": fat}
# ---------------------------------------------------------------------------

def click_meal_tab(page, meal_text: str) -> bool:
    for role in ("tab", "button"):
        try:
            page.get_by_role(role, name=meal_text, exact=False).click(timeout=1200)
            return True
        except PWTimeout:
            pass
    paths = [
        f"//button[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'))='{meal_text.lower()}']",
        f"//*[self::a or self::button or @role='tab'][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{meal_text.lower()}')]",
    ]
    for xp in paths:
        try:
            page.locator(f"xpath={xp}").first.click(timeout=1200)
            return True
        except PWTimeout:
            continue
    return False

def is_visible_filter_js(selector: str) -> str:
    return f"""
    () => Array.from(document.querySelectorAll('{selector}'))
      .filter(el => el.offsetParent !== null)
      .filter(el => !el.closest('template,script,noscript'))
      .filter(el => !el.closest('[hidden], [aria-hidden="true"], .hidden, .sr-only, .visually-hidden, .d-none'))
    """

def collect_visible_cards(page):
    handles = page.evaluate_handle(is_visible_filter_js(CARD_SELECTOR))
    cards   = handles.get_properties().values()
    out = []
    for h in cards:
        el = h.as_element()
        if el: out.append(el)
    return out

def inner_text(el_handle):
    try:
        return el_handle.inner_text().strip()
    except Exception:
        return ""

def text_content(el_handle):
    try:
        return el_handle.text_content().strip()
    except Exception:
        return ""

def get_child_text(card, selector):
    try:
        el = card.query_selector(selector)
        return el.inner_text().strip() if el else ""
    except Exception:
        return ""

def extract_macros_from_card(card):
    """
    Parse ONLY with label-anchored, bidirectional regex from the card's full text,
    so carbs and saturated fat cannot collide.
    """
    try:
        txt = text_content(card)
        return extract_macros_from_text(txt)
    except Exception:
        return {"calories": None, "protein": None, "carbs": None, "fat": None}

def extract_description(card):
    desc = get_child_text(card, ".description, .desc, .notes, .menu-item-desc")
    if desc:
        return desc
    t = text_content(card)
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    return lines[1] if len(lines) > 1 else ""

def open_nutrition_modal(card):
    try:
        btn = card.get_by_role("button", name=NUTRITION_BUTTON_TEXT, exact=False)
        if btn and btn.count() > 0:
            btn.first.click()
            return True
    except Exception:
        pass
    try:
        btn2 = card.locator(f"text={NUTRITION_BUTTON_TEXT}").first
        if btn2 and btn2.count() > 0:
            btn2.click()
            return True
    except Exception:
        pass
    return False

def collect_dietary_from_modal(page):
    try:
        modal = page.get_by_role("dialog").first
        modal.wait_for(state="visible", timeout=3000)
    except PWTimeout:
        try:
            page.wait_for_selector(".modal:visible, .dialog:visible, .popup:visible", timeout=1500)
            modal = page.locator(".modal:visible, .dialog:visible, .popup:visible").first
        except PWTimeout:
            return []

    labels = set()
    try:
        for sel in [".badge", ".dietary", ".dietary .tag", "[data-diet]"]:
            for t in modal.locator(sel).all_inner_texts():
                t = t.strip()
                if t: labels.add(t)
        for sel in [".allergens li", ".dietary li", ".allergen-list li", ".nutrition-facts li"]:
            for t in modal.locator(sel).all_inner_texts():
                t = t.strip()
                if t: labels.add(t)
        alts = modal.locator("img[alt]").evaluate_all("els => els.map(e=>e.alt)")
        for a in alts:
            a = a.strip()
            if a: labels.add(a)
    except Exception:
        pass

    # Normalize & dedupe
    norm = []
    for s in labels:
        s2 = s.strip()
        s2 = re.sub(r"\s*[-–]\s*", "-", s2)
        s2 = re.sub(r"\s+", " ", s2)
        s2 = s2.title()
        s2 = s2.replace("Gluten Free", "Gluten-Free")
        if s2:
            norm.append(s2)

    # Close modal
    closed = False
    try:
        page.get_by_role("button", name=re.compile("close", re.I)).first.click(timeout=800)
        closed = True
    except Exception:
        pass
    if not closed:
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass

    seen, out = set(), []
    for t in norm:
        if t not in seen:
            seen.add(t); out.append(t)
    return out

def scrape_all_meals():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="tastebu-hackathon/1.0 (+contact@example.com)")
        page.goto(URL, wait_until="networkidle")

        # Hall name
        try:
            page.wait_for_selector(HALL_SELECTOR, timeout=5000)
            hall = page.locator(HALL_SELECTOR).first.inner_text().strip()
        except Exception:
            hall = "West Campus Dining Hall"

        page.wait_for_selector(TITLE_SELECTOR, timeout=15000)

        meals_out = []

        for meal in MEALS:
            if not click_meal_tab(page, meal):
                continue

            page.wait_for_timeout(400)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(300)

            cards = collect_visible_cards(page)

            for card in cards:
                title_el = card.query_selector(TITLE_SELECTOR)
                if not title_el:
                    continue
                name = title_el.inner_text().strip()
                if not name:
                    continue

                macros = extract_macros_from_card(card)
                calories = macros.get("calories") or 0
                protein  = macros.get("protein")  or 0
                carbs    = macros.get("carbs")    or 0   # only carb labels
                fat      = macros.get("fat")      or 0   # saturated fat only

                description = extract_description(card)

                dietary = []
                if open_nutrition_modal(card):
                    dietary = collect_dietary_from_modal(page)

                meals_out.append({
                    "id": f"{slug(name)}@{meal.lower()}@{slug(hall)}",
                    "name": name,
                    "hall": hall,
                    "mealType": meal.lower(),
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat,  # SATURATED FAT ONLY
                    "dietaryRestrictions": dietary,
                    "description": description
                })

        browser.close()

    # De-dupe by (name, hall, mealType)
    seen, final = set(), []
    for it in meals_out:
        key = (it["name"].lower(), it["hall"].lower(), it["mealType"])
        if key in seen:
            continue
        seen.add(key)
        final.append(it)

    return final
#----------------------------------------------------------------------------
#############################################################################
#Below Functions are for added Dietary Restrictions
#############################################################################
#----------------------------------------------------------------------------
def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def normalize_tag(tag: str) -> str:
    if not tag:
        return ""
    t = norm_space(tag).title()
    return t.replace("Gluten Free", "Gluten-Free")

def log(*args, **kwargs):
    kwargs.setdefault("flush", True)
    print(*args, **kwargs)

# ---- fast: build {title -> [diets]} from the current tab in one JS pass ----
def build_diet_map_for_visible(page):
    """
    Returns dict { normalized_title_lower: [diet1, diet2, ...] } for all visible cards
    without walking each card from Python. Very fast.

    First section creates a JavaScript function that checks if the DOM is visible yet
    and whether or not the code can read the HTML (card) yet

    Second section uses CARD_SELECTOR and TITLE_SELECTOR to open the new menu that pops
    up (Clicks the Nutrition Facts) and then pulls all of the contents that are in the 
    unordered list (ul) containing the dietary restrictions and returning the variable
    that gets that content
    """
    js = f"""
    () => {{
      const isVisible = (el) => {{
        if (!el) return false;
        if (el.closest('template,script,noscript')) return false;
        if (el.closest('[hidden], [aria-hidden="true"], .hidden, .sr-only, .visually-hidden, .d-none')) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') return false;
        if (!el.offsetParent && style.position !== 'fixed') return false;
        return true;
      }};

      const cards = Array.from(document.querySelectorAll("{CARD_SELECTOR}")).filter(isVisible);
      const out = [];
      for (const card of cards) {{
        const titleEl = card.querySelector("{TITLE_SELECTOR}");
        if (!titleEl) continue;
        const title = (titleEl.textContent || "").trim().replace(/\\s+/g, " ");
        if (!title) continue;

        const liNodes = card.querySelectorAll("ul.menu-item-dietary-restriction li, ul.js-filterby-dietary-restriction li");
        const diets = Array.from(liNodes).map(li => (li.textContent || "").trim()).filter(Boolean);

        out.push({{ title, diets }});
      }}
      return out;
    }}
    """
    rows = page.evaluate(js)
    diet_map = {}
    for row in rows or []:
        title = norm_space(row.get("title", "")).lower()
        if not title:
            continue
        diets = [normalize_tag(d) for d in (row.get("diets") or []) if d]
        # de-dupe
        seen, cleaned = set(), []
        for d in diets:
            if d and d.lower() not in {"n/a", "none"} and d not in seen:
                seen.add(d)
                cleaned.append(d)
        diet_map[title] = cleaned
    return diet_map

def click_meal_tab(page, meal_text: str) -> bool:
    # Try role-based
    for role in ("tab", "button"):
        try:
            page.get_by_role(role, name=meal_text, exact=False).click(timeout=1200)
            return True
        except Exception:
            pass
    # Fallback XPath
    try:
        xp = f"//*[self::a or self::button or @role='tab'][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{meal_text.lower()}')]"
        page.locator(f"xpath={xp}").first.click(timeout=1200)
        return True
    except Exception:
        return False

def update_dietary_fast(meals):
    by_meal = {"breakfast": [], "lunch": [], "dinner": []}
    for m in meals:
        mt = (m.get("mealType") or "").lower()
        if mt in by_meal:
            by_meal[mt].append(m)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(user_agent="tastebu-hackathon/1.0 (+contact@example.com)")
            page.set_default_timeout(DEFAULT_TIMEOUT_MS)
            page.set_default_navigation_timeout(NAV_TIMEOUT_MS)

            log("Navigating to page...")
            page.goto(URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
            try:
                page.wait_for_load_state("networkidle", timeout=4000)
            except Exception:
                pass

            for meal_label in MEALS:
                mt_key = meal_label.lower()
                targets = by_meal.get(mt_key) or []
                if not targets:
                    continue

                log(f"\n== {meal_label} ==")

                if not click_meal_tab(page, meal_label):
                    log(f"⚠️  Could not click {meal_label} tab; skipping.")
                    continue

                # Allow lazy content; quick scroll to bottom once
                page.wait_for_timeout(SCROLL_PAUSE_MS)
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                except Exception:
                    pass
                page.wait_for_timeout(SCROLL_PAUSE_MS)

                # Build map; optionally retry after an extra scroll
                diet_map = build_diet_map_for_visible(page)
                retry = 0
                while retry < RETRIES_PER_TAB and not diet_map:
                    retry += 1
                    try:
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    except Exception:
                        pass
                    page.wait_for_timeout(SCROLL_PAUSE_MS)
                    diet_map = build_diet_map_for_visible(page)

                # Merge into meals + DEBUG PRINT PER ITEM
                updated, missing = 0, 0
                for m in targets:
                    title_key = norm_space(m.get("name", "")).lower()
                    diets = diet_map.get(title_key)

                    if diets:
                        m["dietaryRestrictions"] = diets
                        updated += 1
                        log(f"  • {m.get('name', '<no name>')}: {', '.join(diets)}")
                    else:
                        missing += 1
                        log(f"  • {m.get('name', '<no name>')}: (none)")

                log(f"-- Summary {meal_label}: updated {updated}, missing {missing}")

                # Optional: modal fallback (disabled for speed)
                if USE_MODAL_FALLBACK and missing:
                    log("  (modal fallback disabled for speed)")

        finally:
            browser.close()
#--------------------------------------------------------------------------------------
def norm_space_ing(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def log_ing(*args, **kwargs):
    kwargs.setdefault("flush", True)
    print(*args, **kwargs)

# ---------- normalize + fuzzy ----------
def simplify_title(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokens(s: str) -> List[str]:
    return [t for t in simplify_title(s).split() if t]

def token_overlap(a: str, b: str) -> float:
    A, B = set(tokens(a)), set(tokens(b))
    if not A or not B: return 0.0
    inter = len(A & B)
    return inter / max(len(A), len(B))

# ---------- nav ----------
def click_meal_tab(page, meal_text: str) -> bool:
    try:
        page.evaluate("window.scrollTo(0,0)"); page.wait_for_timeout(60)
    except Exception:
        pass
    for role in ("tab", "button"):
        for name in ({"exact": True}, {}):
            try:
                page.get_by_role(role, name=meal_text, **name).click(timeout=1100)
                return True
            except Exception:
                pass
    for sel in [
        ".menu-tabs a", ".menu-tabs button", ".filters a", ".filters button",
        "a.js-sortby-meal, button.js-sortby-meal",
    ]:
        try:
            cand = page.locator(sel).filter(has_text=meal_text)
            if cand.count() > 0:
                cand.first.click(timeout=1100)
                return True
        except Exception:
            pass
    for sel in (f"text=^{meal_text}$", f"text=/{meal_text}/i"):
        try:
            page.locator(sel).first.click(timeout=1100)
            return True
        except Exception:
            pass
    try:
        xp = f"//*[self::a or self::button or @role='tab'][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{meal_text.lower()}')]"
        page.locator(f"xpath={xp}").first.click(timeout=1200)
        return True
    except Exception:
        pass
    try:
        ok = page.evaluate("""
          (txt) => {
            const t = txt.toLowerCase().trim();
            const nodes = Array.from(document.querySelectorAll('a,button,[role=tab]'))
              .filter(n => n.offsetParent !== null);
            for (const n of nodes) {
              const s = (n.textContent||'').trim().toLowerCase();
              if (s === t) { n.click(); return true; }
            }
            return false;
          }
        """, meal_text)
        if ok: return True
    except Exception:
        pass
    return False

def goto_with_retries(page, url: str, retries: int = NAV_RETRIES):
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=9000 if attempt == 1 else NAV_TIMEOUT_MS_ING)
            try:
                page.wait_for_selector(TITLE_SELECTOR, timeout=5000)
            except Exception:
                page.wait_for_selector(CARD_SELECTOR_ING, timeout=5000)
            return
        except Exception as e:
            last_err = e
            log_ing(f"  retrying navigation ({attempt}/{retries})...")
            try: page.wait_for_timeout(600)
            except Exception: pass
    raise last_err

# ---------- helpers ----------
def close_modal_fast(page):
    for sel in [
        "button[aria-label='Close']",
        "button:has-text('Close')",
        ".js-nutrition-close",
        ".nutrition-close",
        ".modal button:has-text('×')",
    ]:
        try:
            page.locator(sel).first.click(timeout=300); return
        except Exception:
            pass
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass

def parse_ingredients_text(raw: str) -> Tuple[str, List[str]]:
    body = norm_space_ing(raw)
    body = re.sub(r"^\s*Ingredients\s*:\s*", "", body, flags=re.I)
    body = re.split(r"\b(Dietary\s+Restrictions|Allergens)\b", body, flags=re.I)[0].strip()
    parts = [p.strip() for p in body.split(",") if p.strip()]
    return body, parts

def try_hidden_ingredients_in_card(card) -> str:
    try:
        txt = card.evaluate("""(node) => {
            const el = node.querySelector('.nutrition-facts-ingredients');
            return el ? (el.textContent || '') : '';
        }""")
        if txt and txt.strip():
            body, parts = parse_ingredients_text(txt)
            return ", ".join(parts) if parts else body
    except Exception:
        pass
    return ""

def try_open_modal_wait_ingredients(card) -> bool:
    page = card.page
    if page.locator(MODAL_ROOT_SEL).count() > 0:
        close_modal_fast(page); page.wait_for_timeout(60)

    try:
        card.evaluate("(n)=>n.scrollIntoView({block:'center', inline:'nearest'})")
        card.page.wait_for_timeout(50)
    except Exception:
        pass

    for sel in [
        "button.js-nutrition-open.button-primary.menu-nutrition-button",
        "button.js-nutrition-open",
        "button.menu-nutrition-button",
        "button:has-text('Nutrition')",
        "h4.js-nutrition-open-alias.menu-item-title",
    ]:
        try:
            card.locator(sel).first.click(timeout=OPEN_MODAL_TIMEOUT_MS)
            page.locator(ING_SEL).first.wait_for(state="visible", timeout=ING_APPEAR_TIMEOUT_MS)
            return True
        except Exception:
            pass

    # JS fallback
    try:
        ok = card.evaluate("""
          (node) => {
            const btns = node.querySelectorAll('button, [role=button], a, h4.js-nutrition-open-alias.menu-item-title');
            for (const b of btns) {
              const t = (b.textContent||'').toLowerCase();
              if (t.includes('nutrition') || b.matches('h4.js-nutrition-open-alias.menu-item-title')) {
                b.click(); return true;
              }
            }
            return false;
          }
        """)
        if ok:
            try:
                page.locator(ING_SEL).first.wait_for(state="visible", timeout=ING_APPEAR_TIMEOUT_MS)
                return True
            except Exception:
                pass
    except Exception:
        pass
    return False

def extract_ingredients_from_modal(modal) -> str:
    """
    Extracts the ingredients section from the modal and returns it as a single
    comma-separated string. Returns an empty string if not found.
    """
    try:
        if modal.locator(ING_SEL).count() > 0:
            txt = modal.locator(ING_SEL).first.inner_text(timeout=700)
            body, parts = parse_ingredients_text(txt)
            if parts:
                return ", ".join(parts)
            elif body:
                return body.strip()
    except Exception:
        pass

    try:
        full = modal.inner_text(timeout=900)
        m = re.search(
            r"ingredients\s*:\s*(.+?)\s*(dietary\s+restrictions|allergens|$)",
            norm_space_ing(full),
            flags=re.I,
        )
        if m:
            body, parts = parse_ingredients_text(m.group(0))
            if parts:
                return ", ".join(parts)
            elif body:
                return body.strip()
    except Exception:
        pass

    return ""

# ---------- NEW: snapshot visible cards + titles ----------
def snapshot_cards_with_titles(page) -> List[Dict[str, Any]]:
    js = f"""
    () => {{
      const vis = (el) => {{
        if (!el) return false;
        if (el.closest('template,script,noscript')) return false;
        if (el.closest('[hidden], [aria-hidden="true"], .hidden, .sr-only, .visually-hidden, .d-none')) return false;
        const s = getComputedStyle(el);
        if (s.display === 'none' || s.visibility === 'hidden') return false;
        if (!el.offsetParent && s.position !== 'fixed') return false;
        return true;
      }};
      const cards = Array.from(document.querySelectorAll("{CARD_SELECTOR_ING}"));
      const out = [];
      let idx = -1;
      for (const c of cards) {{
        idx += 1;
        if (!vis(c)) continue;
        const t = c.querySelector("{TITLE_SELECTOR}");
        const title = (t && t.textContent || '').trim().replace(/\\s+/g,' ');
        if (!title) continue;
        out.push({{ index: idx, title }});
      }}
      return out;
    }}
    """
    rows = page.evaluate(js)
    out = []
    for r in rows or []:
        t = norm_space_ing(r.get("title",""))
        if not t: continue
        out.append({"index": int(r.get("index", -1)), "title": t, "simple": simplify_title(t)})
    return out

def best_card_index_for_title(target_title: str, snapshot: List[Dict[str, Any]]) -> int:
    key = simplify_title(target_title)
    for r in snapshot:
        if r["simple"] == key:
            return r["index"]
    best_idx, best_score = -1, 0.0
    for r in snapshot:
        s = token_overlap(key, r["simple"])
        if s > best_score:
            best_idx, best_score = r["index"], s
    return best_idx if best_score >= FUZZY_THRESHOLD else -1

# ---------- main (targeted only) ----------
def update_ingredients_targeted(meals):
    index_by_meal: Dict[str, Dict[str, List[int]]] = {"breakfast": {}, "lunch": {}, "dinner": {}}
    pending_titles: Dict[str, List[str]] = {"breakfast": [], "lunch": [], "dinner": []}

    for idx, m in enumerate(meals):
        mt = (m.get("mealType") or "").lower()
        if mt not in index_by_meal:
            continue
        title = m.get("name") or ""
        key = simplify_title(title)
        index_by_meal[mt].setdefault(key, []).append(idx)
        if not m.get("ingredients"):
            pending_titles[mt].append(title)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        context = browser.new_context(
            user_agent="tastebu-hackathon/1.0 (+contact@example.com)",
            viewport={"width": 1366, "height": 900},
        )
        def _route(route, request):
            if request.resource_type in ("image", "media", "font"):
                return route.abort()
            return route.continue_()
        context.route("**/*", _route)

        try:
            page = context.new_page()
            page.set_default_timeout(DEFAULT_TIMEOUT_MS_ING)
            page.set_default_navigation_timeout(NAV_TIMEOUT_MS_ING)

            log_ing("Navigating to page...")
            goto_with_retries(page, URL)
            try: page.wait_for_load_state("networkidle", timeout=4000)
            except Exception: pass

            for meal_label in MEALS:
                mt_key = meal_label.lower()
                targets = pending_titles.get(mt_key) or []
                if not targets:
                    continue

                log_ing(f"\n== {meal_label} (ingredients) ==")
                if not click_meal_tab(page, meal_label):
                    try: page.evaluate("window.scrollTo(0,0)")
                    except Exception: pass
                    if not click_meal_tab(page, meal_label):
                        log_ing(f"⚠️  Could not click {meal_label} tab; skipping.")
                        continue

                page.wait_for_timeout(SCROLL_PAUSE_MS_ING)
                try: page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                except Exception: pass
                page.wait_for_timeout(SCROLL_PAUSE_MS_ING)

                snapshot = snapshot_cards_with_titles(page)
                if not snapshot:
                    try: page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    except Exception: pass
                    page.wait_for_timeout(200)
                    snapshot = snapshot_cards_with_titles(page)

                updated = skipped = missed = 0
                meal_deadline = time.perf_counter() + MEAL_WATCHDOG_SEC
                processed_in_meal = 0
                cards_all = page.locator(CARD_SELECTOR_ING)

                for t in targets:
                    if time.perf_counter() >= meal_deadline:
                        log_ing(f"  ⏱️ Meal deadline reached for {meal_label}; moving on.")
                        break

                    t0 = time.perf_counter()
                    try:
                        key = simplify_title(t)
                        idxs = index_by_meal[mt_key].get(key, [])
                        if idxs and all(meals[i].get("ingredients") for i in idxs):
                            skipped += 1
                            continue

                        ci = best_card_index_for_title(t, snapshot)
                        if ci < 0:
                            snapshot = snapshot_cards_with_titles(page)
                            ci = best_card_index_for_title(t, snapshot)
                        if ci < 0:
                            missed += 1
                            log_ing(f"  • {t}: (card not found in snapshot)")
                            continue

                        card = cards_all.nth(ci)
                        if not card.is_visible():
                            try: page.evaluate("window.scrollBy(0, Math.floor(window.innerHeight*0.8))")
                            except Exception: pass
                            page.wait_for_timeout(120)
                            if not card.is_visible():
                                missed += 1
                                log_ing(f"  • {t}: (card not visible)")
                                continue

                        ing_text = try_hidden_ingredients_in_card(card)
                        opened_modal = False

                        if not ing_text:
                            opened_modal = try_open_modal_wait_ingredients(card)
                            if not opened_modal:
                                missed += 1
                                log_ing(f"  • {t}: (ingredients not visible)")
                                continue

                            modal = None
                            try:
                                ing_blocks = page.locator(f"{ING_SEL}:visible")
                                if ing_blocks.count() > 0:
                                    ing = ing_blocks.last
                                    modal = ing.locator(
                                        "xpath=ancestor::*[self::div or self::section]"
                                        "[contains(@class,'modal') or contains(@class,'dialog') or contains(@class,'nutrition-facts')][1]"
                                    )
                                    modal = modal.first if modal and modal.count() > 0 else None
                            except Exception:
                                modal = None
                            if modal is None:
                                mods = page.locator(MODAL_ROOT_SEL)
                                modal = mods.last if mods and mods.count() > 0 else None

                            if modal is None or not modal.is_visible():
                                missed += 1
                                log_ing(f"  • {t}: (could not resolve modal root)")
                                close_modal_fast(page)
                                continue

                            ing_text = extract_ingredients_from_modal(modal)
                            close_modal_fast(page)

                        if not ing_text:
                            missed += 1
                            log_ing(f"  • {t}: (no ingredients)")
                            continue

                        for i in idxs:
                            meals[i]["ingredients"] = ing_text

                        updated += 1
                        preview = ", ".join(ing_text.split(",")[:4]) + ("..." if len(ing_text.split(",")) > 4 else "")
                        speed = "fast" if not opened_modal else "modal"
                        log_ing(f"  • {t}: {len(ing_text.split(','))} ingredients [{preview}] ({speed})")

                    except Exception:
                        missed += 1
                        close_modal_fast(page)
                    finally:
                        if time.perf_counter() - t0 > PER_ITEM_BUDGET_SEC:
                            log_ing("    ⏱️ skipping slow item")
                            close_modal_fast(page)
                        page.wait_for_timeout(25)

                        processed_in_meal += 1
                        if processed_in_meal % RELOAD_EVERY_N_ITEMS == 0:
                            try:
                                page.reload(wait_until="domcontentloaded", timeout=12000)
                                click_meal_tab(page, meal_label)
                                page.wait_for_timeout(200)
                                snapshot = snapshot_cards_with_titles(page)
                            except Exception:
                                pass

                log_ing(f"-- Summary {meal_label}: updated {updated}, skipped {skipped}, missed {missed}")

        finally:
            context.close()
            browser.close()



#--------------------------------------------------------------------------------------

def main():
    meals = scrape_all_meals()
    out_path = pathlib.Path("data")
    out_path.mkdir(exist_ok=True)
    out_file = out_path / "meals.json"
    out_file.write_text(json.dumps(meals, indent=2, ensure_ascii=False), encoding="utf-8")

    if not IN_FILE.exists():
        print(f"❌ {IN_FILE} not found. Run your main scraper first.")
        sys.exit(1)
    try:
        meals = json.loads(IN_FILE.read_text(encoding="utf-8"))
    except Exception:
        print("❌ Could not parse JSON in meals.json")
        sys.exit(1)
    if not isinstance(meals, list):
        print("❌ Expected JSON array")
        sys.exit(1)

    t0 = time.perf_counter()
    update_dietary_fast(meals)
    dt = time.perf_counter() - t0
    log(f"\n⏱️ dietary update in {dt:.1f}s")

    OUT_FILE.parent.mkdir(exist_ok=True)
    OUT_FILE.write_text(json.dumps(meals, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"✅ Wrote {OUT_FILE}")

    print(f"✅ Wrote {len(meals)} meals to {out_file}")

    if not IN_FILE_ING.exists():
        print(f"❌ {IN_FILE_ING} not found.")
        sys.exit(1)
    try:
        meals = json.loads(IN_FILE_ING.read_text(encoding="utf-8"))
    except Exception:
        print("❌ Could not parse JSON in input file.")
        sys.exit(1)
    log_ing(f"Loaded {len(meals)} meals.")
    update_ingredients_targeted(meals)
    OUT_FILE_ING.write_text(json.dumps(meals, ensure_ascii=False, indent=2), encoding="utf-8")
    log_ing(f"\n✅ Saved updated file to {OUT_FILE_ING}")

if __name__ == "__main__":
    main()
