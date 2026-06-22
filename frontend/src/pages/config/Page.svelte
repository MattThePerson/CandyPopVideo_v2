<!-- pages/config/Page.svelte -->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { EditorView, basicSetup } from 'codemirror';
    import { keymap } from '@codemirror/view';
    import { Prec } from '@codemirror/state';
    import { indentWithTab } from '@codemirror/commands';
    import { yaml } from '@codemirror/lang-yaml';
    import { oneDark } from '@codemirror/theme-one-dark';
    import { vim, Vim } from '@replit/codemirror-vim';
    import { navigate } from '../../lib/router/router.svelte';
    import { configBuffer } from '../../lib/stores/configBuffer.svelte';
    import ConfirmDialog from '../../lib/components/ConfirmDialog.svelte';

    interface ValidationResult {
        ok:              boolean;
        errors:          string[];
        warnings:        string[];
        requires_restart: boolean;
        saved?:          boolean;
    }

    let editorEl       = $state<HTMLDivElement | undefined>(undefined);
    let view:          EditorView | null = null;
    let status         = $state<'idle' | 'saving' | 'saved' | 'error'>('idle');
    let result         = $state<ValidationResult | null>(null);
    let showDiscard    = $state(false);
    let showRestore    = $state(false);
    let suppressUpdate = false;

    function setEditorContent(content: string) {
        if (!view) return;
        suppressUpdate = true;
        view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: content } });
        suppressUpdate = false;
    }

    async function loadFromServer(): Promise<string> {
        const res = await fetch('/api/config');
        return res.ok ? res.text() : '';
    }

    async function resetEditor() {
        const text = await loadFromServer();
        setEditorContent(text);
        configBuffer.clear();
        result = null;
        status = 'idle';
    }

    // Redirect printable keystrokes and Tab to the editor when it isn't focused.
    function handleWindowKeydown(e: KeyboardEvent) {
        if (!view) return;
        const target = e.target as Element;
        if (editorEl?.contains(target)) return;
        if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) return;
        const isPrintable = e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey;
        const isTab = e.key === 'Tab' && !e.ctrlKey && !e.altKey && !e.metaKey;
        if (!isPrintable && !isTab) return;
        view.focus();
        view.contentDOM.dispatchEvent(new KeyboardEvent(e.type, {
            key: e.key, code: e.code,
            shiftKey: e.shiftKey, ctrlKey: e.ctrlKey, altKey: e.altKey, metaKey: e.metaKey,
            bubbles: true, cancelable: true,
        }));
        e.preventDefault();
        e.stopPropagation();
    }

    function handleBeforeUnload(e: BeforeUnloadEvent) {
        if (configBuffer.isDirty) { e.preventDefault(); e.returnValue = ''; }
    }

    onMount(async () => {
        document.title = 'Config | CandyPop';
        document.querySelector('footer')?.style.setProperty('display', 'none');
        window.addEventListener('keydown', handleWindowKeydown, true);
        window.addEventListener('beforeunload', handleBeforeUnload);

        const serverContent = await loadFromServer();
        const initialContent = configBuffer.isDirty ? configBuffer.content : serverContent;

        // :w and :write trigger the same save as the Save button.
        Vim.defineEx('write', 'w', () => { handleSave(); });

        // High-priority keymap: scroll commands + Tab/Shift-Tab so they never leak to browser focus cycling.
        const vimScrollKeys = Prec.highest(keymap.of([
            { key: 'Ctrl-d', run: v => { v.scrollDOM.scrollTop += v.scrollDOM.clientHeight / 2; return true; } },
            { key: 'Ctrl-u', run: v => { v.scrollDOM.scrollTop -= v.scrollDOM.clientHeight / 2; return true; } },
            { key: 'Ctrl-e', run: v => { v.scrollDOM.scrollTop += 20; return true; } },
            { key: 'Ctrl-y', run: v => { v.scrollDOM.scrollTop -= 20; return true; } },
            indentWithTab,
        ]));

        view = new EditorView({
            doc: initialContent,
            extensions: [
                basicSetup,
                vim(),
                yaml(),
                oneDark,
                vimScrollKeys,
                EditorView.updateListener.of(update => {
                    if (update.docChanged && !suppressUpdate) {
                        configBuffer.content = update.state.doc.toString();
                    }
                }),
                EditorView.theme({ '&': { height: '100%' }, '.cm-scroller': { overflow: 'auto' } }),
            ],
            parent: editorEl!,
        });
    });

    onDestroy(() => {
        view?.destroy();
        document.querySelector('footer')?.style.removeProperty('display');
        window.removeEventListener('keydown', handleWindowKeydown, true);
        window.removeEventListener('beforeunload', handleBeforeUnload);
    });

    async function handleSave() {
        if (!view) return;
        status = 'saving';
        result = null;
        const body = view.state.doc.toString();
        const res  = await fetch('/api/config/save', {
            method: 'POST',
            headers: { 'Content-Type': 'text/plain' },
            body,
        }).catch(() => null);

        if (!res) { status = 'error'; return; }
        result = await res.json();
        status = result?.saved ? 'saved' : 'error';
        if (result?.saved) configBuffer.clear();
    }

    function handleDiscard() { showDiscard = true; }

    async function confirmDiscard() {
        showDiscard = false;
        await resetEditor();
    }

    function handleRestore() { showRestore = true; }

    async function confirmRestore() {
        showRestore = false;
        await fetch('/api/config/restore-defaults', { method: 'POST' });
        await resetEditor();
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="config-page">
    <div class="toolbar">
        <button class="btn-back" onclick={() => navigate('/dashboard')}>← Dashboard</button>
        <h1 class="title">Config Editor</h1>
        <div class="toolbar-actions">
            {#if configBuffer.isDirty}
                <span class="dirty-notice">Unsaved changes from {new Date(configBuffer.savedAt).toLocaleString()}</span>
                <button class="btn-secondary" onclick={handleDiscard}>Discard</button>
            {/if}
            {#if result}
                {#if !result.ok && result.errors.length > 0}
                    <span class="save-status error">✕ {result.errors[0]}</span>
                {:else if result.requires_restart}
                    <span class="save-status restart">⟳ Restart required</span>
                {:else if result.warnings.length > 0}
                    <span class="save-status warn">⚠ {result.warnings[0]}</span>
                {:else if result.saved}
                    <span class="save-status ok">✓ Saved</span>
                {/if}
            {/if}
            <button class="btn-secondary" onclick={handleRestore}>Restore Defaults</button>
            <button class="btn-primary" disabled={status === 'saving'} onclick={handleSave}>
                {status === 'saving' ? 'Saving…' : 'Save'}
            </button>
        </div>
    </div>

    <div class="editor-wrap" bind:this={editorEl}></div>
</div>

{#if showDiscard}
    <ConfirmDialog
        message="Discard all unsaved changes and reload from disk?"
        confirmLabel="Discard"
        onConfirm={confirmDiscard}
        onCancel={() => showDiscard = false}
    />
{/if}

{#if showRestore}
    <ConfirmDialog
        message="Replace config.yaml with the built-in defaults? This will overwrite your current settings."
        confirmLabel="Restore Defaults"
        onConfirm={confirmRestore}
        onCancel={() => showRestore = false}
    />
{/if}

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .config-page {
        width: 100%;
        max-width: 1200px;
        padding: 1.5rem 2rem 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        /* Pin to remaining viewport below the header so the page never scrolls. */
        height: calc(100dvh - 3.1rem);
        overflow: hidden;
        box-sizing: border-box;
    }

    .toolbar {
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .title {
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #555;
        font-weight: 600;
        margin: 0;
        flex: 1;
    }

    .toolbar-actions {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        flex-wrap: wrap;
    }

    .dirty-notice {
        font-size: 0.75rem;
        color: #c8882a;
    }

    .btn-back {
        background: transparent;
        border: none;
        color: #666;
        font-size: 0.82rem;
        cursor: pointer;
        padding: 0.3rem 0;
    }
    .btn-back:hover { color: #aaa; }

    .btn-secondary {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #aaa;
        font-size: 0.83rem;
        border-radius: 5px;
        padding: 0.4rem 0.9rem;
        cursor: pointer;
    }
    .btn-secondary:hover { border-color: rgba(255,255,255,0.35); color: #ddd; }

    .btn-primary {
        background: #f97316;
        border: none;
        color: #000;
        font-weight: 600;
        font-size: 0.83rem;
        border-radius: 5px;
        padding: 0.4rem 1rem;
        cursor: pointer;
    }
    .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-primary:not(:disabled):hover { background: #ea6c0b; }

    .save-status         { font-size: 0.82rem; }
    .save-status.ok      { color: #3dba6e; }
    .save-status.error   { color: #dc3c3c; }
    .save-status.warn    { color: #c8882a; }
    .save-status.restart { color: #f97316; }

    .editor-wrap {
        flex: 1;
        min-height: 0;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 6px;
        overflow: hidden;
        font-size: 0.88rem;
    }

    /* Override CodeMirror container to fill the wrapper */
    .editor-wrap :global(.cm-editor) {
        height: 100%;
    }
</style>
