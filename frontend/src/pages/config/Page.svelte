<!-- pages/config/Page.svelte -->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { EditorView, basicSetup } from 'codemirror';
    import { yaml } from '@codemirror/lang-yaml';
    import { oneDark } from '@codemirror/theme-one-dark';
    import { vim } from '@replit/codemirror-vim';
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

    onMount(async () => {
        document.title = 'Config | CandyPop';
        const serverContent = await loadFromServer();
        const initialContent = configBuffer.isDirty ? configBuffer.content : serverContent;

        view = new EditorView({
            doc: initialContent,
            extensions: [
                basicSetup,
                vim(),
                yaml(),
                oneDark,
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

    onDestroy(() => view?.destroy());

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
            <button class="btn-secondary" onclick={handleRestore}>Restore Defaults</button>
            <button class="btn-primary" disabled={status === 'saving'} onclick={handleSave}>
                {status === 'saving' ? 'Saving…' : 'Save'}
            </button>
        </div>
    </div>

    {#if result}
        <div class="result-bar" class:is-error={!result.ok} class:is-ok={result.ok}>
            {#each result.errors as e}<p class="msg-error">✕ {e}</p>{/each}
            {#each result.warnings as w}<p class="msg-warn">⚠ {w}</p>{/each}
            {#if result.saved && !result.requires_restart}<p class="msg-ok">✓ Config saved.</p>{/if}
            {#if result.requires_restart}
                <p class="msg-restart">⟳ preview_media_dir changed — restart the server to apply.</p>
            {/if}
        </div>
    {/if}

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
        padding: 1.5rem 2rem 2rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        flex: 1;
        min-height: 0;
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

    .result-bar {
        background: #0d1212;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 6px;
        padding: 0.7rem 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
    }
    .result-bar.is-error { border-color: rgba(220, 60, 60, 0.35); }
    .result-bar.is-ok    { border-color: rgba(40, 180, 100, 0.3); }

    .msg-error   { color: #dc3c3c; font-size: 0.82rem; margin: 0; }
    .msg-warn    { color: #c8882a; font-size: 0.82rem; margin: 0; }
    .msg-ok      { color: #3dba6e; font-size: 0.82rem; margin: 0; }
    .msg-restart { color: #f97316; font-size: 0.82rem; margin: 0; }

    .editor-wrap {
        flex: 1;
        min-height: 400px;
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
