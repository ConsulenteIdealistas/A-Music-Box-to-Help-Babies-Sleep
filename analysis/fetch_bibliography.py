#!/usr/bin/env python3
"""Phase 1 / Identification: METHODOLOGY.md のクエリ v1 で PubMed から
書誌データ（PMID・タイトル・年・抄録）を取得し、ジャーナル別 CSV と
統合 CSV を literature/ に書き出す。Python 標準ライブラリのみ。

使い方: python3 fetch_bibliography.py
"""
import csv
import json
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
HERE = os.path.dirname(os.path.abspath(__file__))
LIT = os.path.join(HERE, "..", "literature")

QUERIES = {
    "pediatrics": '"Pediatrics"[Journal] AND (infant OR newborn OR neonate) AND ("white noise" OR "sound" OR "music" OR "lullaby" OR "heartbeat") AND (sleep OR decibel OR hearing)',
    "early_human_development": '"Early Human Development"[Journal] AND (fetal OR newborn OR preterm) AND ("intrauterine" OR "heartbeat" OR "maternal voice" OR "auditory") AND (autonomic OR "heart rate" OR sleep)',
    "infant_behavior_development": '"Infant Behavior & Development"[Journal] AND (infant OR newborn) AND (rhythm OR tempo OR music OR lullaby OR "white noise") AND (soothing OR crying OR attention OR preference)',
    "jasa": '"The Journal of the Acoustical Society of America"[Journal] AND (fetal OR intrauterine OR womb OR infant) AND (attenuation OR spectrum OR frequency OR "white noise" OR acoustic)',
    "hearing_research": '"Hearing Research"[Journal] AND (fetal OR fetus OR newborn OR neonate OR infant) AND (frequency OR pitch OR threshold OR sensitivity)',
    "journal_of_music_therapy": '"Journal of Music Therapy"[Journal] AND (infant OR NICU OR premature OR preterm OR newborn OR neonate)',
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "lullaby-research/1.0"})
    return urllib.request.urlopen(req, timeout=60).read()


def esearch_ids(term):
    url = BASE + "/esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": term, "retmode": "json", "retmax": 10000})
    d = json.loads(get(url))
    return d["esearchresult"]["idlist"]


def efetch_batch(ids):
    url = BASE + "/efetch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": ",".join(ids), "retmode": "xml"})
    root = ET.fromstring(get(url))
    rows = []
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = art.findtext(".//ArticleTitle") or ""
        year = art.findtext(".//JournalIssue/PubDate/Year") or art.findtext(".//JournalIssue/PubDate/MedlineDate") or ""
        journal = art.findtext(".//Journal/Title") or ""
        parts = []
        for node in art.iter("AbstractText"):
            label = node.get("Label")
            text = "".join(node.itertext())
            parts.append(f"{label}: {text}" if label else text)
        rows.append({
            "PMID": pmid, "Title": title, "Journal": journal,
            "Year": year, "Abstract": " ".join(parts),
            "Has_Abstract": "yes" if parts else "no",
        })
    return rows


def main():
    os.makedirs(LIT, exist_ok=True)
    all_rows = []
    for key, query in QUERIES.items():
        ids = esearch_ids(query)
        time.sleep(0.4)
        rows = []
        for i in range(0, len(ids), 200):
            rows.extend(efetch_batch(ids[i:i + 200]))
            time.sleep(0.4)
        path = os.path.join(LIT, f"bibliography_{key}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["PMID", "Title", "Journal", "Year", "Abstract", "Has_Abstract"])
            w.writeheader()
            w.writerows(rows)
        no_abs = sum(1 for r in rows if r["Has_Abstract"] == "no")
        print(f"{key}: {len(rows)}件 (抄録なし {no_abs}件)")
        all_rows.extend(rows)
    path = os.path.join(LIT, "bibliography_all.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["PMID", "Title", "Journal", "Year", "Abstract", "Has_Abstract"])
        w.writeheader()
        w.writerows(all_rows)
    print(f"合計: {len(all_rows)}件 -> {path}")


if __name__ == "__main__":
    main()
