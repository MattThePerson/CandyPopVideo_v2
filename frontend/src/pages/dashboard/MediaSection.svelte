<script lang="ts">
    export interface MediaOptions {
        media_type:  string;
        redo:        boolean;
        collection:  string;
        path_filter: string;
        days_filter: number;
    }

    interface MediaTypeStatus { with: number; without: number; total: number; pct: number; }
    interface MediaStatusResponse {
        teaser_thumbs:  MediaTypeStatus;
        seek_thumbs:    MediaTypeStatus;
        teasers:        MediaTypeStatus;
        preview_thumbs: MediaTypeStatus;
    }
    interface CollectionStat { name: string; count: number; }

    /* Props */
    let { stats, mediaStatus, mediaLoading, disabled, onStart, onRefreshStatus }: {
        stats:             { collections: CollectionStat[] } | null;
        mediaStatus:       MediaStatusResponse | null;
        mediaLoading:      boolean;
        disabled:          boolean;
        onStart:           (opts: MediaOptions) => void;
        onRefreshStatus:   () => void;
    } = $props();

    let mediaType  = $state('all');
    let redo       = $state(false);
    let collection = $state('');
    let pathFilter = $state('');
    let daysFilter = $state(0);

    const mediaTypes: { value: string; label: string; python?: boolean }[] = [
        { value: 'all',           label: 'All' },
        { value: 'teasers',       label: 'Teasers' },
        { value: 'teaser_thumbs', label: 'Teaser Thumbs' },
        { value: 'seek_thumbs',   label: 'Seek Thumbs' },
        { value: 'preview_thumbs', label: 'Preview Thumbs', python: true },
    ];

    const coverageRows: { key: keyof MediaStatusResponse; label: string; python?: boolean }[] = [
        { key: 'teaser_thumbs',  label: 'Teaser Thumbs' },
        { key: 'seek_thumbs',    label: 'Seek Thumbs' },
        { key: 'teasers',        label: 'Teasers' },
        { key: 'preview_thumbs', label: 'Preview Thumbs', python: true },
    ];

    function quickStart(days: number) {
        daysFilter = days;
        onStart({ media_type: 'all', redo: false, collection, path_filter: pathFilter, days_filter: days });
    }

    function generate() {
        onStart({ media_type: mediaType, redo, collection, path_filter: pathFilter, days_filter: daysFilter });
    }

    function fmt(n: number) { return n.toLocaleString(); }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<section class="card">
    <h2 class="section-title">Media Generation</h2>

    <!-- Quick actions -->
    <div class="quick-row">
        <span class="quick-label">Quick:</span>
        <button class="btn-quick" {disabled} onclick={() => quickStart(1)}>New (24 h)</button>
        <button class="btn-quick" {disabled} onclick={() => quickStart(7)}>New (7 d)</button>
        <button class="btn-quick" {disabled} onclick={() => quickStart(0)}>All videos</button>
    </div>

    <!-- Type selector -->
    <div class="type-row">
        {#each mediaTypes as t}
            <label class="type-opt">
                <input type="radio" name="media-type" value={t.value} bind:group={mediaType} {disabled} />
                {t.label}{#if t.python}<span class="py-badge">Python</span>{/if}
            </label>
        {/each}
    </div>

    <!-- Filters -->
    <div class="filter-grid">
        <select class="select-input" bind:value={collection} {disabled}>
            <option value="">All collections</option>
            {#each stats?.collections ?? [] as c}
                <option value={c.name}>{c.name} ({fmt(c.count)})</option>
            {/each}
        </select>
        <input class="text-input" type="text"   placeholder="Path filter"       bind:value={pathFilter} {disabled} />
        <input class="text-input" type="number" placeholder="Added in last N days (0 = all)" bind:value={daysFilter} min="0" {disabled} />
    </div>

    <div class="action-row">
        <label class="redo-opt">
            <input type="checkbox" bind:checked={redo} {disabled} />
            Redo existing
        </label>
        <button class="btn-primary" {disabled} onclick={generate}>Generate Media</button>
    </div>

    <!-- Coverage bars -->
    <div class="coverage">
        <div class="coverage-header">
            <span class="coverage-title">Media Coverage</span>
            <button class="btn-refresh" {disabled} onclick={onRefreshStatus}>
                {mediaLoading ? 'Loading…' : 'Refresh'}
            </button>
        </div>

        {#if mediaStatus}
            {#each coverageRows as row}
                {@const s = mediaStatus[row.key]}
                <div class="bar-row">
                    <span class="bar-label">
                        {row.label}
                        {#if row.python}<span class="py-badge">Python</span>{/if}
                    </span>
                    <div class="bar-track">
                        <div class="bar-fill" style="width: {s.pct.toFixed(1)}%"></div>
                    </div>
                    <span class="bar-pct">{s.pct.toFixed(1)}%</span>
                    <span class="bar-counts">{fmt(s.with)} / {fmt(s.total)}</span>
                </div>
            {/each}
        {:else}
            <p class="no-status">Click Refresh to check media coverage.</p>
        {/if}
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

    /* Quick actions */
    .quick-row { display: flex; align-items: center; gap: 0.5rem; }
    .quick-label { font-size: 0.78rem; color: #444; }
    .btn-quick {
        background: transparent;
        border: 1px solid rgba(1, 184, 184, 0.35);
        color: #01b8b8;
        border-radius: 4px;
        font-size: 0.78rem;
        padding: 0.25rem 0.7rem;
        cursor: pointer;
        transition: border-color 0.15s, background 0.15s;
    }
    .btn-quick:hover:not(:disabled) { background: rgba(1, 184, 184, 0.08); border-color: #01b8b8; }
    .btn-quick:disabled { opacity: 0.3; cursor: not-allowed; }

    /* Type selector */
    .type-row { display: flex; gap: 1rem; flex-wrap: wrap; }
    .type-opt {
        display: flex; align-items: center; gap: 0.4rem;
        font-size: 0.83rem; color: #aaa; cursor: pointer; user-select: none;
    }
    .type-opt input[type="radio"] { accent-color: #01b8b8; cursor: pointer; }

    /* Filters */
    .filter-grid { display: flex; flex-direction: column; gap: 0.4rem; }
    .select-input, .text-input {
        background: #060a0a;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        color: #ccc;
        font-size: 0.82rem;
        padding: 0.42rem 0.65rem;
        outline: none;
        width: 100%;
        box-sizing: border-box;
    }
    .select-input:focus, .text-input:focus { border-color: rgba(1, 184, 184, 0.5); }
    .text-input::placeholder { color: #333; }
    .select-input option { background: #111; }

    /* Action row */
    .action-row { display: flex; align-items: center; gap: 1rem; }
    .redo-opt {
        display: flex; align-items: center; gap: 0.45rem;
        font-size: 0.82rem; color: #888; cursor: pointer; user-select: none;
    }
    .redo-opt input[type="checkbox"] { accent-color: #01b8b8; cursor: pointer; }

    .btn-primary {
        background: #01b8b8; color: #000; font-weight: 700;
        font-size: 0.85rem; border: none; border-radius: 5px;
        padding: 0.48rem 1.1rem; cursor: pointer; transition: background 0.15s;
    }
    .btn-primary:hover:not(:disabled) { background: #00d0d0; }
    .btn-primary:disabled { opacity: 0.35; cursor: not-allowed; }

    /* Coverage */
    .coverage {
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 0.9rem;
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
    }
    .coverage-header { display: flex; align-items: center; justify-content: space-between; }
    .coverage-title {
        font-size: 0.68rem; letter-spacing: 0.12em;
        text-transform: uppercase; color: #444; font-weight: 600;
    }
    .btn-refresh {
        background: transparent; border: 1px solid rgba(255,255,255,0.12);
        color: #666; border-radius: 4px; font-size: 0.74rem;
        padding: 0.2rem 0.55rem; cursor: pointer;
    }
    .btn-refresh:hover:not(:disabled) { color: #aaa; border-color: rgba(255,255,255,0.25); }
    .btn-refresh:disabled { opacity: 0.4; cursor: not-allowed; }

    .bar-row {
        display: grid;
        grid-template-columns: 140px 1fr 50px 100px;
        align-items: center;
        gap: 0.6rem;
    }
    .bar-label { font-size: 0.8rem; color: #888; }
    .py-badge {
        font-size: 0.62rem; background: rgba(117, 40, 104, 0.4);
        color: #c080b8; border-radius: 3px; padding: 0 0.3rem;
        margin-left: 0.3rem; vertical-align: middle;
    }
    .bar-track { height: 5px; background: #1a2020; border-radius: 3px; overflow: hidden; }
    .bar-fill  { height: 100%; background: #01b8b8; border-radius: 3px; transition: width 0.4s; }
    .bar-pct   { font-size: 0.78rem; color: #aaa; text-align: right; }
    .bar-counts { font-size: 0.72rem; color: #444; }

    .no-status { font-size: 0.8rem; color: #333; font-style: italic; margin: 0; }
</style>
