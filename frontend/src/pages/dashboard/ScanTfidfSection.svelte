<script lang="ts">
    export interface ScanOptions {
        rederive_metadata: boolean;
        redo_attributes:   boolean;
        rehash:            boolean;
        path_filter:       string;
        quick_scan:        boolean;
        novel_files_only:  boolean;
        read_json:         boolean;
    }

    /* Props */
    let { disabled, onStartScan, onStartTfidf }: {
        disabled:     boolean;
        onStartScan:  (opts: ScanOptions) => void;
        onStartTfidf: () => void;
    } = $props();

    let redoMetadata   = $state(false);
    let redoAttributes = $state(false);
    let rehash         = $state(false);
    let pathFilter     = $state('');
    let readJson       = $state(true);
    let quickDropOpen  = $state(false);

    function startScan(quick: boolean, novelOnly = false) {
        quickDropOpen = false;
        onStartScan({
            rederive_metadata: redoMetadata,
            redo_attributes:   redoAttributes,
            rehash,
            path_filter:       pathFilter,
            quick_scan:        quick,
            novel_files_only:  novelOnly,
            read_json:         readJson,
        });
    }

    // Close the dropdown when clicking outside the split button
    $effect(() => {
        if (!quickDropOpen) return;
        function close(e: MouseEvent) {
            if (!(e.target as Element).closest('.quick-scan-split')) quickDropOpen = false;
        }
        window.addEventListener('mousedown', close);
        return () => window.removeEventListener('mousedown', close);
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<section class="card">
    <!-- Scan subpanel -->
    <div class="subpanel">
        <h2 class="section-title">Scan Libraries</h2>

        <div class="opts">
            <label class="opt">
                <input type="checkbox" bind:checked={redoMetadata} {disabled} />
                Redo metadata extraction (filenames and JSON sidecar)
            </label>
            <label class="opt">
                <input type="checkbox" bind:checked={redoAttributes} {disabled} />
                Redo video attributes (filedata, ffmpeg)
            </label>
            <label class="opt">
                <input type="checkbox" bind:checked={rehash} {disabled} />
                Rehash videos
            </label>
        </div>

        <input
            class="path-input"
            type="text"
            placeholder="Path filter — optional, comma-separated"
            bind:value={pathFilter}
            {disabled}
        />

        <div class="btn-row">
            <div class="quick-scan-split" class:disabled>
                <button
                    class="split-main"
                    title="Scan only folders touched since last scan"
                    {disabled}
                    onclick={() => startScan(true)}
                >Quick Scan</button>
                <button
                    class="split-arrow"
                    {disabled}
                    onclick={() => quickDropOpen = !quickDropOpen}
                    aria-label="More quick scan options"
                >▾</button>
                {#if quickDropOpen}
                    <div class="split-dropdown">
                        <button onclick={() => startScan(true, true)}>Novel Files Only</button>
                    </div>
                {/if}
            </div>
            <button
                class="btn-primary"
                title="Scan all files, mark deleted as unlinked"
                {disabled}
                onclick={() => startScan(false)}
            >Full Scan</button>
        </div>

        <label class="opt">
            <input type="checkbox" bind:checked={readJson} {disabled} />
            Read JSON sidecars
        </label>
    </div>

    <!-- TF-IDF subpanel -->
    <div class="subpanel tfidf-subpanel">
        <h2 class="section-title">TF-IDF Model <span class="py-badge">Python</span></h2>
        <p class="subpanel-desc">Search ranking and similar-videos. Rebuild after scanning new videos.</p>
        <button class="btn-secondary" {disabled} onclick={onStartTfidf}>
            Rebuild TF-IDF
        </button>
    </div>
</section>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .card {
        background: #0d1212;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 1.2rem 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 0;
    }

    .subpanel {
        display: flex;
        flex-direction: column;
        gap: 0.9rem;
        padding-bottom: 1.1rem;
    }

    .tfidf-subpanel {
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 1rem;
        padding-bottom: 0;
        gap: 0.75rem;
    }

    .section-title {
        font-size: 0.68rem;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        color: #555;
        font-weight: 600;
        margin: 0;
    }

    .py-badge {
        font-size: 0.62rem;
        background: rgba(117, 40, 104, 0.35);
        color: #c080b8;
        border-radius: 3px;
        padding: 0 0.35rem;
        margin-left: 0.4rem;
        text-transform: none;
        letter-spacing: 0;
        font-weight: 500;
        vertical-align: middle;
    }

    .opts { display: flex; flex-direction: column; gap: 0.45rem; }

    .opt {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-size: 0.85rem;
        color: #bbb;
        cursor: pointer;
        user-select: none;
    }
    .opt input[type="checkbox"] { accent-color: #01b8b8; cursor: pointer; }

    .path-input {
        background: #060a0a;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        color: #ccc;
        font-size: 0.82rem;
        padding: 0.45rem 0.7rem;
        outline: none;
        width: 100%;
        box-sizing: border-box;
    }
    .path-input:focus { border-color: rgba(1, 184, 184, 0.5); }
    .path-input::placeholder { color: #333; }

    .subpanel-desc { font-size: 0.82rem; color: #666; margin: 0; line-height: 1.5; }

    .btn-row {
        display: flex;
        gap: 0.6rem;
    }

    /* Split button */
    .quick-scan-split {
        position: relative;
        display: flex;
    }
    .split-main {
        background: #01b8b8;
        color: #000;
        font-weight: 700;
        font-size: 0.85rem;
        border: none;
        border-radius: 5px 0 0 5px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: background 0.15s;
    }
    .split-arrow {
        background: #01b8b8;
        color: #000;
        font-weight: 700;
        font-size: 0.78rem;
        border: none;
        border-left: 1px solid rgba(0, 0, 0, 0.2);
        border-radius: 0 5px 5px 0;
        padding: 0.5rem 0.5rem;
        cursor: pointer;
        transition: background 0.15s;
    }
    .split-main:hover:not(:disabled),
    .split-arrow:hover:not(:disabled) { background: #00d0d0; }
    .quick-scan-split.disabled .split-main,
    .quick-scan-split.disabled .split-arrow { opacity: 0.35; cursor: not-allowed; }

    .split-dropdown {
        position: absolute;
        top: calc(100% + 4px);
        left: 0;
        background: #0d1212;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 5px;
        min-width: 100%;
        z-index: 50;
        overflow: hidden;
    }
    .split-dropdown button {
        display: block;
        width: 100%;
        padding: 0.45rem 0.9rem;
        background: none;
        border: none;
        color: #ccc;
        font-size: 0.83rem;
        text-align: left;
        cursor: pointer;
        white-space: nowrap;
    }
    .split-dropdown button:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }

    .btn-primary {
        background: #01b8b8;
        color: #000;
        font-weight: 700;
        font-size: 0.85rem;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1.2rem;
        cursor: pointer;
        transition: background 0.15s;
    }
    .btn-primary:hover:not(:disabled) { background: #00d0d0; }
    .btn-primary:disabled { opacity: 0.35; cursor: not-allowed; }

    .btn-secondary {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #aaa;
        font-size: 0.83rem;
        border-radius: 5px;
        padding: 0.45rem 1rem;
        cursor: pointer;
        align-self: flex-start;
        transition: border-color 0.15s, color 0.15s;
    }
    .btn-secondary:hover:not(:disabled) { border-color: rgba(255,255,255,0.35); color: #ddd; }
    .btn-secondary:disabled { opacity: 0.35; cursor: not-allowed; }
</style>
