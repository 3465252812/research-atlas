"""Parse (never execute) the supplied legacy HTML JSON into canonical data."""
import argparse
import copy
import re
from html.parser import HTMLParser
from data_model import write_json, read_json, doi_key, arxiv_key, date_ok, valid_url
import json
from pathlib import Path

class DataParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.active = False
        self.parts = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'script' and a.get('id') == 'method-data' and a.get('type') == 'application/json':
            self.active = True
    def handle_endtag(self, tag):
        if tag == 'script':
            self.active = False
    def handle_data(self, text):
        if self.active:
            self.parts.append(text)

def import_data(raw, source_name, profile=None):
    profile = profile or {}
    def date(s):
        s = re.sub(r'[^0-9-].*$', '', s or '')
        return s if s and date_ok(s) else None
    def provenance(m):
        return [dict(survey_id=r.get('survey'), reference_label=r.get('label'), locator=r.get('label'),
                     url=r.get('url') if valid_url(r.get('url')) else None, source_id=source_name,
                     access_level='legacy_import', legacy=copy.deepcopy(r)) for r in m.get('references', [])]
    def evidence(m):
        return [dict(field='legacy_record', source_id=source_name,
                     url=m.get('url') if valid_url(m.get('url')) else None,
                     source_type='legacy', access_level='legacy_import', locator=m['id'],
                     summary='保留原文件信息，未重新阅读全文或复核事实。')]
    def edge(e):
        urls = [e.get('url')] + e.get('sources', [])
        return dict(id=e['id'], source=e['source'], target=e['target'], type=e['type'],
                    description=e.get('label'), basis=e.get('evidence') or '旧版记录待复核',
                    claim_basis='inference', confidence=None, verification='pending',
                    evidence=[dict(source_id=source_name, url=u, source_type='legacy', access_level='legacy_import',
                                   locator=e['id'], summary=e.get('evidence', '旧版导入，置信度未校准。'))
                              for u in dict.fromkeys(urls) if valid_url(u)] or
                             [dict(source_id=source_name, source_type='legacy', access_level='legacy_import', locator=e['id'], summary=e.get('evidence', '待核'))],
                    legacy=copy.deepcopy(e))
    papers, methods = [], []
    for m in raw['methods']:
        url = m.get('url') or ''
        arxiv = re.search(r'arxiv\.org/(?:abs|pdf)/([^?#]+)', url)
        doi = re.search(r'doi\.org/(.+)', url)
        pid = 'paper-' + m['id']
        papers.append(dict(id=pid, title=m.get('title') or m['name'], authors=m.get('authors', []),
                           url=url if valid_url(url) else None, doi=doi_key(doi[1]) if doi else None,
                           arxiv_id=arxiv_key(arxiv[1]) if arxiv else None, first_public_date=date(m.get('date')),
                           publication_date=date((m.get('publication') or {}).get('date')),
                           venue=None, publication_status='unknown',
                           date_basis=m.get('dateBasis'), verification='pending', provenance=provenance(m),
                           evidence=evidence(m), legacy=copy.deepcopy(m)))
        methods.append(dict(id=m['id'], name=m['name'], paper_ids=[pid], primary_group=m['group'],
                            group_ids=[m['group']], aliases=m.get('aliases', []), tags=[], modules=m.get('modules', []),
                            problem=m.get('problem'), mechanism=m.get('tech'), contributions=None,
                            value=m.get('value'), scenarios=None, limitations=m.get('limit'),
                            featured=bool(m.get('featured')), featured_reason='旧版代表方法推荐，待重新评估' if m.get('featured') else None,
                            classification_basis='沿用旧版分类，待原文复核', verification='pending',
                            provenance=provenance(m), evidence=evidence(m), legacy=copy.deepcopy(m)))
    groups = [dict(g, parent_id=None, definition=g.get('desc'), problem=None, rationale='旧版分类，尚未独立归纳', representative_method_ids=[]) for g in raw['groups']]
    global_edges = [edge(e) for e in raw.get('edges', [])]
    global_ids = {e['id'] for e in global_edges}
    tracks = []
    r = raw.get('research')
    if r:
        # Original research view replaces theme edges, keeps technical edges.
        # Keep exact membership via explicit global edge selection, without duplicated IDs.
        selected = list(dict.fromkeys([e['id'] for e in raw['edges'] if e['type'] != 'theme'] + [e['id'] for e in r.get('edges', []) if e['id'] in global_ids]))
        tracks.append(dict(id='legacy-research', name=r.get('title', '导入专题'), definition='导入既有专题，未执行新专题分析', enabled=True,
                           method_ids=[a['method'] for a in r['assignments']],
                           groups=[dict(g, parent_id=None, definition=g.get('desc'), rationale='原专题归属', representative_method_ids=[]) for g in r['lanes']],
                           assignments=r['assignments'], sections=r.get('sections', []),
                           global_edge_ids=selected,
                           edges=[edge(e) for e in r.get('edges', []) if e['id'] not in global_ids],
                           date_audits=r.get('dateAudits', []), update=dict(r.get('update', {}), recent_from=profile.get('recent_from')),
                           evidence=r.get('evidence', []), legacy=copy.deepcopy(r)))
    # Domain-specific legacy scopes belong in an optional external profile, never this skill.
    for config in profile.get('tracks', []):
        members = [m for m in methods if m['primary_group'] in config['group_ids']]
        gids = {m['primary_group'] for m in members}
        tracks.append(dict(id=config['id'], name=config['name'], definition=config.get('definition', '既有范围的兼容迁移'), enabled=True,
                           method_ids=[m['id'] for m in members], groups=[g for g in groups if g['id'] in gids],
                           assignments=[dict(method=m['id'], primary=m['primary_group'], memberships=[m['primary_group']], role='', reason='旧范围') for m in members], edges=[]))
    return dict(papers=papers, methods=methods, groups=groups, edges=global_edges, surveys=raw.get('surveys', []), research_tracks=tracks,
                metadata=dict(schema_version='1.0', domain=profile.get('domain', '导入研究领域'), title=profile.get('title', '技术演进图 · 旧版迁移'),
                              version='1', search_cutoff=(r or {}).get('update', {}).get('cutoff'), search_log=[],
                              coverage_limitations='仅迁移用户原型，未新增文献、重新阅读或进行在线核验。',
                              first_html_delivered=False, review_decisions=[], unresolved=['旧版元数据、分类和全部关系需要按原文证据复核。'],
                              import_source=source_name, legacy_meta=raw.get('meta', {})))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input')
    p.add_argument('--output', required=True)
    p.add_argument('--profile', help='Optional external JSON for domain label, recent_from and legacy scope group IDs')
    a = p.parse_args()
    parser = DataParser()
    parser.feed(Path(a.input).read_text(encoding='utf-8-sig'))
    if not parser.parts:
        p.exit(1, '未找到 method-data application/json\n')
    raw = json.loads(''.join(parser.parts))
    if 'papers' in raw and 'metadata' in raw:
        data = raw
    elif 'canonical' in raw:
        data = raw['canonical']
    else:
        data = import_data(raw, Path(a.input).name, read_json(a.profile) if a.profile else None)
    write_json(a.output, data)
    print(f"Imported {len(data['methods'])} methods without executing source scripts.")

if __name__ == '__main__':
    main()
