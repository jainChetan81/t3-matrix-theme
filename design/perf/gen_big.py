import gen, variants
gen.chat_dom_orig = gen.chat_dom
gen.chat_dom = lambda n_msgs=300: gen.chat_dom_orig(300)
CV = variants.CV
cur = gen.RAIN_CUR
hasrule = cur[cur.index(':root:has(.composer-tiptap:focus)'):]
nohas = cur.replace(hasrule, '')
nohas_notr = nohas.replace(';transition:opacity .4s', '')
FOCUS = '<script>addEventListener("load",()=>document.querySelector(".composer-tiptap").focus())</script>'
for name, css, dom in [('big_none', '', ''), ('big_cur', cur, ''), ('big_cur_focus', cur, FOCUS), ('big_nohas', nohas, ''), ('big_nohas_notr', nohas_notr, ''), ('big_noglitch_none', '[data-slot="workspace-breadcrumb-text"]{animation:none!important}', ''), ('big_noglitch_cur', cur + '[data-slot="workspace-breadcrumb-text"]{animation:none!important}', '')]:
    gen.page(name, css, dom)
print('ok')
