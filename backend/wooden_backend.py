#!/usr/bin/env python3
"""Local project evidence and revision registry. Never authorizes manufacture."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3

KINDS = {'source', 'item', 'dimension', 'material', 'hardware', 'part',
         'deliverable', 'issue', 'decision', 'approval', 'check', 'progress'}
REVIEWS = {'geometry', 'hardware', 'site_fit', 'manufacturability', 'rendering'}
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]*$')


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def superseded(data):
    return data.get('status') == 'superseded'


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Store:
    def __init__(self, db_path):
        if str(db_path) != ':memory:':
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(db_path))
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY, client_id TEXT NOT NULL, name TEXT NOT NULL,
            root TEXT NOT NULL UNIQUE, revision INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS records (
            project TEXT NOT NULL REFERENCES projects(id), kind TEXT NOT NULL,
            id TEXT NOT NULL, data TEXT NOT NULL, stale INTEGER NOT NULL DEFAULT 0,
            reviewed_revision INTEGER, PRIMARY KEY(project,kind,id));
        CREATE TABLE IF NOT EXISTS history (
            sequence INTEGER PRIMARY KEY, project TEXT NOT NULL,
            kind TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL,
            stale INTEGER NOT NULL, reason TEXT NOT NULL,
            recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS operations (
            request_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, result TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS history_no_update BEFORE UPDATE ON history
            BEGIN SELECT RAISE(ABORT, 'history is immutable'); END;
        CREATE TRIGGER IF NOT EXISTS history_no_delete BEFORE DELETE ON history
            BEGIN SELECT RAISE(ABORT, 'history is immutable'); END;
        ''')

    def close(self):
        self.db.close()

    def _project(self, project_id):
        row = self.db.execute('SELECT * FROM projects WHERE id=?', (project_id,)).fetchone()
        require(row is not None, 'Unknown project: ' + project_id)
        return row

    def create_project(self, project_id, client_id, name, root):
        require(ID.fullmatch(project_id or '') and ID.fullmatch(client_id or ''), 'Invalid project/client ID')
        require(isinstance(name, str) and name.strip(), 'Project name required')
        path = Path(root).resolve()
        require(path.is_dir(), 'Project root must already exist')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            old = self.db.execute('SELECT * FROM projects WHERE id=?', (project_id,)).fetchone()
            if old:
                require((old['client_id'], old['name'], old['root']) == (client_id, name, str(path)),
                        'Project ID already registered with different information')
            else:
                for existing in self.db.execute('SELECT root FROM projects'):
                    other = Path(existing['root'])
                    require(not (path.is_relative_to(other) or other.is_relative_to(path)),
                            'Project roots must not overlap')
                self.db.execute('INSERT INTO projects(id,client_id,name,root) VALUES(?,?,?,?)',
                                (project_id, client_id, name, str(path)))
        return dict(self._project(project_id))

    def get(self, project_id, kind, record_id):
        self._project(project_id)
        row = self.db.execute('SELECT * FROM records WHERE project=? AND kind=? AND id=?',
                              (project_id, kind, record_id)).fetchone()
        if row is None:
            return None
        return {'kind': row['kind'], 'id': row['id'], 'data': json.loads(row['data']), 'stale': bool(row['stale'])}

    def records(self, project_id, kind):
        self._project(project_id)
        require(kind in KINDS, 'Unknown record kind')
        rows = self.db.execute('SELECT id FROM records WHERE project=? AND kind=? ORDER BY id', (project_id, kind))
        return [self.get(project_id, kind, row['id']) for row in rows.fetchall()]

    def _file(self, project_id, data):
        root = Path(self._project(project_id)['root'])
        path = (root / data.get('path', '')).resolve()
        require(path.is_relative_to(root) and path.is_file(), 'File must exist inside this project root')
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(data.get('sha256') == actual, 'File SHA256 missing or does not match: ' + str(path))
        return path

    def _dependencies(self, kind, data, project_id=None):
        refs = list(data.get('depends_on', []))
        if kind in {'dimension', 'part'} and data.get('item_id'):
            refs.append('item:' + data['item_id'])
        if data.get('source_id'):
            refs.append('source:' + data['source_id'])
        if kind == 'part' and data.get('material_id'):
            refs.append('material:' + data['material_id'])
        if kind == 'part' and project_id:
            refs.extend('dimension:' + r['id'] for r in self.records(project_id, 'dimension')
                        if not superseded(r['data']) and r['data'].get('item_id') == data.get('item_id'))
        if kind == 'deliverable':
            refs.extend('part:' + p for p in data.get('parts', {}))
        return sorted(set(refs))

    def _validate(self, project_id, kind, record_id, data):
        require(isinstance(data, dict), 'Record data must be an object')
        require(isinstance(data.get('depends_on', []), list), 'depends_on must be a list')
        require(all(isinstance(x, str) for x in data.get('depends_on', [])), 'Dependency must be kind:id')
        if kind == 'source':
            require(bool(data.get('revision')), 'Source revision required')
            if not superseded(data):
                self._file(project_id, data)
        if kind == 'dimension':
            require(data.get('item_id') and data.get('key'), 'Dimension item_id and key required')
            require(positive(data.get('value')), 'Dimension must be positive and finite')
            require(data.get('unit') == 'mm', 'Dimension unit must be mm')
            require(type(data.get('critical')) is bool, 'Dimension critical must be boolean')
            require(data.get('evidence') in {'site_verified', 'manufacturer', 'design', 'photo_estimate', 'assumed'},
                    'Invalid dimension evidence classification')
        if kind == 'part':
            require(data.get('item_id'), 'Part item_id required')
            require(type(data.get('quantity')) is int and data['quantity'] > 0, 'Part quantity must be a positive integer')
            for field in ('finished', 'cutting'):
                size = data.get(field)
                require(isinstance(size, dict) and all(positive(size.get(k)) for k in ('length', 'width', 'thickness')),
                        field + ' requires positive finite length, width, thickness in mm')
        if kind == 'deliverable':
            require(isinstance(data.get('parts', {}), dict), 'Deliverable parts must be ID:quantity mapping')
            require(all(type(v) is int and v > 0 for v in data.get('parts', {}).values()), 'Deliverable quantities must be positive integers')
        if kind in {'approval', 'check'}:
            require(isinstance(data.get('reviewer'), str) and data['reviewer'].strip(), 'Reviewer required')
            require(isinstance(data.get('evidence'), str) and data['evidence'].strip(), 'Review evidence required')
        # Retirement preserves historical information; it does not revalidate it.
        if superseded(data):
            return
        for ref in self._dependencies(kind, data, project_id):
            require(isinstance(ref, str) and ':' in ref, 'Dependency must be kind:id')
            rk, ri = ref.split(':', 1)
            require(rk in KINDS and self.get(project_id, rk, ri) is not None, 'Missing project-local dependency: ' + ref)
            require(not superseded(self.get(project_id, rk, ri)['data']), 'Superseded dependency: ' + ref)
            require(not self.get(project_id, rk, ri)['stale'], 'Dependency requires revision first: ' + ref)
            require(ref != kind + ':' + record_id, 'Self dependency forbidden')
            todo, seen = [ref], set()
            while todo:
                node = todo.pop()
                require(node != kind + ':' + record_id, 'Cyclic dependency forbidden')
                if node in seen:
                    continue
                seen.add(node)
                nk, ni = node.split(':', 1)
                found = self.get(project_id, nk, ni)
                if found:
                    todo.extend(self._dependencies(nk, found['data'], project_id))

    def _history(self, project_id, kind, record_id, data, stale, reason):
        self.db.execute('INSERT INTO history(project,kind,id,data,stale,reason) VALUES(?,?,?,?,?,?)',
                        (project_id, kind, record_id, encode(data), int(stale), reason))

    def upsert(self, project_id, kind, record_id, data, request_id):
        require(kind in KINDS and ID.fullmatch(record_id or ''), 'Invalid record kind or ID')
        require(isinstance(request_id, str) and request_id.strip(), 'Unique request_id required')
        fingerprint = hashlib.sha256(encode([project_id, kind, record_id, data]).encode()).hexdigest()
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            previous = self.db.execute('SELECT * FROM operations WHERE request_id=?', (request_id,)).fetchone()
            if previous:
                require(previous['fingerprint'] == fingerprint, 'request_id already used for a different operation')
                return json.loads(previous['result'])
            self._project(project_id)
            self._validate(project_id, kind, record_id, data)
            old = self.get(project_id, kind, record_id)
            retiring = superseded(data)
            if old and (old['stale'] or superseded(old['data'])) and not retiring and kind not in {'check', 'approval'}:
                require(old['data'] != data, 'Stale record requires revised content and revalidation evidence')
                review = data.get('revalidation', {})
                require(isinstance(review, dict) and review.get('reviewer') and review.get('evidence'),
                        'Stale record requires revalidation reviewer and evidence')
            if old and old['data'] == data and (not old['stale'] or retiring):
                result = old
            else:
                engineering = kind not in {'check', 'approval', 'progress'}
                # Capture implicit dimension links before retirement removes them.
                before = {r['kind'] + ':' + r['id']: self._dependencies(r['kind'], json.loads(r['data']), project_id)
                          for r in self.db.execute('SELECT * FROM records WHERE project=?', (project_id,)).fetchall()}
                if engineering:
                    self.db.execute('UPDATE projects SET revision=revision+1 WHERE id=?', (project_id,))
                revision = self._project(project_id)['revision']
                stale = bool(old and old['stale']) if retiring else False
                self.db.execute('INSERT INTO records VALUES(?,?,?,?,?,?) ON CONFLICT(project,kind,id) DO UPDATE SET data=excluded.data,stale=excluded.stale,reviewed_revision=excluded.reviewed_revision',
                                (project_id, kind, record_id, encode(data), int(stale), revision if kind in {'check', 'approval'} and not retiring else None))
                self._history(project_id, kind, record_id, data, stale, 'upsert')
                changed = {kind + ':' + record_id}
                rows = self.db.execute('SELECT * FROM records WHERE project=?', (project_id,)).fetchall()
                again = True
                while again:
                    again = False
                    for row in rows:
                        ref = row['kind'] + ':' + row['id']
                        if ref in changed:
                            continue
                        rd = json.loads(row['data'])
                        if superseded(rd):
                            continue
                        deps = set(before.get(ref, [])) | set(self._dependencies(row['kind'], rd, project_id))
                        if (engineering and row['kind'] in {'check', 'approval'}) or changed.intersection(deps):
                            changed.add(ref)
                            again = True
                            if not row['stale']:
                                self.db.execute('UPDATE records SET stale=1 WHERE project=? AND kind=? AND id=?', (project_id, row['kind'], row['id']))
                                self._history(project_id, row['kind'], row['id'], rd, True, 'dependency or project revision changed')
                result = self.get(project_id, kind, record_id)
            self.db.execute('INSERT INTO operations VALUES(?,?,?)', (request_id, fingerprint, encode(result)))
        return result

    def check(self, project_id):
        project = self._project(project_id)
        grouped = {k: [r for r in self.records(project_id, k) if not superseded(r['data'])] for k in KINDS}
        blockers = []
        for k in ('item', 'dimension', 'part', 'deliverable'):
            if not grouped[k]:
                blockers.append('Missing ' + k + ' records')
        for kind, rows in grouped.items():
            for row in rows:
                for ref in self._dependencies(kind, row['data'], project_id):
                    rk, ri = ref.split(':', 1)
                    dependency = self.get(project_id, rk, ri)
                    if not dependency or superseded(dependency['data']):
                        blockers.append('Inactive dependency: ' + kind + ':' + row['id'] + ' -> ' + ref)
                if row['stale'] and kind != 'progress':
                    blockers.append('Stale ' + kind + ':' + row['id'])
                if kind == 'source':
                    try:
                        self._file(project_id, row['data'])
                    except (ValueError, OSError) as error:
                        blockers.append('Source ' + row['id'] + ': ' + str(error))
        dims = {}
        for row in grouped['dimension']:
            d = row['data']
            dims.setdefault((d['item_id'], d['key']), set()).add((d['value'], d['unit']))
            if d['critical'] and (d['evidence'] not in {'site_verified', 'manufacturer'} or not d.get('source_id')):
                blockers.append('Unverified critical dimension ' + row['id'])
            if d['evidence'] == 'photo_estimate':
                blockers.append('Photographic estimate requires measurement: ' + row['id'])
        for key, values in dims.items():
            if len(values) > 1:
                blockers.append('Conflicting dimensions for ' + ':'.join(key))
        for item in grouped['item']:
            for kind in ('dimension', 'part'):
                if not any(r['data'].get('item_id') == item['id'] for r in grouped[kind]):
                    blockers.append('Item ' + item['id'] + ' has no ' + kind)
        parts = {r['id']: r['data']['quantity'] for r in grouped['part']}
        for row in grouped['part']:
            data = row['data']
            if not data.get('material_id'):
                blockers.append('Part lacks material reference: ' + row['id'])
            for field in ('grain', 'edges', 'finish', 'machining'):
                if not data.get(field):
                    blockers.append('Part lacks ' + field + ' specification: ' + row['id'])
        covered = set()
        manufacturing = []
        for row in grouped['deliverable']:
            d = row['data']
            if d.get('purpose') != 'manufacturing':
                continue
            manufacturing.append(row)
            if not d.get('depends_on'):
                blockers.append('Manufacturing deliverable lacks dependencies: ' + row['id'])
            if not d.get('parts'):
                blockers.append('Manufacturing deliverable lacks parts: ' + row['id'])
            for part, qty in d.get('parts', {}).items():
                covered.add(part)
                if parts.get(part) != qty:
                    blockers.append('Part quantity mismatch: ' + row['id'] + '/' + part)
            try:
                self._file(project_id, d)
            except (ValueError, OSError) as error:
                blockers.append('Deliverable ' + row['id'] + ': ' + str(error))
        if not manufacturing:
            blockers.append('Missing manufacturing deliverable')
        for part in set(parts) - covered:
            blockers.append('Part missing from manufacturing deliverables: ' + part)
        for issue in grouped['issue']:
            if issue['data'].get('status') != 'closed':
                blockers.append('Open issue: ' + issue['id'])
        for name in sorted(REVIEWS):
            review = self.get(project_id, 'check', name)
            valid = False
            if review and not superseded(review['data']) and not review['stale'] and review['data'].get('pass') is True:
                rr = self.db.execute('SELECT reviewed_revision FROM records WHERE project=? AND kind=? AND id=?', (project_id, 'check', name)).fetchone()[0]
                valid = rr == project['revision']
            if not valid:
                blockers.append('Current human review required: ' + name)
        return {'blockers': sorted(set(blockers)), 'ready_for_review': not blockers}

    def summary(self, project_id):
        p = self._project(project_id)
        result = self.check(project_id)
        latest = self.db.execute("SELECT id FROM history WHERE project=? AND kind='progress' AND reason='upsert' ORDER BY sequence DESC LIMIT 1", (project_id,)).fetchone()
        progress = [self.get(project_id, 'progress', latest['id'])] if latest else []
        stage = progress[-1]['data'].get('stage', 'Draft') if progress else 'Draft'
        lines = [p['name'] + ' (' + project_id + ')', 'Current stage: ' + stage,
                 'Engineering revision: ' + str(p['revision']),
                 'Manufacturing authorization: NOT RELEASED (external explicit approval required)']
        lines += ['Blocker: ' + b for b in result['blockers']]
        if result['ready_for_review']:
            lines.append('Recorded checks complete; ready for owner review, not manufacturing release.')
        if progress:
            lines.append('Next action: ' + str(progress[-1]['data'].get('next_action', 'Review project records')))
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True, help='SQLite database path')
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('init-project')
    for name in ('project_id', 'client_id', 'name', 'root'):
        create.add_argument(name)
    put = commands.add_parser('put')
    for name in ('project_id', 'kind', 'record_id', 'json_file', 'request_id'):
        put.add_argument(name)
    for command in ('check', 'summary'):
        commands.add_parser(command).add_argument('project_id')
    args = parser.parse_args()
    store = Store(args.db)
    try:
        if args.command == 'init-project':
            result = store.create_project(args.project_id, args.client_id, args.name, args.root)
        elif args.command == 'put':
            result = store.upsert(args.project_id, args.kind, args.record_id,
                                  json.loads(Path(args.json_file).read_text()), args.request_id)
        elif args.command == 'check':
            result = store.check(args.project_id)
        else:
            result = store.summary(args.project_id)
        print(result if isinstance(result, str) else json.dumps(result, indent=2))
        return 1 if args.command == 'check' and result['blockers'] else 0
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.exit(2, str(error) + '\n')
    finally:
        store.close()


if __name__ == '__main__':
    raise SystemExit(main())
