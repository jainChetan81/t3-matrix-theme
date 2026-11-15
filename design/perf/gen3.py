import gen, variants
CV = variants.CV; cur = gen.RAIN_CUR
NG = '[data-slot="workspace-breadcrumb-text"]{animation:none!important}'
def ov(p): return CV + '::before,' + CV + '::after{' + p + '}'
for name, css in [('r_cur', cur), ('r_nomask', cur + ov('-webkit-mask-image:none!important')),
                  ('r_nowc', cur + ov('will-change:auto!important')), ('r_notr', cur + ov('transition:none!important')),
                  ('r_nomask_nowc', cur + ov('-webkit-mask-image:none!important;will-change:auto!important')),
                  ('r_cur_ng', cur + NG), ('r_none_ng', NG), ('r_before_only_ng', cur + NG + CV + '::after{animation:none!important}')]:
    gen.page(name, css, '')
