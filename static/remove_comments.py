import os, io, re, shutil, tokenize

TARGET_EXTS = {'.py', '.html', '.htm', '.js', '.css', '.txt', '.django'}

def remove_comments_py(path):
    with open(path, 'rb') as f:
        data = f.read()
    try:
        tokens = list(tokenize.tokenize(io.BytesIO(data).readline))
    except Exception:
        return False, 'tokenize error'
    new_tokens = [t for t in tokens if t.type != tokenize.COMMENT]
    try:
        new = tokenize.untokenize(new_tokens)
    except Exception:
        return False, 'untokenize error'
    with open(path, 'wb') as f:
        f.write(new)
    return True, None

def remove_comments_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    text = re.sub(r'{#.*?#}', '', text, flags=re.S)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    text = re.sub(r'(?<!:)//.*?$', '', text, flags=re.M)
    text = re.sub(r'[ \t]+(\r?\n)', r'\1', text)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return True, None

def process_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.py':
        return remove_comments_py(path)
    if ext in TARGET_EXTS:
        return remove_comments_text(path)
    return False, 'unsupported'

def main(root):
    summary = {'processed':0, 'skipped':0, 'errors':[]}
    for dirpath, _, filenames in os.walk(root):
        if '__pycache__' in dirpath or dirpath.endswith('.pyc'):
            continue
        for fn in filenames:
            if fn.endswith('.bak') or fn.endswith('.pyc'):
                continue
            path = os.path.join(dirpath, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext not in TARGET_EXTS:
                summary['skipped'] += 1
                continue
            bak = path + '.bak'
            try:
                if not os.path.exists(bak):
                    shutil.copy2(path, bak)
                ok, err = process_file(path)
                if ok:
                    summary['processed'] += 1
                else:
                    summary['errors'].append((path, err))
            except Exception as e:
                summary['errors'].append((path, str(e)))
    print('Processed:', summary['processed'])
    print('Skipped:', summary['skipped'])
    if summary['errors']:
        print('Errors:')
        for p, e in summary['errors']:
            print(' -', p, ':', e)

if __name__ == '__main__':
    main(os.path.dirname(__file__))