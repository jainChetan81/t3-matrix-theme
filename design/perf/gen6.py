import gen, variants
CV = variants.CV
NG = '[data-slot="workspace-breadcrumb-text"]{animation:none!important}'
svg = variants.svg_cols_anim(gen.svg_raw, durs=(5.2, 10.4, 15.6, 20.8))
css = variants.static_pseudo(gen.enc(svg), layer=True) + CV + '::before,' + CV + '::after{-webkit-mask-image:none!important}'
gen.page('s_cols_slow_layer_ng', css + NG, '')
