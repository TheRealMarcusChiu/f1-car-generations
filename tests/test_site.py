"""No-dependency verifier for the local F1 timeline build.

Run from the project root:  python3 -m unittest discover -s tests -v
"""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
VERIFIED = "2026-10-19"
THUMB_NOTE = "Wikimedia Commons 1280px thumbnail; no further edits"
STATUS = "public GitHub Pages publication authorized; live URL will be added after deployment verification."

# The six verified sources (id -> URL). The site may not cite anything else.
EXPECTED_SOURCES = {
    "f1-1950-vs-2020": "https://www.formula1.com/en/latest/article/1950-vs-2020-cars-drivers-safety-and-pitstops-how-f1-has-changed-in-70-years.62ITx6LlIY3qgzTctXgz1j",
    "f1-lotus-79": "https://www.formula1.com/en/latest/article/tech-tuesday-the-lotus-79-f1s-ground-effect-marvel.sAD9PXt7mC8iMSwwe6CCw",
    "f1-2014-regs": "https://www.formula1.com/en/latest/article/a-racing-revolution-understanding-2014s-technical-regulations.1bTbN3OAEksY00PVE62KvC",
    "f1-halo-2018": "https://www.formula1.com/en/latest/article/halo-protection-system-to-be-introduced-for-2018.2jhITmhSiwkKwOAWOG0UM6",
    "f1-2022-floors": "https://www.formula1.com/en/latest/article/tech-tuesday-why-ripples-and-curls-adorn-the-floors-of-the-2022-cars.1OHf3EXwhbt521IpbXUtVt",
    "f1-2026-guide": "https://www.formula1.com/en/latest/article/the-beginners-guide-to-the-2026-regulations.6j0tS0hrHG2T01tpmK6XYz",
}

# Milestone id -> source id it must cite.
EXPECTED_MILESTONES = {
    "m-1950": "f1-1950-vs-2020",
    "m-1977": "f1-lotus-79",
    "m-2014": "f1-2014-regs",
    "m-2018": "f1-halo-2018",
    "m-2022": "f1-2022-floors",
    "m-2026": "f1-2026-guide",
}

# Commons title -> (creator substring, license name).
EXPECTED_IMAGES = {
    "File:1950 Alfa Romeo 158 (54834195044).jpg": ("David Merrett", "CC BY 4.0"),
    "File:1959 Cooper Climax T51 Goodwood, 2009 (01).jpg": ("Bahnfrend", "CC BY-SA 4.0"),
    "File:Lotus 25 Jim Clark Donington.jpg": ("John Chapman", "CC BY-SA 3.0"),
    "File:Lotus 79 at Goodwood 2014 001.jpg": ("Nic Redhead", "CC BY-SA 2.0"),
    "File:1988 McLaren-Honda MP4 4 Goodwood, 2009 (01).jpg": ("Bahnfrend", "CC BY-SA 4.0"),
    "File:Car Show Nigel Mansell with His 1992 Williams-Renault FW14B Formula 1 Car.jpg": ("Martin Pettitt", "CC BY 2.0"),
    "File:Michael Schumacher Ferrari 2004.jpg": ("Rick Dikeman", "CC BY-SA 3.0"),
    "File:2009 Brawn BGP 001 Goodwood, 2009 (01).jpg": ("Bahnfrend", "CC BY-SA 4.0"),
    "File:Mercedes F1 W05 Hybrid front-left 2015 Malaysia.jpg": ("Morio", "CC BY-SA 4.0"),
    "File:2022 Red Bull RB18.jpg": ("Calreyn88", "CC0"),
    "File:Alpine A526 of Franco Colapinto (028A8049).jpg": ("Yu Chu Chin", "CC BY-SA 4.0"),
}

# Technical-history claims the verified sources do not support.
UNSUPPORTED = [
    r"monocoque", r"rear[- ]engine", r"mid[- ]engine", r"double[- ]diffuser",
    r"flat[- ]bottom", r"\bbann?(ed|s)?\b", r"\bKERS\b", r"turbo era",
    r"\b1962\b", r"\b1983\b",
]


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text = [], []

    def all_text(self):
        out = list(self.text)
        for c in self.children:
            out.append(c.all_text())
        return " ".join(out)

    def iter(self, tag=None):
        for c in self.children:
            if tag is None or c.tag == tag:
                yield c
            yield from c.iter(tag)


VOID = {"img", "meta", "link", "br", "hr", "input", "source", "area", "base", "col", "wbr"}


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag in ("script", "style"):
            self.skip += 1
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.cur.text.append(data.strip())


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def parse_index():
    b = TreeBuilder()
    b.feed(read("index.html"))
    return b.root


class DataContract(unittest.TestCase):
    def test_sources_json(self):
        sources = json.loads(read("data/sources.json"))
        self.assertEqual(len(sources), 6)
        by_id = {s["id"]: s for s in sources}
        self.assertEqual(set(by_id), set(EXPECTED_SOURCES))
        for sid, url in EXPECTED_SOURCES.items():
            s = by_id[sid]
            self.assertEqual(s["url"], url)
            self.assertEqual(s["publisher"], "Formula 1 (formula1.com)")
            self.assertEqual(s["verified"], VERIFIED)
            for key in ("title", "claim", "caveat"):
                self.assertTrue(s.get(key, "").strip(), f"{sid} missing {key}")

    def test_source_matrix(self):
        matrix = read("research/source-matrix.md")
        self.assertIn(VERIFIED, matrix)
        for sid, url in EXPECTED_SOURCES.items():
            self.assertIn(sid, matrix)
            self.assertIn(url, matrix)

    def test_images_json(self):
        images = json.loads(read("data/images.json"))
        self.assertEqual(len(images), 11)
        self.assertEqual({i["title"] for i in images}, set(EXPECTED_IMAGES))
        for img in images:
            creator, lic = EXPECTED_IMAGES[img["title"]]
            self.assertIn(creator, img["author"])
            self.assertEqual(img["license"], lic)
            for key in ("file", "alt", "model", "context", "author", "license",
                        "licenseUrl", "page", "processing"):
                self.assertTrue(str(img.get(key, "")).strip(), f"{img['title']} missing {key}")
            self.assertTrue(img["page"].startswith("https://commons.wikimedia.org/wiki/File:"))
            self.assertTrue(img["licenseUrl"].startswith("https://creativecommons.org/"),
                            f"{img['title']} license URL must be HTTPS: {img['licenseUrl']}")
            self.assertEqual(img["processing"], THUMB_NOTE)
            path = ROOT / img["file"]
            self.assertTrue(img["file"].startswith("assets/images/"))
            self.assertTrue(path.is_file(), f"missing {path}")
            self.assertGreater(path.stat().st_size, 10_000, f"suspiciously small {path}")
            self.assertEqual(path.read_bytes()[:3], b"\xff\xd8\xff", f"not a JPEG {path}")

    def test_image_dir_matches_json(self):
        images = json.loads(read("data/images.json"))
        on_disk = {f"assets/images/{p.name}" for p in (ROOT / "assets/images").iterdir() if p.is_file()}
        self.assertEqual(on_disk, {i["file"] for i in images})
        self.assertNotIn("Lotus 72", json.dumps(images))

    def test_research_docs(self):
        audit = read("research/image-audit.md")
        self.assertIn("Lotus 72", audit)
        self.assertIn("darker", audit)
        self.assertRegex(audit, r"(?i)model year")
        self.assertRegex(audit, r"(?i)photo (context|year)")
        readme = read("README.md")
        self.assertIn(STATUS, readme)
        self.assertIn(THUMB_NOTE, readme)
        self.assertIn("python3 -m unittest", readme)
        self.assertIn("http.server", readme)


class PageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = parse_index()
        cls.html = read("index.html")
        cls.images = {i["file"]: i for i in json.loads(read("data/images.json"))}

    def test_title_and_scope_statement(self):
        title = next(self.root.iter("title")).all_text()
        self.assertIn("The Shape of Speed", title)
        h1 = next(self.root.iter("h1")).all_text()
        self.assertIn("The Shape of Speed", h1)
        text = self.root.all_text()
        self.assertRegex(text, r"(?i)editorially selected")
        self.assertRegex(text, r"(?i)not an? (official|exhaustive)")
        self.assertIn('lang="en"', self.html)
        self.assertIn('name="viewport"', self.html)

    def test_six_milestones_with_citations(self):
        ms = [n for n in self.root.iter("article") if "milestone" in n.attrs.get("class", "")]
        self.assertEqual(len(ms), 6)
        ids = [m.attrs.get("id") for m in ms]
        self.assertEqual(len(ids), len(set(ids)), "milestone IDs must be unique")
        self.assertEqual(set(ids), set(EXPECTED_MILESTONES))
        for m in ms:
            sid = m.attrs.get("data-source")
            self.assertEqual(sid, EXPECTED_MILESTONES[m.attrs["id"]])
            links = [a for a in m.iter("a") if a.attrs.get("href") == EXPECTED_SOURCES[sid]]
            self.assertTrue(links, f"{m.attrs['id']} lacks visible citation link")
            self.assertTrue(links[0].all_text().strip(), "citation link needs text")

    def test_milestone_wording_guards(self):
        ms = {n.attrs["id"]: n.all_text() for n in self.root.iter("article") if n.attrs.get("id") in EXPECTED_MILESTONES}
        self.assertRegex(ms["m-1950"], r"(?i)representative")
        self.assertRegex(ms["m-1950"], r"(?i)not .*universal|not the (only|standard)")
        self.assertIn("Lotus 79", ms["m-1977"])
        self.assertIn("Andretti", ms["m-1977"])
        self.assertIn("100 kg", ms["m-2014"])
        self.assertNotRegex(ms["m-2014"], r"(?i)\b\d+\s*(bhp|hp|kw)\b")
        self.assertRegex(ms["m-2018"], r"(?i)halo")
        self.assertNotRegex(ms["m-2022"], r"(?i)identical|same as (the )?(19)?70s")
        self.assertIn(EXPECTED_SOURCES["f1-lotus-79"], self._hrefs_in("m-2022"),
                      "'new ground-effect era' framing needs the Lotus 79 citation")
        self.assertRegex(ms["m-2026"], r"(?i)in force")
        self.assertNotRegex(ms["m-2026"], r"(?i)upcoming|will be introduced|proposal")

    def _hrefs_in(self, mid):
        node = next(n for n in self.root.iter("article") if n.attrs.get("id") == mid)
        return {a.attrs.get("href") for a in node.iter("a")}

    def test_no_unsupported_technical_claims(self):
        text = self.root.all_text()
        for pat in UNSUPPORTED:
            self.assertNotRegex(text, re.compile(pat, re.I), f"unsupported claim pattern: {pat}")
        # 1959 / 2009 may appear only inside gallery figure credits/labels.
        non_gallery = " ".join(
            n.all_text() for n in self.root.iter() if n.tag in ("p", "h1", "h2", "h3", "li", "dd", "dt")
            and not self._inside_figure(n)
        )
        self.assertNotRegex(non_gallery, r"\b(1959|2009)\b")

    @staticmethod
    def _inside_figure(n):
        while n is not None:
            if n.tag == "figure":
                return True
            n = n.parent
        return False

    def test_images_are_local_and_credited(self):
        imgs = list(self.root.iter("img"))
        self.assertEqual(len(imgs), 11)
        self.assertEqual({i.attrs["src"] for i in imgs}, set(self.images))
        for img in imgs:
            src = img.attrs["src"]
            self.assertFalse(urlparse(src).scheme or src.startswith("//") or src.startswith("/"),
                             f"non-relative img src {src}")
            self.assertTrue(img.attrs.get("alt", "").strip(), f"{src} needs alt")
            self.assertEqual(img.attrs["alt"], self.images[src]["alt"])
            self.assertTrue(img.attrs.get("width") and img.attrs.get("height"))
        for fig in self.root.iter("figure"):
            img = next(fig.iter("img"))
            meta = self.images[img.attrs["src"]]
            cap = next(fig.iter("figcaption"))
            text = cap.all_text()
            hrefs = {a.attrs.get("href") for a in cap.iter("a")}
            self.assertIn(meta["model"], text)
            self.assertIn(meta["context"], text)
            self.assertIn(meta["author"], text)
            self.assertIn(meta["license"], text)
            self.assertIn(meta["licenseUrl"], hrefs)
            self.assertIn(meta["page"], hrefs)

    def test_no_remote_assets(self):
        css = read("styles.css")
        self.assertNotRegex(css, r"url\(\s*['\"]?(https?:)?//")
        self.assertNotRegex(self.html, r"<img[^>]+src=[\"'](https?:)?//")
        self.assertNotRegex(self.html, r"(?i)upload\.wikimedia|thumb\.wikimedia")

    def test_links_resolve(self):
        ids = {n.attrs["id"] for n in self.root.iter() if "id" in n.attrs}
        for a in self.root.iter("a"):
            href = a.attrs.get("href", "")
            self.assertTrue(href, "empty href")
            if href.startswith("#"):
                self.assertIn(href[1:], ids, f"broken anchor {href}")
            else:
                self.assertTrue(href.startswith("https://"), href)
        allowed = set(EXPECTED_SOURCES.values())
        f1_links = {a.attrs["href"] for a in self.root.iter("a") if "formula1.com" in a.attrs.get("href", "")}
        self.assertTrue(f1_links <= allowed, f"unverified F1 links: {f1_links - allowed}")

    def test_no_insecure_license_links(self):
        for rel in ("index.html", "data/images.json"):
            self.assertFalse("http://creativecommons.org/" in read(rel), f"insecure license URL in {rel}")
        license_hrefs = [a.attrs["href"] for a in self.root.iter("a") if "creativecommons.org" in a.attrs.get("href", "")]
        self.assertTrue(license_hrefs)
        for href in license_hrefs:
            self.assertTrue(href.startswith("https://creativecommons.org/"), href)

    def test_local_asset_refs_exist(self):
        for ref in re.findall(r'(?:href|src)="([^"#:]+)"', self.html):
            self.assertTrue((ROOT / ref).is_file(), f"missing local asset {ref}")


class StyleContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = read("styles.css").lower()

    def test_palette_and_type(self):
        for c in ("#0f0c09", "#14110b", "#1a150e", "#2a2218", "#ece1cf", "#cdc1ab", "#a99e88", "#d8a942"):
            self.assertIn(c, self.css)
        self.assertIn("newsreader", self.css)
        self.assertIn("jetbrains mono", self.css)
        self.assertRegex(self.css, r"monospace")
        self.assertRegex(self.css, r"serif")

    def test_accessibility_and_responsive_rules(self):
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn(":focus-visible", self.css)
        self.assertRegex(self.css, r"@media[^{]*(max|min)-width")
        self.assertRegex(self.css, r"img[^{]*\{[^}]*max-width:\s*100%")
        self.assertIn("overflow-wrap", self.css)


if __name__ == "__main__":
    unittest.main()
