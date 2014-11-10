import os
import re


conf = None
args = None


def _get_mdfile(adir):
    for afile in os.listdir(adir):
        if afile.endswith('.md'):
            name = afile.split('.')[0]
            yield (adir, name, os.path.join(adir, afile))

def _write_list(adir, rf):
    rf.write('# '+adir+'\n\n')
    is_post = adir == 'post'
    names = []
    for adir, name, fpath in _get_mdfile(adir):
        if is_post:
            names.append(int(name))
        else:
            names.append(name)
    if is_post:
        names = sorted(names)
    for name in names:
        _write_a_file(adir, str(name), rf)
    rf.write('\n')

def _write_a_file(adir, name, rf):
    with open(os.path.join(adir, str(name)+'.md'), 'r', encoding='utf-8') as f:
        fmt = '1. %s [%s](http://zengrong.net/%s.htm)\n'
        time = None
        title = None
        for line in f:
            if line.startswith('Title:'):
                title = line[6:].strip()
            elif line.startswith('Date:'):
                time = line[6:16]
                break
        if time and title:
            rf.write(fmt%(time, title, name))


def _write_readme():
    with open('README.md', 'w', encoding='utf-8', newline='\n') as f:
        f.write("[zrong's blog](http://zengrong.net) 中的所有文章\n")
        f.write('==========\n\n')
        f.write("----------\n\n")
        _write_list('page', f)
        _write_list('post', f)

def _rewrite_title(dirname):
    for adir, name, fpath in _get_mdfile(dirname):
        content = None
        with open(fpath, 'r', encoding='utf-8', newline='\n') as f:
            for line in f:
                if line.startswith('Title:') and line.find('[转]') > -1:
                    f.seek(0)
                    content = True
                    break
            if content:
                 content = f.read().replace('[转]', '【转】')
        if content:
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)

def _rewrite_url(dirname):
    url = re.compile(r'\]\(/\?p=(\d+)\)', re.S)
    for adir, name, fpath in _get_mdfile(dirname):
        content = None
        fpath = os.path.join(adir, afile)
        with open(fpath, 'r', encoding='utf-8', newline='\n') as f:
            content = f.read()
            matchs = url.findall(content)
            if len(matchs) > 0:
                print(afile, matchs)
                for num in matchs:
                    content = content.replace('](/?p=%s'% num,
                            '](http://zengrong.net/post/%s.htm'%num)
            else:
                content = None
        if content:
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
                print(fpath)

def _rewrite_category():
    sign = 'Category: '
    num = 0
    for adir,name,fpath in _get_mdfile('post'):
        content = None
        with open(fpath, 'r', encoding='utf-8', newline='\n') as f:
            for line in f:
                if line.startswith(sign):
                    f.seek(0)
                    line = line[len(sign):]
                    cats = line.split(',')
                    if len(cats) > 1:
                        content = True
                    break
        if content:
            print(name, cats)
            num = num + 1
            # with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
            #     f.write(content)
    print(num)

def _rewrite_dir(fun, dirname):
    if dirname == 'all':
        fun('post')
        fun('page')
        fun('draft')
    else:
        fun(dirname)

def build(gconf, gargs, parser=None):
    global conf
    global args
    conf = gconf
    args = gargs

    if args.all:
        _updateAll()
        return

    noAnyArgs = True
    if args.readme:
        _write_readme()
        noAnyArgs = False
    if args.title:
        _rewrite_dir(_rewrite_title, args.dirname)
        noAnyArgs = False
    if args.url:
        _rewrite_dir(_rewrite_url, args.dirname)
        noAnyArgs = False
    if args.category:
        _rewrite_category()
        noAnyArgs = False

    if noAnyArgs and parser:
        parser.print_help()

