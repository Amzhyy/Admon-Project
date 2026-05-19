"""
Motor OSINT v3 — Escaneo de identidad digital multi-fuente.

Fuentes de brechas implementadas (6):
  1. XposedOrNot        — Email en brechas conocidas (por nombre)
  2. HIBP Pwned Passwords — Hash/contraseña en colecciones filtradas (k-anonimato)
  3. Proxynova COMB     — 3,200M pares credential:hash de colecciones masivas
  4. EmailRep.io        — Reputación + flags de brecha + plataformas registradas
  5. HudsonRock Cavalier— Presencia en logs de infostealers (malware de robo)
  6. LeakCheck.io       — Base de datos de brechas independiente (endpoint público)

Descubrimiento de cuentas cercanas:
  - Red social de GitHub (following/followers → usernames relacionados)
  - Extracción de @menciones de bios y descripciones de perfiles
  - EmailRep profiles → plataformas en las que el email está registrado
  - Variantes de email (Gmail dot-trick, alias +tag)
  - Cross-scan de usernames relacionados en plataformas rápidas
"""

import concurrent.futures
import hashlib
import json
import math
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ── Tipos de nodo ─────────────────────────────────────────────────────────────
class NodeType(Enum):
    SEED         = "seed"
    EMAIL        = "email"
    USERNAME     = "username"
    ACCOUNT      = "account"
    NEARBY       = "nearby"        # Cuenta relacionada (no confirmada como mismo usuario)
    REAL_NAME    = "real_name"
    LOCATION     = "location"
    WEBSITE      = "website"
    BREACH       = "breach"
    STEALER      = "stealer"       # Log de infostealer (HudsonRock)
    ORGANIZATION = "organization"
    PHONE        = "phone"


NODE_COLORS = {
    NodeType.SEED:         "#FFFFFF",
    NodeType.EMAIL:        "#3FE0C5",
    NodeType.USERNAME:     "#F59E0B",
    NodeType.ACCOUNT:      "#3B82F6",
    NodeType.NEARBY:       "#60A5FA",   # Azul más claro
    NodeType.BREACH:       "#EF4444",
    NodeType.STEALER:      "#FF6B6B",   # Rojo coral — infostealer
    NodeType.REAL_NAME:    "#A78BFA",
    NodeType.LOCATION:     "#10B981",
    NodeType.WEBSITE:      "#F97316",
    NodeType.ORGANIZATION: "#06B6D4",
    NodeType.PHONE:        "#EC4899",
}

# Iconos por tipo de nodo — ASCII puro para garantizar renderizado en cualquier fuente.
# Para nodos ACCOUNT, se usa la abreviación de plataforma (ver PLATFORM_ABBREVS).
NODE_ICONS = {
    NodeType.SEED:         "*",
    NodeType.EMAIL:        "@",
    NodeType.USERNAME:     "U",
    NodeType.ACCOUNT:      "A",   # Sobreescrito con PLATFORM_ABBREVS al pintar
    NodeType.NEARBY:       "~",
    NodeType.BREACH:       "!",
    NodeType.STEALER:      "X",
    NodeType.REAL_NAME:    "N",
    NodeType.LOCATION:     "L",
    NodeType.WEBSITE:      "W",
    NodeType.ORGANIZATION: "O",
    NodeType.PHONE:        "#",
}

# Abreviaciones de plataforma (1-2 letras). Se dibujan dentro del círculo del nodo ACCOUNT.
# Convención: la 1ra letra mayúscula + 2da minúscula, salvo nombres icónicos (X, in, fb).
PLATFORM_ABBREVS = {
    "github":      "Gh",   "gitlab":      "Gl",   "bitbucket":   "Bb",
    "hackernews":  "HN",   "npm":         "np",   "pypi":        "Py",
    "replit":      "Rp",   "codepen":     "CP",   "devto":       "Dv",
    "hashnode":    "Hn",   "stackoverflow":"SO",
    "reddit":      "R",    "twitter":     "X",    "instagram":   "Ig",
    "tiktok":      "Tk",   "youtube":     "Yt",   "twitch":      "Tw",
    "pinterest":   "Pn",   "tumblr":      "Tm",   "mastodon":    "Md",
    "threads":     "Th",   "facebook":    "fb",   "snapchat":    "Sc",
    "deviantart":  "DA",   "behance":     "Be",   "dribbble":    "Db",
    "artstation":  "AS",   "soundcloud":  "SC",   "bandcamp":    "Bc",
    "vimeo":       "Vm",   "flickr":      "Fl",   "spotify":     "Sp",
    "lastfm":      "LF",
    "steam":       "St",   "kick":        "Kk",   "roblox":      "Rb",
    "linkedin":    "in",   "medium":      "Me",   "substack":    "Ss",
    "keybase":     "Kb",   "linktree":    "Lt",   "patreon":     "Pt",
    "aboutme":     "Am",   "cashapp":     "$",    "gravatar":    "Gr",
    "telegram":    "Tg",
}



class RiskLevel(Enum):
    CRITICAL = "Crítico"
    HIGH     = "Alto"
    MEDIUM   = "Medio"
    LOW      = "Bajo"
    INFO     = "Info"


RISK_COLORS = {
    RiskLevel.CRITICAL: "#EF4444",
    RiskLevel.HIGH:     "#F59E0B",
    RiskLevel.MEDIUM:   "#3B82F6",
    RiskLevel.LOW:      "#10B981",
    RiskLevel.INFO:     "#6B7280",
}


@dataclass
class OsintNode:
    id: str
    type: NodeType
    label: str
    platform: str = ""
    url: str = ""
    details: dict = field(default_factory=dict)
    risk: RiskLevel = RiskLevel.INFO

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, OsintNode) and self.id == other.id


@dataclass
class OsintEdge:
    source_id: str
    target_id: str
    label: str = ""
    color: str = "#555555"
    dashed: bool = False


@dataclass
class OsintReport:
    seed: str
    nodes: list
    edges: list
    scan_time: float = 0.0
    total_checked: int = 0
    platforms_found: int = 0
    breaches_found: int = 0


# ── Catálogo de plataformas (39) ───────────────────────────────────────────────
PLATFORMS = [
    # === Desarrollo ===
    {"id": "github",      "name": "GitHub",        "url": "https://github.com/{}",                       "not_found": ["Not Found"], "api": True, "timeout": 8},
    {"id": "gitlab",      "name": "GitLab",        "url": "https://gitlab.com/{}",                       "not_found": ["couldn't find"]},
    {"id": "bitbucket",   "name": "Bitbucket",     "url": "https://bitbucket.org/{}",                    "not_found": ["We couldn't find"]},
    {"id": "hackernews",  "name": "HackerNews",    "url": "https://news.ycombinator.com/user?id={}",     "not_found": ["No such user"], "timeout": 5},
    {"id": "npm",         "name": "npm",           "url": "https://www.npmjs.com/~{}",                   "not_found": ["not found", "404"]},
    {"id": "pypi",        "name": "PyPI",          "url": "https://pypi.org/user/{}/",                   "not_found": ["404", "Not Found"]},
    {"id": "replit",      "name": "Replit",        "url": "https://replit.com/@{}",                      "not_found": ["not found"]},
    {"id": "codepen",     "name": "CodePen",       "url": "https://codepen.io/{}",                       "not_found": ["not found", "404"]},
    {"id": "devto",       "name": "Dev.to",        "url": "https://dev.to/{}",                           "not_found": ["404", "not found"]},
    {"id": "hashnode",    "name": "Hashnode",      "url": "https://hashnode.com/@{}",                    "not_found": ["not found"]},
    # === Social ===
    {"id": "reddit",      "name": "Reddit",        "url": "https://www.reddit.com/user/{}",              "not_found": ["nobody on reddit goes by that name", "Sorry, nobody", "not found"]},
    {"id": "twitter",     "name": "Twitter/X",     "url": "https://twitter.com/{}",                      "not_found": ["doesn't exist", "account_not_found", "Hmm...this page"]},
    {"id": "instagram",   "name": "Instagram",     "url": "https://www.instagram.com/{}/",               "not_found": ["Sorry, this page"]},
    {"id": "tiktok",      "name": "TikTok",        "url": "https://www.tiktok.com/@{}",                  "not_found": ["Couldn't find this account", "page not found", "couldn't find"]},
    {"id": "youtube",     "name": "YouTube",       "url": "https://www.youtube.com/@{}",                 "not_found": ["not found"]},
    {"id": "twitch",      "name": "Twitch",        "url": "https://www.twitch.tv/{}",                    "not_found": ["Sorry. Unless you've got a time machine", "doesn't stream here"]},
    {"id": "pinterest",   "name": "Pinterest",     "url": "https://www.pinterest.com/{}",                "not_found": ["not found"]},
    {"id": "tumblr",      "name": "Tumblr",        "url": "https://{}.tumblr.com",                       "not_found": ["There's nothing here"]},
    {"id": "mastodon",    "name": "Mastodon",      "url": "https://mastodon.social/@{}",                 "not_found": ["not found"]},
    {"id": "threads",     "name": "Threads",       "url": "https://www.threads.net/@{}",                 "not_found": ["not found", "Sorry, this page", "doesn't exist"]},
    # === Creativo ===
    {"id": "deviantart",  "name": "DeviantArt",    "url": "https://www.deviantart.com/{}",               "not_found": ["not found", "does not exist"]},
    {"id": "behance",     "name": "Behance",       "url": "https://www.behance.net/{}",                  "not_found": ["not found"]},
    {"id": "dribbble",    "name": "Dribbble",      "url": "https://dribbble.com/{}",                     "not_found": ["Whoops", "not found"]},
    {"id": "artstation",  "name": "ArtStation",    "url": "https://www.artstation.com/{}",               "not_found": ["not found"]},
    {"id": "soundcloud",  "name": "SoundCloud",    "url": "https://soundcloud.com/{}",                   "not_found": ["We can't find that user", "not found"]},
    {"id": "bandcamp",    "name": "Bandcamp",      "url": "https://{}.bandcamp.com",                     "not_found": ["not found", "Sorry, that something"]},
    {"id": "vimeo",       "name": "Vimeo",         "url": "https://vimeo.com/{}",                        "not_found": ["Page Not Found"]},
    {"id": "flickr",      "name": "Flickr",        "url": "https://www.flickr.com/people/{}/",           "not_found": ["page not found"]},
    # === Gaming ===
    {"id": "steam",       "name": "Steam",         "url": "https://steamcommunity.com/id/{}",            "not_found": ["The specified profile could not be found", "error_ctn"]},
    {"id": "kick",        "name": "Kick",          "url": "https://kick.com/{}",                         "not_found": ["not found", "404"]},
    # === Profesional ===
    {"id": "linkedin",    "name": "LinkedIn",      "url": "https://www.linkedin.com/in/{}",              "not_found": ["Page Not Found", "This page doesn't exist"]},
    {"id": "medium",      "name": "Medium",        "url": "https://medium.com/@{}",                      "not_found": ["PAGE NOT FOUND"]},
    {"id": "substack",    "name": "Substack",      "url": "https://substack.com/@{}",                    "not_found": ["not found"]},
    # === Identidad ===
    {"id": "keybase",     "name": "Keybase",       "url": "https://keybase.io/{}",                       "not_found": ["Not found", "404"]},
    {"id": "linktree",    "name": "Linktree",      "url": "https://linktr.ee/{}",                        "not_found": ["not found", "404", "page doesn't exist"]},
    {"id": "patreon",     "name": "Patreon",       "url": "https://www.patreon.com/{}",                  "not_found": ["Sorry, we couldn't find"]},
    {"id": "aboutme",     "name": "About.me",      "url": "https://about.me/{}",                         "not_found": ["not found"]},
    {"id": "cashapp",     "name": "Cash App",      "url": "https://cash.app/${}",                        "not_found": ["not found"]},
    {"id": "gravatar",    "name": "Gravatar",      "email_only": True},
    # === Adicionales ===
    {"id": "telegram",      "name": "Telegram",      "url": "https://t.me/{}",                              "not_found": ["not found"]},
    {"id": "snapchat",      "name": "Snapchat",      "url": "https://www.snapchat.com/add/{}",              "not_found": ["not found", "Sorry"]},
    {"id": "facebook",      "name": "Facebook",      "url": "https://www.facebook.com/{}",                  "not_found": ["Sorry, this content"]},
    {"id": "spotify",       "name": "Spotify",       "url": "https://open.spotify.com/user/{}",             "not_found": ["not found", "couldn't find"]},
    {"id": "lastfm",        "name": "Last.fm",       "url": "https://www.last.fm/user/{}",                  "not_found": ["not found", "User not found"]},
    {"id": "roblox",        "name": "Roblox",        "url": "https://www.roblox.com/user.aspx?username={}", "not_found": ["not found", "Page cannot be found"]},
    {"id": "stackoverflow", "name": "Stack Overflow","url": "https://stackoverflow.com/users/{}",           "not_found": ["Page Not Found"]},
]

# Plataformas rápidas para escaneo de cuentas cercanas (username variants)
_QUICK_PLATFORMS = [
    p for p in PLATFORMS
    if p["id"] in ("github", "gitlab", "reddit", "twitter", "hackernews", "keybase", "devto", "medium", "linktree")
]

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
    "Gecko/20100101 Firefox/124.0"
)


def _http_get(
    url: str,
    timeout: int = 7,
    extra_headers: dict | None = None,
    retries: int = 1,
) -> tuple:
    """
    HTTP GET seguro con reintentos automáticos.

    - Reintentos configurables (default 1) con backoff exponencial.
    - Decodifica gzip/deflate automáticamente.
    - Los errores HTTP 4xx son definitivos (no se reintentan).
    - Los errores de red, timeout y 5xx sí se reintentan.

    Returns:
        (status_code: int|None, content: str)
    """
    import gzip as _gz
    import zlib as _zl

    headers = {
        "User-Agent": _UA,
        "Accept": "text/html,application/xhtml+xml,application/json,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }
    if extra_headers:
        headers.update(extra_headers)

    last_status: int | None = None
    last_content: str = ""

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                enc = resp.headers.get("Content-Encoding", "").lower()

                # Descomprimir si es necesario
                try:
                    if enc == "gzip":
                        raw = _gz.decompress(raw)
                    elif enc in ("deflate", "zlib"):
                        raw = _zl.decompress(raw)
                except Exception:
                    pass  # fallback al raw original

                try:
                    content = raw.decode("utf-8")
                except UnicodeDecodeError:
                    content = raw.decode("latin-1", errors="ignore")

                return resp.status, content

        except urllib.error.HTTPError as e:
            # 4xx: definitivo. 429/503/502: reintentable
            body = ""
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                pass
            if e.code in (429, 503, 502, 504) and attempt < retries:
                wait = 1.5 * (attempt + 1)
                time.sleep(wait)
                last_status, last_content = e.code, body
                continue
            return e.code, body

        except urllib.error.URLError:
            # Sin conexión, DNS fallo, etc.
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
                continue
            return None, ""

        except TimeoutError:
            if attempt < retries:
                time.sleep(0.3)
                continue
            return None, ""

        except Exception:
            if attempt < retries:
                time.sleep(0.4 * (attempt + 1))
                continue
            return None, ""

    return last_status, last_content




# ── Extracción de metadatos ────────────────────────────────────────────────────
_META_PATTERNS = {
    "avatar_url": [
        r'property="og:image"\s+content="(https?://[^"]{10,300})"',
        r'"avatar_url"\s*:\s*"(https?://[^"]{10,300})"',
        r'"profileImage"\s*:\s*"(https?://[^"]{10,300})"',
        r'"image"\s*:\s*"(https?://[^"]{10,300}\.(?:jpg|jpeg|png|webp))"',
    ],
    "name": [
        r'"name"\s*:\s*"([^"]{2,60})"',
        r'property="og:title"\s+content="([^"]+)"',
        r'"displayName"\s*:\s*"([^"]{2,60})"',
        r'"full_name"\s*:\s*"([^"]{2,60})"',
        r'<title>([^|<>·]{3,40})\s*[\|·]',
    ],
    "bio": [
        r'property="og:description"\s+content="([^"]{10,300})"',
        r'"bio"\s*:\s*"([^"]{5,300})"',
        r'"description"\s*:\s*"([^"]{5,300})"',
        r'<meta name="description"\s+content="([^"]{5,300})"',
    ],
    "location": [
        r'"location"\s*:\s*"([^"]{2,80})"',
        r'"city"\s*:\s*"([^"]{2,40})"',
        r'class="[^"]*location[^"]*"[^>]*>\s*([^<]{2,40})<',
    ],
    "website": [
        r'"blog"\s*:\s*"(https?://[^"]{4,150})"',
        r'"website"\s*:\s*"(https?://[^"]{4,150})"',
        r'"url"\s*:\s*"(https?://[^"]{4,150})"',
        r'rel="me"\s+href="(https?://[^"]{4,150})"',
    ],
    "company": [
        r'"company"\s*:\s*"([^"]{2,80})"',
        r'"organization"\s*:\s*"([^"]{2,80})"',
    ],
}


def _extract_metadata(content: str, username: str) -> dict:
    meta: dict = {}
    for key, patterns in _META_PATTERNS.items():
        for pattern in patterns:
            m = re.search(pattern, content, re.IGNORECASE)
            if m:
                val = m.group(1).strip()
                if val and val.lower() not in (username.lower(), "null", "undefined", "none", ""):
                    meta[key] = val[:200]
                    break
    return meta


def _extract_mentions(texts: list[str]) -> list[str]:
    """Extrae @usernames de bios/descripciones. Filtra palabras comunes."""
    _IGNORE = {"mention", "follow", "contact", "email", "me", "us", "you",
                "everyone", "admin", "support", "team", "official", "account"}
    found: set[str] = set()
    for text in texts:
        for m in re.finditer(r'@([a-zA-Z0-9_]{2,30})', text or ""):
            un = m.group(1).lower()
            if un not in _IGNORE:
                found.add(un)
    return list(found)[:15]


# ── 1. XposedOrNot ────────────────────────────────────────────────────────────
def _check_xposed(email: str) -> list[str]:
    """Retorna lista de nombres de brechas donde aparece el email."""
    url = f"https://api.xposedornot.com/v1/check-email/{email}"
    status, content = _http_get(url, timeout=8,
                                extra_headers={"Referer": "https://xposedornot.com/"})
    if status != 200 or not content:
        return []
    try:
        data = json.loads(content)
        raw = data.get("breaches", [[]])
        return list(raw[0]) if raw and raw[0] else []
    except Exception:
        return []


# ── 2. HIBP Pwned Passwords (k-anonimato) ─────────────────────────────────────
def _check_hibp(text: str) -> tuple[bool, int]:
    """Verifica si una contraseña/hash aparece en HIBP (solo envía 5 chars del hash)."""
    sha1 = hashlib.sha1(text.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    status, content = _http_get(
        f"https://api.pwnedpasswords.com/range/{prefix}",
        timeout=6,
        extra_headers={"User-Agent": "OSINT-Research-Scanner/3.0"},
    )
    if status != 200 or not content:
        return False, 0
    for line in content.splitlines():
        parts = line.split(":")
        if len(parts) == 2 and parts[0] == suffix:
            return True, int(parts[1])
    return False, 0


# ── 3. Proxynova COMB (3,200M credentials) ────────────────────────────────────
def _check_proxynova(email: str) -> dict:
    """
    Consulta el COMB (Collection of Many Breaches) via Proxynova.
    Retorna {count, sample_hashes} si encuentra coincidencias.
    """
    url = f"https://api.proxynova.com/comb?query={email}"
    status, content = _http_get(url, timeout=10,
                                extra_headers={"Origin": "https://www.proxynova.com",
                                               "Referer": "https://www.proxynova.com/"})
    if status != 200 or not content:
        return {}
    try:
        data = json.loads(content)
        count = data.get("count", 0)
        if count == 0:
            return {}
        lines = data.get("lines", [])
        # Extraer solo hashes (nunca contraseñas en texto claro)
        hashes = []
        for line in lines[:5]:
            parts = line.split(":")
            if len(parts) >= 2:
                h = ":".join(parts[1:])
                if len(h) >= 20:   # Parece un hash, no texto plano
                    hashes.append(h[:40])
        return {"count": count, "hashes": hashes}
    except Exception:
        return {}


# ── 4. EmailRep.io (reputación + plataformas) ─────────────────────────────────
def _check_emailrep(email: str) -> dict:
    """
    EmailRep.io: reputación del email + flags de brecha + lista de plataformas.
    El campo 'profiles' es valioso: lista directa de servicios donde está registrado.
    """
    url = f"https://emailrep.io/{email}"
    status, content = _http_get(url, timeout=8,
                                extra_headers={"Key": "",
                                               "Accept": "application/json"})
    if status != 200 or not content:
        return {}
    try:
        d = json.loads(content)
        details = d.get("details", {})
        return {
            "reputation":          d.get("reputation", "unknown"),
            "suspicious":          d.get("suspicious", False),
            "references":          d.get("references", 0),
            "blacklisted":         details.get("blacklisted", False),
            "credentials_leaked":  details.get("credentials_leaked", False),
            "data_breach":         details.get("data_breach", False),
            "malicious_activity":  details.get("malicious_activity", False),
            "first_seen":          details.get("first_seen", ""),
            "last_seen":           details.get("last_seen", ""),
            "profiles":            details.get("profiles", []),  # ← Gold: plataformas registradas
            "free_provider":       details.get("free_provider", True),
            "disposable":          details.get("disposable", False),
        }
    except Exception:
        return {}


# ── 5. HudsonRock Cavalier (infostealers) ─────────────────────────────────────
def _check_hudsonrock(email: str) -> dict:
    """
    HudsonRock Cavalier: comprueba si el email aparece en logs de infostealers.
    Los infostealers son malware que roban credenciales de navegadores y apps.
    Un resultado positivo indica compromiso activo de alto riesgo.
    """
    url = (
        f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools"
        f"/search-by-email?email={email}"
    )
    status, content = _http_get(url, timeout=10,
                                extra_headers={"Origin": "https://cavalier.hudsonrock.com"})
    if status != 200 or not content:
        return {}
    try:
        d = json.loads(content)
        count = d.get("stealerlogsCount", 0)
        if count == 0:
            return {}
        computers = d.get("data", {}).get("computers", [])
        # Extraer solo información de riesgo (no credenciales completas)
        malware_paths = []
        for c in computers[:3]:
            path = c.get("malware_path", "")
            date = c.get("date_uploaded", "")
            if path or date:
                malware_paths.append({"path": path[:80], "date": date[:10]})
        return {"count": count, "malware_info": malware_paths}
    except Exception:
        return {}


# ── 6. LeakCheck.io (endpoint público limitado) ───────────────────────────────
def _check_leakcheck(email: str) -> dict:
    """
    LeakCheck.io endpoint público — verifica presencia en su base de brechas.
    Sin API key solo retorna si existe o no (no los detalles).
    """
    url = f"https://leakcheck.io/api/public?check={email}"
    status, content = _http_get(url, timeout=8,
                                extra_headers={"Referer": "https://leakcheck.io/"})
    if status != 200 or not content:
        return {}
    try:
        d = json.loads(content)
        if d.get("success") and d.get("found", 0) > 0:
            return {
                "found": d["found"],
                "sources": d.get("sources", [])[:8],
            }
        return {}
    except Exception:
        return {}


# ── Gravatar ──────────────────────────────────────────────────────────────────
def _check_gravatar(email: str) -> dict | None:
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    status, _ = _http_get(f"https://www.gravatar.com/avatar/{h}?d=404&s=200", timeout=5)
    if status != 200:
        return None
    result: dict = {"hash": h, "avatar_url": f"https://www.gravatar.com/avatar/{h}?s=200"}
    status2, content = _http_get(f"https://www.gravatar.com/{h}.json", timeout=6)
    if status2 == 200 and content:
        try:
            entry = json.loads(content).get("entry", [{}])[0]
            dn = entry.get("displayName", "")
            if not dn:
                n = entry.get("name", {})
                dn = n.get("formatted", "") if isinstance(n, dict) else str(n)
            if dn:
                result["name"] = dn
            if entry.get("currentLocation"):
                result["location"] = entry["currentLocation"]
            if entry.get("aboutMe"):
                result["bio"] = entry["aboutMe"][:200]
            linked = [
                {"platform": a.get("shortname", ""), "url": a.get("url", "")}
                for a in entry.get("accounts", []) if a.get("url")
            ]
            if linked:
                result["linked_accounts"] = linked
            urls = [u.get("value", "") for u in entry.get("urls", []) if u.get("value")]
            if urls:
                result["urls"] = urls
        except Exception:
            pass
    return result


# ── GitHub API ─────────────────────────────────────────────────────────────────
def _enrich_github(username: str) -> dict | None:
    status, content = _http_get(
        f"https://api.github.com/users/{username}",
        timeout=8,
        extra_headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "curl/8.0"},
    )
    if status != 200 or not content:
        return None
    try:
        d = json.loads(content)
        if d.get("message") == "Not Found":
            return None
        return {
            "name":         d.get("name", ""),
            "bio":          d.get("bio", ""),
            "location":     d.get("location", ""),
            "email":        d.get("email", ""),
            "website":      d.get("blog", ""),
            "company":      d.get("company", ""),
            "twitter":      d.get("twitter_username", ""),
            "public_repos": d.get("public_repos", 0),
            "followers":    d.get("followers", 0),
            "avatar_url":   d.get("avatar_url", ""),
            "created_at":   (d.get("created_at") or "")[:10],
        }
    except Exception:
        return None


# ── GitHub: Red Social (cuentas cercanas) ─────────────────────────────────────
def _find_github_network(username: str, max_per_type: int = 20) -> dict:
    """
    Obtiene following y followers de GitHub para descubrir usernames relacionados.
    El 'following' es más valioso: son personas que el objetivo eligió seguir.
    """
    result = {"following": [], "followers": []}
    for rel_type in ("following", "followers"):
        url = (
            f"https://api.github.com/users/{username}/{rel_type}"
            f"?per_page={max_per_type}"
        )
        status, content = _http_get(
            url, timeout=8,
            extra_headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "curl/8.0"},
        )
        if status == 200 and content:
            try:
                users = json.loads(content)
                result[rel_type] = [u.get("login", "") for u in users if u.get("login")]
            except Exception:
                pass
    return result


# ── Generador de variantes de username ────────────────────────────────────────
def _generate_variants(username: str) -> list[str]:
    base = re.sub(r"[^a-z0-9]", "", username.lower())
    seen = {base}
    variants = [base]

    def add(v: str):
        v = str(v)
        if v and v not in seen and 2 <= len(v) <= 30:
            seen.add(v)
            variants.append(v)

    for sep in ["_", ".", "-"]:
        add(f"{base}{sep}x")
        add(f"the{sep}{base}")
        add(f"{base}{sep}real")
        add(f"{base}{sep}oficial")

    for n in ["1", "2", "99", "123", "2024", "2025"]:
        add(f"{base}{n}")

    leet = base.replace("a", "4").replace("e", "3").replace("o", "0").replace("i", "1")
    if leet != base:
        add(leet)

    # Sin vocales (usuario_sn → usrsn)
    no_vowels = re.sub(r"[aeiou]", "", base)
    if len(no_vowels) >= 3:
        add(no_vowels)

    return variants[:15]


# ── Variantes de email (Gmail dot-trick) ──────────────────────────────────────
def _gmail_variations(email: str) -> list[str]:
    """
    Gmail ignora puntos: john.doe@gmail.com = johndoe@gmail.com.
    Genera las variaciones más comunes para buscar otros registros.
    """
    if "@gmail.com" not in email.lower():
        return []
    local = email.split("@")[0]
    local_clean = local.replace(".", "")
    variations: set[str] = set()
    # Inserta puntos en distintas posiciones
    for i in range(1, len(local_clean)):
        variations.add(f"{local_clean[:i]}.{local_clean[i:]}@gmail.com")
    # Plus-addressing
    for tag in ["work", "personal", "spam", "test", "backup"]:
        variations.add(f"{local_clean}+{tag}@gmail.com")
    variations.discard(email)
    return list(variations)[:8]


# ── Verificación de plataforma ─────────────────────────────────────────────────
def _check_platform(username: str, platform: dict) -> dict | None:
    if platform.get("email_only"):
        return None
    url = platform["url"].format(username)
    status, content = _http_get(url, timeout=platform.get("timeout", 6))
    if status is None or status >= 400:
        return None
    for marker in platform.get("not_found", []):
        if marker.lower() in content.lower():
            return None
    if status == 200:
        return {"url": url, "metadata": _extract_metadata(content, username)}
    return None


# ── Graph Builder ─────────────────────────────────────────────────────────────
class _GraphBuilder:
    def __init__(self):
        self.nodes: dict[str, OsintNode] = {}
        self.edges: list[OsintEdge] = []
        self._edge_set: set[tuple] = set()

    def add_node(self, node: OsintNode) -> OsintNode:
        if node.id not in self.nodes:
            self.nodes[node.id] = node
        return self.nodes[node.id]

    def add_edge(self, src: str, tgt: str, label: str, color: str, dashed: bool = False):
        key = (src, tgt, label)
        if key not in self._edge_set and src in self.nodes and tgt in self.nodes:
            self._edge_set.add(key)
            self.edges.append(OsintEdge(src, tgt, label, color, dashed))

    def report(self, seed: str, t0: float, total_checked: int) -> OsintReport:
        nodes = list(self.nodes.values())
        accounts_found = sum(1 for n in nodes if n.type == NodeType.ACCOUNT)
        breaches_found = sum(1 for n in nodes if n.type in (NodeType.BREACH, NodeType.STEALER))

        # ── Detección de información compartida entre plataformas ─────────────
        # Para cada nodo de metadata (REAL_NAME, LOCATION, WEBSITE, ORGANIZATION,
        # EMAIL), contamos cuántas cuentas distintas convergen en él.
        # Si ≥2 cuentas comparten el mismo atributo → es una CORRELACIÓN
        # cross-platform, dato OSINT de alta confianza.
        CORRELATABLE = {
            NodeType.REAL_NAME, NodeType.LOCATION, NodeType.WEBSITE,
            NodeType.ORGANIZATION, NodeType.EMAIL,
        }
        incoming_accounts: dict[str, set[str]] = {}
        for edge in self.edges:
            tgt = self.nodes.get(edge.target_id)
            src = self.nodes.get(edge.source_id)
            if not tgt or not src:
                continue
            if tgt.type in CORRELATABLE and src.type in (NodeType.ACCOUNT, NodeType.NEARBY):
                incoming_accounts.setdefault(edge.target_id, set()).add(src.id)

        # Marcar nodos correlacionados
        for node in nodes:
            if node.type not in CORRELATABLE:
                continue
            sources = incoming_accounts.get(node.id, set())
            if len(sources) >= 2:
                # Lista de plataformas que comparten este atributo
                platforms = sorted({
                    self.nodes[sid].platform or self.nodes[sid].label
                    for sid in sources if sid in self.nodes
                })
                node.details["correlation_count"] = len(sources)
                node.details["correlated_platforms"] = platforms
                node.risk = RiskLevel.CRITICAL    # Coincidencia confirmada = riesgo crítico
                # Sufijo visible en la etiqueta para identificarlo en el grafo
                if "×" not in node.label:
                    node.label = f"{node.label} ×{len(sources)}"

        return OsintReport(
            seed=seed,
            nodes=nodes,
            edges=self.edges,
            scan_time=time.time() - t0,
            total_checked=total_checked,
            platforms_found=accounts_found,
            breaches_found=breaches_found,
        )


def _attach_metadata(g: _GraphBuilder, account_node: OsintNode, meta: dict, username: str):
    """Convierte metadatos de un perfil en nodos y los agrega al grafo."""
    acc_id = account_node.id

    name = (meta.get("name") or "").strip()
    if name and name.lower() != username.lower() and 2 < len(name) <= 60:
        nid = f"name:{name.lower()[:40]}"
        existing = nid in g.nodes
        g.add_node(OsintNode(nid, NodeType.REAL_NAME, name, risk=RiskLevel.HIGH,
                             details={"source": account_node.platform}))
        g.add_edge(acc_id, nid, "nombre real", "#A78BFA", dashed=existing)

    loc = (meta.get("location") or "").strip()
    if loc and 2 < len(loc) <= 80:
        lid = f"loc:{loc.lower()[:40]}"
        existing = lid in g.nodes
        g.add_node(OsintNode(lid, NodeType.LOCATION, loc, risk=RiskLevel.LOW,
                             details={"source": account_node.platform}))
        g.add_edge(acc_id, lid, "ubicación", "#10B981", dashed=existing)

    web = (meta.get("website") or "").strip()
    if web and web.startswith("http"):
        wid = f"web:{web[:60]}"
        existing = wid in g.nodes
        g.add_node(OsintNode(wid, NodeType.WEBSITE, web[:40], url=web, risk=RiskLevel.LOW,
                             details={"source": account_node.platform}))
        g.add_edge(acc_id, wid, "sitio web", "#F97316", dashed=existing)

    comp = (meta.get("company") or "").strip()
    if comp and 2 < len(comp) <= 80:
        cid = f"org:{comp.lower()[:40]}"
        existing = cid in g.nodes
        g.add_node(OsintNode(cid, NodeType.ORGANIZATION, comp, risk=RiskLevel.LOW,
                             details={"source": account_node.platform}))
        g.add_edge(acc_id, cid, "organización", "#06B6D4", dashed=existing)


# ─────────────────────────────────────────────────────────────────────────────
#  FUNCIÓN PRINCIPAL DE ESCANEO
# ─────────────────────────────────────────────────────────────────────────────
def scan(
    target: str,
    progress_cb=None,
    node_cb=None,
    max_workers: int = 20,
) -> OsintReport:
    """
    Escanea un objetivo (email, username o hash SHA-1/MD5/SHA-256).

    Flujo para EMAIL:
      1. Extrae username del email
      2. Verifica 6 fuentes de brechas en paralelo
      3. Consulta Gravatar (email → identidad visual)
      4. Escanea 39 plataformas por username (concurrente)
      5. Enriquece GitHub con API oficial
      6. Busca red social de GitHub (following/followers)
      7. Extrae @menciones de bios encontradas
      8. Usa perfiles de EmailRep para verificar plataformas adicionales
      9. Escanea variantes de username en plataformas rápidas

    Flujo para USERNAME:
      Pasos 4–9 (sin brechas de email)

    Flujo para HASH:
      Solo HIBP (k-anonimato)
    """
    t0 = time.time()
    g = _GraphBuilder()

    def notify(msg: str):
        if progress_cb:
            progress_cb(msg)

    def emit(node: OsintNode):
        if node_cb:
            node_cb(node)

    target = target.strip()
    is_email = "@" in target and "." in target.split("@")[-1]
    is_hash = (
        len(target) in (32, 40, 64)
        and " " not in target
        and all(c in "0123456789abcdefABCDEF" for c in target)
    )

    # Inicializar variables que se usan después del bloque `if is_email`
    # para evitar UnboundLocalError cuando el objetivo es username/hash.
    emailrep_platforms: list[str] = []


    seed_type = NodeType.EMAIL if is_email else (NodeType.REAL_NAME if is_hash else NodeType.SEED)
    seed = g.add_node(OsintNode(
        id=f"seed:{target}",
        type=seed_type,
        label=target if len(target) < 35 else target[:33] + "…",
        risk=RiskLevel.INFO,
        details={"input": target},
    ))

    username = target.split("@")[0] if is_email else target

    # ─── HASH: solo HIBP ────────────────────────────────────────────────────
    if is_hash:
        notify("Verificando hash en HIBP…")
        found, count = _check_hibp(target)
        if found:
            bn = g.add_node(OsintNode(
                id=f"breach:hibp:{target[:16]}",
                type=NodeType.BREACH,
                label=f"HIBP ×{count:,}",
                platform="Have I Been Pwned",
                url="https://haveibeenpwned.com",
                risk=RiskLevel.CRITICAL,
                details={"count": count, "hash": target},
            ))
            g.add_edge(seed.id, bn.id, "hash filtrado", "#EF4444")
            emit(bn)
        return g.report(target, t0, 1)

    # ─── USERNAME: nodo derivado (si viene de email) ─────────────────────────
    if is_email:
        unode = g.add_node(OsintNode(
            id=f"usr:{username}",
            type=NodeType.USERNAME,
            label=username,
            risk=RiskLevel.INFO,
        ))
        g.add_edge(seed.id, unode.id, "username extraído", "#F59E0B")
        emit(unode)
        parent_id = unode.id

        # ── FASE 1: Brechas en paralelo (6 fuentes) ────────────────────────
        notify("Consultando 6 fuentes de brechas…")
        breach_futures: dict = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as bex:
            breach_futures["xposed"]     = bex.submit(_check_xposed, target)
            breach_futures["proxynova"]  = bex.submit(_check_proxynova, target)
            breach_futures["emailrep"]   = bex.submit(_check_emailrep, target)
            breach_futures["hudsonrock"] = bex.submit(_check_hudsonrock, target)
            breach_futures["leakcheck"]  = bex.submit(_check_leakcheck, target)
            breach_futures["gravatar"]   = bex.submit(_check_gravatar, target)

        # XposedOrNot — brechas por nombre
        try:
            xposed_list = breach_futures["xposed"].result()
            for breach_name in xposed_list:
                bn = g.add_node(OsintNode(
                    id=f"breach:xposed:{breach_name.lower()[:30]}",
                    type=NodeType.BREACH,
                    label=breach_name,
                    platform="XposedOrNot",
                    url="https://xposedornot.com",
                    risk=RiskLevel.CRITICAL,
                    details={"email": target, "source": "XposedOrNot"},
                ))
                g.add_edge(seed.id, bn.id, "brecha de datos", "#EF4444")
                emit(bn)
            if xposed_list:
                notify(f"XposedOrNot: {len(xposed_list)} brecha(s)")
        except Exception:
            pass

        # Proxynova COMB
        try:
            comb_data = breach_futures["proxynova"].result()
            if comb_data.get("count", 0) > 0:
                bn = g.add_node(OsintNode(
                    id=f"breach:comb:{target[:20]}",
                    type=NodeType.BREACH,
                    label=f"COMB ×{comb_data['count']}",
                    platform="Proxynova COMB",
                    url="https://www.proxynova.com/tools/comb",
                    risk=RiskLevel.CRITICAL,
                    details={"count": comb_data["count"], "source": "COMB (3.2B records)"},
                ))
                g.add_edge(seed.id, bn.id, "en colección COMB", "#EF4444")
                emit(bn)
                notify(f"COMB: credential encontrada ({comb_data['count']} ocurrencias)")
        except Exception:
            pass

        # EmailRep — reputación + plataformas registradas
        try:
            er = breach_futures["emailrep"].result()
            if er:
                emailrep_platforms = er.get("profiles", [])
                rep = er.get("reputation", "unknown")
                # Nodo de reputación solo si hay datos relevantes
                if er.get("credentials_leaked") or er.get("data_breach") or er.get("suspicious"):
                    bn = g.add_node(OsintNode(
                        id=f"breach:emailrep:{target[:20]}",
                        type=NodeType.BREACH,
                        label=f"EmailRep ({rep})",
                        platform="EmailRep.io",
                        url=f"https://emailrep.io/{target}",
                        risk=RiskLevel.HIGH if not er.get("suspicious") else RiskLevel.CRITICAL,
                        details={k: v for k, v in er.items() if k != "profiles"},
                    ))
                    g.add_edge(seed.id, bn.id, "email comprometido", "#F59E0B")
                    emit(bn)
                if emailrep_platforms:
                    notify(f"EmailRep: plataformas registradas → {', '.join(emailrep_platforms[:5])}")
        except Exception:
            pass

        # HudsonRock — logs de infostealers
        try:
            hr = breach_futures["hudsonrock"].result()
            if hr.get("count", 0) > 0:
                bn = g.add_node(OsintNode(
                    id=f"stealer:hr:{target[:20]}",
                    type=NodeType.STEALER,
                    label=f"Infostealer ×{hr['count']}",
                    platform="HudsonRock Cavalier",
                    url="https://cavalier.hudsonrock.com",
                    risk=RiskLevel.CRITICAL,
                    details={
                        "count": hr["count"],
                        "description": (
                            "Email encontrado en logs de malware infostealer. "
                            "Indica compromiso activo de credenciales en el dispositivo de la víctima."
                        ),
                        "malware_info": hr.get("malware_info", []),
                    },
                ))
                g.add_edge(seed.id, bn.id, "comprometido por malware", "#FF6B6B")
                emit(bn)
                notify(f"⚠ HudsonRock: email en {hr['count']} log(s) de infostealer")
        except Exception:
            pass

        # LeakCheck
        try:
            lc = breach_futures["leakcheck"].result()
            if lc.get("found", 0) > 0:
                sources_label = ", ".join(lc.get("sources", [])[:3])
                bn = g.add_node(OsintNode(
                    id=f"breach:leakcheck:{target[:20]}",
                    type=NodeType.BREACH,
                    label=f"LeakCheck ×{lc['found']}",
                    platform="LeakCheck.io",
                    url="https://leakcheck.io",
                    risk=RiskLevel.HIGH,
                    details={"found": lc["found"], "sources": lc.get("sources", [])},
                ))
                g.add_edge(seed.id, bn.id, f"en brechas ({sources_label})", "#EF4444")
                emit(bn)
        except Exception:
            pass

        # Gravatar
        try:
            gdata = breach_futures["gravatar"].result()
            if gdata:
                gnode = g.add_node(OsintNode(
                    id=f"acc:gravatar:{username}",
                    type=NodeType.ACCOUNT,
                    label="Gravatar",
                    platform="Gravatar",
                    url=f"https://gravatar.com/{gdata['hash']}",
                    risk=RiskLevel.MEDIUM,
                    details=gdata,
                ))
                g.add_edge(seed.id, gnode.id, "perfil en", "#EC4899")
                emit(gnode)
                _attach_metadata(g, gnode, gdata, username)
                for la in gdata.get("linked_accounts", []):
                    if la.get("url") and la.get("platform"):
                        lid = f"acc:grav:{la['platform']}"
                        ln = g.add_node(OsintNode(
                            lid, NodeType.ACCOUNT,
                            la["platform"].capitalize(),
                            platform=la["platform"].capitalize(),
                            url=la["url"],
                            risk=RiskLevel.MEDIUM,
                        ))
                        g.add_edge(gnode.id, lid, "vinculada", "#EC4899")
                        emit(ln)
        except Exception:
            pass

    else:
        parent_id = seed.id

    # ─── FASE 2: Escaneo concurrente de 39 plataformas ──────────────────────
    platforms_to_check = [p for p in PLATFORMS if not p.get("email_only")]
    notify(f"Escaneando {len(platforms_to_check)} plataformas para '{username}'…")

    collected_bios: list[str] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_check_platform, username, p): p for p in platforms_to_check}
        for future in concurrent.futures.as_completed(futures, timeout=50):
            plat = futures[future]
            try:
                result = future.result()
            except Exception:
                continue
            if not result:
                continue

            acc = g.add_node(OsintNode(
                id=f"acc:{plat['id']}:{username}",
                type=NodeType.ACCOUNT,
                label=plat["name"],
                platform=plat["name"],
                url=result["url"],
                risk=RiskLevel.MEDIUM,
                details=result.get("metadata", {}),
            ))
            g.add_edge(parent_id, acc.id, "cuenta en", "#3B82F6")
            _attach_metadata(g, acc, result.get("metadata", {}), username)
            notify(f"✓ {plat['name']}")
            emit(acc)

            bio = result.get("metadata", {}).get("bio", "")
            if bio:
                collected_bios.append(bio)

    # ─── FASE 3: Enriquecimiento GitHub ─────────────────────────────────────
    gh_id = f"acc:github:{username}"
    if gh_id in g.nodes:
        notify("Enriqueciendo GitHub con API oficial…")
        gh_data = _enrich_github(username)
        if gh_data:
            g.nodes[gh_id].details.update(gh_data)
            _attach_metadata(g, g.nodes[gh_id], gh_data, username)
            if gh_data.get("bio"):
                collected_bios.append(gh_data["bio"])

            if gh_data.get("email"):
                eid = f"email:{gh_data['email']}"
                en = g.add_node(OsintNode(eid, NodeType.EMAIL, gh_data["email"],
                                          risk=RiskLevel.HIGH, details={"source": "GitHub"}))
                g.add_edge(gh_id, eid, "email público", "#3FE0C5")
                emit(en)

            if gh_data.get("twitter"):
                tw = gh_data["twitter"]
                tw_id = f"acc:twitter:{tw}"
                if tw_id not in g.nodes:
                    tn = g.add_node(OsintNode(
                        tw_id, NodeType.ACCOUNT, "Twitter/X",
                        platform="Twitter/X",
                        url=f"https://twitter.com/{tw}",
                        risk=RiskLevel.MEDIUM,
                        details={"username": tw, "source": "GitHub"},
                    ))
                    g.add_edge(gh_id, tw_id, "Twitter vinculado", "#3B82F6")
                    emit(tn)

            # ── Red social de GitHub (cuentas cercanas) ──────────────────────
            notify("Analizando red social de GitHub (following/followers)…")
            gh_network = _find_github_network(username, max_per_type=20)

            for related_user in gh_network.get("following", [])[:15]:
                if related_user.lower() == username.lower():
                    continue
                nid = f"nearby:github:following:{related_user}"
                nn = g.add_node(OsintNode(
                    nid, NodeType.NEARBY,
                    f"@{related_user}",
                    platform="GitHub",
                    url=f"https://github.com/{related_user}",
                    risk=RiskLevel.INFO,
                    details={"relationship": "following", "source": "GitHub social graph"},
                ))
                g.add_edge(gh_id, nid, "sigue a", "#60A5FA", dashed=True)
                emit(nn)

            # Solo primeros 5 followers (menos relevantes para identidad)
            for related_user in gh_network.get("followers", [])[:5]:
                if related_user.lower() == username.lower():
                    continue
                nid = f"nearby:github:follower:{related_user}"
                if nid not in g.nodes:
                    nn = g.add_node(OsintNode(
                        nid, NodeType.NEARBY,
                        f"@{related_user}",
                        platform="GitHub",
                        url=f"https://github.com/{related_user}",
                        risk=RiskLevel.INFO,
                        details={"relationship": "follower", "source": "GitHub social graph"},
                    ))
                    g.add_edge(gh_id, nid, "seguido por", "#60A5FA", dashed=True)
                    emit(nn)

            total_network = len(gh_network.get("following", [])) + len(gh_network.get("followers", []))
            if total_network:
                notify(f"Red GitHub: {total_network} cuentas relacionadas encontradas")

    # ─── FASE 4: Cuentas desde EmailRep profiles ────────────────────────────
    if emailrep_platforms:
        notify(f"Verificando plataformas detectadas por EmailRep: {emailrep_platforms}…")
        # Mapa de nombres de EmailRep → IDs de plataforma
        _EMAILREP_MAP = {
            "twitter": "twitter", "spotify": None, "google": None,
            "linkedin": "linkedin", "github": "github", "instagram": "instagram",
            "facebook": None, "pinterest": "pinterest", "reddit": "reddit",
            "medium": "medium", "deviantart": "deviantart", "twitch": "twitch",
        }
        for platform_name in emailrep_platforms:
            plat_id = _EMAILREP_MAP.get(platform_name.lower())
            if not plat_id:
                continue
            existing_id = f"acc:{plat_id}:{username}"
            if existing_id in g.nodes:
                continue   # Ya lo tenemos del scan principal
            # Agregar como sugerencia con riesgo medio
            plat_conf = next((p for p in PLATFORMS if p["id"] == plat_id), None)
            if plat_conf:
                url = plat_conf["url"].format(username)
                en = g.add_node(OsintNode(
                    existing_id, NodeType.ACCOUNT,
                    plat_conf["name"],
                    platform=plat_conf["name"],
                    url=url,
                    risk=RiskLevel.MEDIUM,
                    details={"source": "EmailRep.io profile detection"},
                ))
                g.add_edge(parent_id, en.id, "registrado (EmailRep)", "#3FE0C5", dashed=True)
                emit(en)

    # ─── FASE 5: @menciones en bios ─────────────────────────────────────────
    if collected_bios:
        mentions = _extract_mentions(collected_bios)
        if mentions:
            notify(f"Encontradas {len(mentions)} @menciones en bios — verificando…")
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                mention_futures = {
                    ex.submit(_check_platform, m, p): (m, p)
                    for m in mentions
                    for p in _QUICK_PLATFORMS[:4]
                    if m.lower() != username.lower()
                }
                for fut in concurrent.futures.as_completed(mention_futures, timeout=20):
                    m_user, m_plat = mention_futures[fut]
                    try:
                        res = fut.result()
                    except Exception:
                        continue
                    if not res:
                        continue
                    nid = f"nearby:mention:{m_plat['id']}:{m_user}"
                    nn = g.add_node(OsintNode(
                        nid, NodeType.NEARBY,
                        f"@{m_user}",
                        platform=m_plat["name"],
                        url=res["url"],
                        risk=RiskLevel.INFO,
                        details={"relationship": "bio mention", "source": "bio extract"},
                    ))
                    g.add_edge(parent_id, nn.id, "mencionado en bio", "#60A5FA", dashed=True)
                    emit(nn)

    # ─── FASE 6: Variantes de username ──────────────────────────────────────
    account_count = sum(1 for n in g.nodes.values() if n.type == NodeType.ACCOUNT)
    if account_count < 5:
        notify("Pocos resultados — buscando variantes del username…")
        variants = _generate_variants(username)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            var_futures = {
                ex.submit(_check_platform, v, p): (v, p)
                for v in variants if v != username
                for p in _QUICK_PLATFORMS
            }
            for fut in concurrent.futures.as_completed(var_futures, timeout=25):
                v_user, v_plat = var_futures[fut]
                try:
                    res = fut.result()
                except Exception:
                    continue
                if not res:
                    continue
                var_node_id = f"usr:var:{v_user}"
                if var_node_id not in g.nodes:
                    vn = g.add_node(OsintNode(
                        var_node_id, NodeType.USERNAME,
                        f"@{v_user}",
                        risk=RiskLevel.LOW,
                        details={"variant_of": username},
                    ))
                    g.add_edge(parent_id, var_node_id, "variante", "#F59E0B", dashed=True)

                acc_id2 = f"acc:{v_plat['id']}:{v_user}"
                an = g.add_node(OsintNode(
                    acc_id2, NodeType.ACCOUNT,
                    f"{v_plat['name']} (@{v_user})",
                    platform=v_plat["name"],
                    url=res["url"],
                    risk=RiskLevel.MEDIUM,
                ))
                g.add_edge(var_node_id, acc_id2, "cuenta en", "#3B82F6")
                emit(an)

    return g.report(target, t0, len(platforms_to_check))
