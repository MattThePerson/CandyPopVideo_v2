<script lang="ts">
    export interface ScanOptions {
        reparse_filenames: boolean;
        reread_json:       boolean;
        redo_attributes:   boolean;
        rehash:            boolean;
        path_filter:       string;
    }

    /* Props */
    let { disabled, onStart }: {
        disabled: boolean;
        onStart: (opts: ScanOptions) => void;
    } = $props();

    let reparseFilenames = $state(false);
    let rereadJson       = $state(false);
    let redoAttributes   = $state(false);
    let rehash           = $state(false);
    let pathFilter       = $state('');
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<section class="card">
    <h2 class="section-title">Scan Libraries</h2>

    <div class="opts">
        <label class="opt">
            <input type="checkbox" bind:checked={reparseFilenames} {disabled} />
            Reparse filenames
        </label>
        <label class="opt">
            <input type="checkbox" bind:checked={rereadJson} {disabled} />
            Reread JSON sidecar metadata
        </label>
        <label class="opt">
            <input type="checkbox" bind:checked={redoAttributes} {disabled} />
            Redo video attributes (ffprobe)
        </label>
        <label class="opt">
            <input type="checkbox" bind:checked={rehash} {disabled} />
            Rehash videos
        </label>
    </div>

    <input
        class="path-input"
        type="text"
        placeholder="Path filter — optional, comma-separated (e.g. collection-name)"
        bind:value={pathFilter}
        {disabled}
    />

    <button
        class="btn-primary"
        {disabled}
        onclick={() => onStart({ reparse_filenames: reparseFilenames, reread_json: rereadJson, redo_attributes: redoAttributes, rehash, path_filter: pathFilter })}
    >
        Scan Libraries
    </button>
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
        gap: 0.9rem;
    }

    .section-title {
        font-size: 0.68rem;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        color: #555;
        font-weight: 600;
        margin: 0;
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
    .opt.warn { color: #c89040; }

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

    .btn-primary {
        background: #01b8b8;
        color: #000;
        font-weight: 700;
        font-size: 0.85rem;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1.2rem;
        cursor: pointer;
        align-self: flex-start;
        transition: background 0.15s;
    }
    .btn-primary:hover:not(:disabled) { background: #00d0d0; }
    .btn-primary:disabled { opacity: 0.35; cursor: not-allowed; }
</style>
