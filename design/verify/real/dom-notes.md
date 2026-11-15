# Real-app DOM notes (throwaway instance :3999, headless Chrome :9388)

## Timeline

rows: 2
row kinds: ["message","message"]
scroll kids: 1
scroll ancestry: ["DIV.messages-timeline-scroll scrollbar-gutter-both h-full min-h-0 overflow","DIV.relative h-full min-h-0","DIV.relative flex min-h-0 flex-1 flex-col bg-background","DIV.relative flex min-h-0 min-w-0 flex-1 flex-col"]
row frame kids: 1
row structure: [{"kind":"message","tag":"DIV","cls":"pb-4","ptag":"DIV","pcls":"chat-content-lane overflow-x-clip","isLast":true,"idx":0,"sibs":1},{"kind":"message","tag":"DIV","cls":"pb-4 group/assistant","ptag":"DIV","pcls":"chat-content-lane overflow-x-clip","isLast":true,"idx":0,"sibs":1}]
workspace-area count: 4
legend-list nodes: 1
content-visibility on sidebar rows: auto

## Remount on thread switch

mark: 2
marks surviving round-trip: 0

## Header / composer / popups / terminal

chat-header: HEADER.relative bg-background [[data-panel-animations=true]_&]:motion-safe:transition-[
header buttons: ["Maximize panel","Toggle thread details panel","Toggle terminal drawer","Toggle right panel","MS\nmatrix-scratch","Matrix rendering one"]
composer: {"tiptap":"tiptap ProseMirror composer-tiptap -m-1 block max-h-52 min-h-[calc(2lh+--spacing(2))] overflow-y-aut","formKids":2}
chat-width default: comfortable
popups now: []
terminal drawer after toggle: ["HTML.dark","LINK.","LINK.","LINK.","LINK.","BUTTON.[&_svg]:-mx-0.5 relative inline-flex cursor-pointer select-none items-center jus","DIV.relative z-0","ASIDE.relative flex min-w-0 flex-col overflow-hidden bg-background z-45 shrink-0 borde"]
popups after menu action: ["dialog:Claude Opus 5.5, ClaudeClaude Sonnet 5.5, ClaudeClaude Fable"]

## Facts found while building the Possessed round (v0.1.10, real app)

- **Nothing above the rows remounts on a thread switch.** Marked every ancestor of a row plus the header, breadcrumb `<li>`s, composer host and form; after thread A -> thread B only the row, its lane, row frame and absolute container were new. Draft -> thread remounts the whole chat column. So a mount animation cannot signal "thread opened"; the theme keys it on the active sidebar row instead (`[data-sidebar-row$="<hex>"][aria-current]`).
- Sidebar row card: `[data-thread-item] > div[role=button][data-sidebar-row="<env>:<thread id>"][data-testid=sidebar-row-card]`, `aria-current="page"` when active, `relative overflow-hidden`, `::after` unused. The `<li>` has `content-visibility: auto`.
- Running thread: the row card's `aria-label` becomes `"<title>, Working, <project>"` and its status slot shows `svg.lucide-circle-dashed` + "Working Ns". No `aria-busy` on the row. No `lucide-loader` icon was seen in any state.
- Timeline while running: extra rows `[data-timeline-row-kind=working]` ("Working for Ns", id `working-indicator-row`) and `[data-timeline-row-kind=thinking]` (id `live-activity-row`, T3's own `live-activity-focus` animations). Other kinds seen: `message`, `turn-fold`, `work-toggle`.
- Streaming: `.chat-markdown` gets a bare `data-streaming` attribute (empty value, not "true") while the message streams, and loses it when done. The node is the same before, during and after; existing rows do not remount when a message arrives.
- Draft screen: the conversation area holds only `[data-timeline-loading="true"]` (opaque `bg-background`); the composer lives in a sibling overlay `[data-workspace-area=composer][data-chat-composer-overlay]` (`absolute inset-0 flex items-center` on a draft, `absolute inset-x-0 bottom-0` in a thread). The composer is never inside `[data-workspace-area=conversation]`.
- `[data-assistant-citation-viewport]` is the non-scrolling parent of `.messages-timeline-scroll` (relative, full conversation size, pseudos unused). It does not exist on a draft.
- Row containers have `contain: content`, so nothing inside a row can paint outside it.
- Virtualisation: with a 380 px viewport and a 1236 px timeline, scrolling end to end remounted no rows (draw distance is at least ~850 px). No thread long enough to force a remount exists in the test instance.
- Popups: `[data-slot=tooltip-popup|menu-popup|popover-popup|dialog-popup]`; Settings opens as a dialog. The model picker is a popover.

## Facts found while building the Watcher round (v0.1.10, real app)

- Composer nesting: `[data-slot=composer-shell]` (::before used) > `[data-slot=composer-host]` (relative, ::after used, `aria-busy` stays "false" during a run) > div > `form[data-chat-composer-form]` > div > `[data-chat-composer-main-surface]` (relative, ::after used) > `[data-chat-composer-surface]` (static, overflow visible, both pseudos free). No ancestor clips.
- While a turn runs the submit button's `aria-label` changes from "Submit message" to "Stop generation" (same position, inside the surface) for the whole turn: seen from +1.6 s to the end in a real send. In the same run: `[data-timeline-row-kind=working]` and `=thinking` rows, the active sidebar row's label gains ", Working," about .2 s later, `[data-streaming]` (bare attribute) only while text streams (about 3 s for eight paragraphs). `[data-thread-now-line]` never appeared.
- Failed turn: an error banner `div.chat-banner-lane > div > [data-slot=alert][data-variant=error][role=alert]` over the thread (sibling of the conversation area, dismissable, still there when the thread is reopened), a `[data-timeline-row-kind=work]` row "Provider error", and the sidebar label ", Failed," until the thread is opened. `[role=alert]` is also used by settings forms and file viewers; `data-variant=error` alerts also appear inside settings and pairing dialogs (not in the banner lane).
- Confirm dialog (sidebar row context menu > Delete): `[data-slot=alert-dialog-popup][role=alertdialog]` > `alert-dialog-header` (title, description) + `[data-slot=alert-dialog-footer]` > `button[data-slot=alert-dialog-close]` "Cancel" + `button[data-slot=button]` "Confirm". No `data-variant` on either button. Escape cancels.
- Placeholder: `div.pointer-events-none.absolute.inset-0.text-placeholder` beside the editor, text "Ask anything. @ files, $ skills, / commands" on threads and drafts. Removed from the DOM while the editor has text; a new node is mounted when it is emptied.
- Workspace children order: banner lane, `[data-workspace-area=conversation]`, `[data-workspace-area=composer]`, `[data-workspace-area=details]`.
- A `prefers-reduced-motion` media query inside an SVG used as a CSS background did not stop the SVG's animation under CDP media emulation.
- T3's theme loader accepts nested CSS rules as written.
