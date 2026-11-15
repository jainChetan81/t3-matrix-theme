# Many composited layers (like a real app) to see if animation ticks inflate commit.
import gen, variants
CV = variants.CV; cur = gen.RAIN_CUR
NG = '[data-slot="workspace-breadcrumb-text"]{animation:none!important}'
gen.PAGE_CSS += '.row,[data-thread-item]{will-change:transform}'
for name, css in [('l_none_ng', NG), ('l_cur_ng', cur + NG), ('l_before_only_ng', cur + NG + CV + '::after{animation:none!important}')]:
    gen.page(name, css, '')
