# Add a Tailwind-v4-like stylesheet (registered --tw-* props on *,::before,::after + many utilities) to test per-recalc cost.
import gen, variants, random
CV = variants.CV; cur = gen.RAIN_CUR
NG = '[data-slot="workspace-breadcrumb-text"]{animation:none!important}'
props = [f'--tw-p{i}' for i in range(45)]
tw = ''.join(f'@property {p}{{syntax:"*";inherits:false}}' for p in props)
tw += '*,::before,::after,::backdrop{' + ''.join(f'{p}:initial;' for p in props) + 'box-sizing:border-box;border:0 solid}'
tw += ''.join(f'.u{i}{{margin:{i%9}px;padding:{i%7}px}}.u{i}:hover{{color:#{i%999:03d}}}.g{i}::before{{content:"{i}"}}' for i in range(3000))
tw += '::before,::after{--tw-content:"";}' + ''.join(f'.x{i} ::after,.y{i}::before{{opacity:.{i%9}}}' for i in range(500))
gen.PAGE_CSS = tw + gen.PAGE_CSS
for name, css in [('t_none_ng', NG), ('t_cur_ng', cur + NG), ('t_cur', cur), ('t_before_only_ng', cur + NG + CV + '::after{animation:none!important}')]:
    gen.page(name, css, '')
