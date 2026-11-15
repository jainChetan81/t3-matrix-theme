import re
CV = '[data-workspace-area="conversation"]'

def split_svg(svg_raw):
    m = re.match(r"(<svg[^>]*>)(<style>.*?</style>)<g fill=\"#0affa0\">(.*?)</g><g class=\"h\">(.*?)</g></svg>", svg_raw, re.S)
    assert m, 'svg parse'
    return m.groups()

def texts_by_x(body):
    out = {}
    for t in re.findall(r'<text x="(\d+)".*?</text>', body, re.S):
        pass
    for mt in re.finditer(r'<text x="(\d+)"[^>]*>.*?</text>', body, re.S):
        out.setdefault(int(mt.group(1)), []).append(mt.group(0))
    return out

def svg_tile_anim(svg_raw, dur='3.7s', timing='steps(26)'):
    head, style, cols, heads = split_svg(svg_raw)
    style = style.replace('</style>', '.m{animation:f %s %s infinite}@keyframes f{to{transform:translateY(650px)}}</style>' % (dur, timing))
    return (f'{head}{style}<defs><g id="t"><g fill="#0affa0">{cols}</g><g class="h">{heads}</g></g></defs>'
            f'<g class="m"><use href="#t"/><use href="#t" y="-650"/></g></svg>')

def svg_cols_anim(svg_raw, durs=(2.6, 5.2, 7.8, 10.4), timing='steps(26)', classes=4):
    head, style, cols, heads = split_svg(svg_raw)
    C = texts_by_x(cols); H = texts_by_x(heads)
    xs = sorted(set(C) | set(H))
    order = [0, 2, 1, 3, 2, 0, 3, 1]  # interleave speeds across neighbouring columns
    groups = {i: [] for i in range(classes)}
    for n, x in enumerate(xs):
        g = order[n % len(order)] % classes
        groups[g].append((C.get(x, []), H.get(x, [])))
    anim = ''.join('.m%d{animation:f %ss %s infinite}' % (i, durs[i], timing) for i in range(classes))
    style = style.replace('</style>', anim + '@keyframes f{to{transform:translateY(650px)}}</style>')
    defs = ''.join(f'<g id="c{i}"><g fill="#0affa0">{"".join(t for c,h in groups[i] for t in c)}</g><g class="h">{"".join(t for c,h in groups[i] for t in h)}</g></g>' for i in range(classes))
    uses = ''.join(f'<g class="m{i}"><use href="#c{i}"/><use href="#c{i}" y="-650"/></g>' for i in range(classes))
    return f'{head}{style}<defs>{defs}</defs>{uses}</svg>'

def static_pseudo(url_css, layer=False, both_masks=True):
    wc = 'will-change:transform;' if layer else ''
    return (f':root{{--rain2:{url_css}}}'
            f'{CV},[data-workspace-area="home"]{{position:relative;isolation:isolate;contain:paint}}'
            f'{CV}::before,{CV}::after{{content:"";position:absolute;top:0;bottom:0;z-index:-1;pointer-events:none;background:var(--rain2) 0 0/1000px 650px;opacity:.5;{wc}'
            f'width:max(0px,calc(50% - var(--lane) - 24px))}}'
            f'{CV}::before{{left:0;-webkit-mask-image:linear-gradient(90deg,#000 35%,transparent)}}'
            f'{CV}::after{{right:0;background-position-x:-410px;-webkit-mask-image:linear-gradient(270deg,#000 35%,transparent)}}')

def VARIANTS(RAIN_CUR, svg_raw, enc):
    v = []
    v.append(('none', '', ''))
    v.append(('cur', RAIN_CUR, ''))
    v.append(('cur_linear', RAIN_CUR + '[data-workspace-area]::before,[data-workspace-area]::after{animation-timing-function:linear!important}', ''))
    v.append(('cur_nomask_nowc', RAIN_CUR + CV + '::before,' + CV + '::after{-webkit-mask-image:none!important;will-change:auto!important;transition:none!important}', ''))
    # real elements with the same rules, to compare against pseudo-elements
    real = RAIN_CUR.replace(CV + '::before', '.r1').replace(CV + '::after', '.r2').replace('[data-workspace-area="home"]::before', '.r3')
    v.append(('real_elem', real, '<div class="r1"></div><div class="r2"></div>'))
    one = (f'{CV}{{position:relative;isolation:isolate;contain:paint}}'
           f'{CV}::before{{content:"";position:absolute;top:-650px;bottom:0;left:0;right:0;z-index:-1;pointer-events:none;background:var(--rain) 0 0/1000px 650px;opacity:.5;will-change:transform;'
           f'-webkit-mask-image:linear-gradient(90deg,#000 calc(25% - 196px),transparent calc(50% - 392px),transparent calc(50% + 392px),#000 calc(75% + 196px));animation:rn 4.4s steps(26) infinite}}'
           '@keyframes rn{to{transform:translateY(650px)}}')
    v.append(('one_pseudo', one, ''))
    v.append(('svg_tile_steps', static_pseudo(enc(svg_tile_anim(svg_raw))), ''))
    v.append(('svg_tile_linear', static_pseudo(enc(svg_tile_anim(svg_raw, timing='linear'))), ''))
    v.append(('svg_cols_steps', static_pseudo(enc(svg_cols_anim(svg_raw))), ''))
    v.append(('svg_cols_steps_layer', static_pseudo(enc(svg_cols_anim(svg_raw)), layer=True), ''))
    v.append(('svg_cols_linear', static_pseudo(enc(svg_cols_anim(svg_raw, timing='linear'))), ''))
    v.append(('static_only', static_pseudo('var(--rain)'), ''))
    bgpos = static_pseudo('var(--rain)') + f'{CV}::before,{CV}::after{{animation:bp 3.7s steps(26) infinite}}@keyframes bp{{to{{background-position-y:650px}}}}'
    v.append(('bgpos_steps', bgpos, ''))
    return v
