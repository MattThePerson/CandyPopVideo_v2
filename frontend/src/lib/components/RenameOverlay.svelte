<script lang="ts">
    /* Props */
    let {
        filename,
        onClose,
        onRename,
    }: {
        filename: string;
        onClose: () => void;
        onRename: (newStem: string) => Promise<{ ok: boolean; error?: string }>;
    } = $props();

    const lastDot = filename.lastIndexOf('.');
    const ext = lastDot > 0 ? filename.slice(lastDot) : '';
    const initStem = lastDot > 0 ? filename.slice(0, lastDot) : filename;

    const ILLEGAL_RE = /[\\/:*?"<>|]/;

    let inputValue = $state(initStem);
    let status = $state<'idle' | 'loading' | 'error'>('idle');
    let errorMsg = $state('');
    let inputEl: HTMLInputElement | undefined;

    let trimmed = $derived(inputValue.trim());
    let hasIllegal = $derived(ILLEGAL_RE.test(inputValue));
    let isEmpty = $derived(trimmed.length === 0);
    let isUnchanged = $derived(trimmed === initStem);
    let canSubmit = $derived(!hasIllegal && !isEmpty && !isUnchanged && status !== 'loading');

    $effect(() => {
        inputEl?.focus();
        inputEl?.select();
    });

    // Global Escape listener — fires before Page.svelte's listener because Svelte
    // mounts child components after parents, so this registers later and runs later
    // in bubble phase, but Page.svelte gates its handler on !renameOpen anyway.
    $effect(() => {
        function handler(e: KeyboardEvent) {
            if (e.key === 'Escape') onClose();
        }
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    });

    async function submit() {
        if (!canSubmit) return;
        status = 'loading';
        errorMsg = '';
        const result = await onRename(trimmed);
        if (!result.ok) {
            status = 'error';
            errorMsg = result.error ?? 'Unknown error';
        }
        // On success the parent unmounts this component, so we just stay loading.
    }

    function onInputKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            e.preventDefault();
            submit();
        }
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="backdrop" onclick={onClose} role="presentation">
    <div
        class="modal"
        onclick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Rename video"
    >
        <h2 class="title">Rename Video</h2>

        <div class="input-row">
            <input
                bind:this={inputEl}
                bind:value={inputValue}
                class:invalid={hasIllegal}
                onkeydown={onInputKeydown}
                disabled={status === 'loading'}
                spellcheck="false"
                autocomplete="off"
                type="text"
                class="stem-input"
            />
            {#if ext}
                <span class="ext-label">{ext}</span>
            {/if}
        </div>

        {#if hasIllegal}
            <p class="hint error">Illegal characters: \ / : * ? &quot; &lt; &gt; |</p>
        {:else if isEmpty}
            <p class="hint error">Filename cannot be empty</p>
        {:else}
            <p class="hint">&nbsp;</p>
        {/if}

        {#if status === 'error'}
            <p class="error-msg">{errorMsg}</p>
        {/if}

        <div class="actions">
            <button class="btn-cancel" onclick={onClose} disabled={status === 'loading'}>
                Cancel
            </button>
            {#if status === 'error'}
                <button class="btn-primary" onclick={submit}>Retry</button>
            {:else}
                <button class="btn-primary" onclick={submit} disabled={!canSubmit}>
                    {status === 'loading' ? 'Renaming…' : 'Rename'}
                </button>
            {/if}
        </div>
    </div>
</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.75);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .modal {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 1.5rem;
        width: min(780px, 90vw);
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }

    .title {
        margin: 0 0 0.25rem;
        font-size: 1rem;
        font-weight: 600;
        color: #e5e5e5;
    }

    .input-row {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }

    .stem-input {
        flex: 1;
        background: #0d0d0d;
        border: 1px solid #444;
        border-radius: 4px;
        color: #e5e5e5;
        font-size: 0.88rem;
        padding: 0.45rem 0.6rem;
        outline: none;
        font-family: inherit;
        transition: border-color 0.15s;
    }

    .stem-input:focus {
        border-color: #666;
    }

    .stem-input.invalid {
        border-color: #ef4444;
        color: #ef4444;
    }

    .stem-input:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .ext-label {
        color: #555;
        font-size: 0.88rem;
        white-space: nowrap;
        user-select: none;
    }

    .hint {
        margin: 0;
        font-size: 0.75rem;
        color: #555;
        min-height: 1em;
    }

    .hint.error {
        color: #ef4444;
    }

    .error-msg {
        margin: 0;
        font-size: 0.8rem;
        color: #fca5a5;
        background: #2d1010;
        border: 1px solid #5a1a1a;
        border-radius: 4px;
        padding: 0.4rem 0.6rem;
        word-break: break-word;
    }

    .actions {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
        margin-top: 0.25rem;
    }

    button {
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.83rem;
        padding: 0.4rem 0.9rem;
        font-family: inherit;
        transition: opacity 0.15s;
    }

    button:disabled {
        opacity: 0.35;
        cursor: not-allowed;
    }

    .btn-cancel {
        background: #2a2a2a;
        color: #999;
    }

    .btn-cancel:hover:not(:disabled) {
        background: #333;
    }

    .btn-primary {
        background: #f97316;
        color: #000;
        font-weight: 600;
    }

    .btn-primary:hover:not(:disabled) {
        opacity: 0.82;
    }
</style>
