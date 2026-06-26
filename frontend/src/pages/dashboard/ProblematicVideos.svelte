<script lang="ts">
    import { onMount } from 'svelte';

    interface VideoEntry {
        hash:       string;
        name:       string;
        value:      string;
        path:       string;
        parent_dir: string;
    }
    interface ProblematicData {
        vfr:           VideoEntry[];
        audio_codec:   VideoEntry[];
        video_codec:   VideoEntry[];
        pix_fmt_10bit: VideoEntry[];
        hevc:          VideoEntry[];
        hdr:           VideoEntry[];
    }

    const LABELS: Record<keyof ProblematicData, string> = {
        vfr:           'Variable Frame Rate',
        audio_codec:   'Unsupported Audio Codec',
        video_codec:   'Unsupported Video Codec',
        pix_fmt_10bit: '10-bit / 12-bit Pixel Format',
        hevc:          'HEVC (H.265)',
        hdr:           'HDR Color Transfer',
    };

    const MAX_SHOWN = 20;

    let data        = $state<ProblematicData | null>(null);
    let loading     = $state(false);
    let filterText  = $state('');
    let hideFine    = $state(true);
    let markedFine  = $state(new Set<string>());
    let shownCount  = $state(new Map<string, number>());  // key → items shown
    let favStatus   = $state(new Map<string, boolean>()); // hash → is_favourite
    const fetched   = new Set<string>();

    const groups    = $derived(data ? (Object.keys(LABELS) as (keyof ProblematicData)[]).filter(k => data![k].length > 0) : []);
    const hasIssues = $derived(groups.length > 0);

    // Reset per-group shown counts when filter or hide-fine toggle changes.
    $effect(() => { filterText; hideFine; shownCount = new Map(); });

    async function refresh() {
        loading = true;
        data = await fetch('/api/dashboard/problematic-videos').then(r => r.json()).catch(() => null);
        loading = false;
    }

    onMount(async () => {
        const d = await fetch('/api/dashboard/marked-fine').then(r => r.json()).catch(() => ({ hashes: [] }));
        console.log('[marked-fine] loaded:', d?.hashes);
        markedFine = new Set(d?.hashes ?? []);
        await refresh();
    });

    function copy(text: string) { navigator.clipboard.writeText(text).catch(() => {}); }

    function getShown(key: string)   { return shownCount.get(key) ?? MAX_SHOWN; }
    function expandMore(key: string) { shownCount = new Map([...shownCount, [key, getShown(key) + MAX_SHOWN]]); }
    function contract(key: string)   { shownCount = new Map([...shownCount, [key, MAX_SHOWN]]); }

    function filteredEntries(entries: VideoEntry[]) {
        let result = entries;
        if (filterText.trim()) {
            const q = filterText.toLowerCase();
            result = result.filter(e => e.path.toLowerCase().includes(q));
        }
        if (hideFine) result = result.filter(e => !markedFine.has(e.hash));
        return result;
    }

    // Optimistic — flips UI immediately, then persists; no revert on error (non-critical).
    async function toggleMarkFine(hash: string) {
        const adding = !markedFine.has(hash);
        const s = new Set(markedFine);
        if (adding) s.add(hash); else s.delete(hash);
        markedFine = s;
        const action = adding ? 'add' : 'remove';
        await fetch(`/api/dashboard/marked-fine/${action}/${hash}`, { method: 'POST' }).catch(() => {});
    }

    async function fetchFav(hash: string) {
        if (fetched.has(hash)) return;
        fetched.add(hash);
        const d = await fetch(`/api/interact/get/${hash}`).then(r => r.json()).catch(() => null);
        if (d?.is_favourite) favStatus = new Map([...favStatus, [hash, true]]);
    }

    // Fires fetchFav once when the element enters the viewport.
    function lazyFav(node: Element, hash: string) {
        if (fetched.has(hash)) return { destroy() {} };
        const obs = new IntersectionObserver(es => {
            if (es[0].isIntersecting) { obs.disconnect(); fetchFav(hash); }
        }, { rootMargin: '80px' });
        obs.observe(node);
        return { destroy() { obs.disconnect(); } };
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

{#if hasIssues}
<section class="card warn-card">
    <div class="card-header">
        <h2 class="section-title">Potentially Problematic Videos</h2>
        <button class="refresh-btn" onclick={refresh} disabled={loading} title="Refresh">
            <span class:spinning={loading}>↺</span>
        </button>
    </div>

    <div class="controls-row">
        <input
            class="filter-input"
            type="text"
            placeholder="Filter by filepath…"
            bind:value={filterText}
        />
        <button class="hide-btn" class:active={hideFine} onclick={() => hideFine = !hideFine}>
            Hide marked fine
        </button>
    </div>

    {#each groups as key}
        {@const all      = filteredEntries(data![key])}
        {@const count    = getShown(key)}
        {@const shown    = all.slice(0, count)}
        {@const overflow = all.length - count}

        <details class="group">
            <summary class="group-header">
                <span class="group-label">{LABELS[key]}</span>
                <span class="group-count">{data![key].length}{filterText.trim() || hideFine ? ` (${all.length} shown)` : ''}</span>
            </summary>

            <ul class="entry-list">
                {#each shown as entry (entry.hash)}
                    <li class="entry" use:lazyFav={entry.hash}>
                        <button class="copy-btn" onclick={() => copy(entry.path)}       title={entry.path}>path</button>
                        <button class="copy-btn" onclick={() => copy(entry.parent_dir)} title={entry.parent_dir}>dir</button>
                        <button class="hash-btn" onclick={() => copy(entry.hash)}       title="Copy hash">{entry.hash}</button>
                        <span class="value-badge">{entry.value}</span>
                        <button
                            class="fine-btn"
                            class:marked={markedFine.has(entry.hash)}
                            onclick={() => toggleMarkFine(entry.hash)}
                            title={markedFine.has(entry.hash) ? 'Unmark' : 'Mark as fine'}
                        >✓</button>
                        {#if favStatus.get(entry.hash)}
                            <svg class="fav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                                <path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" fill="rgba(236,195,59,0.85)"/>
                            </svg>
                        {/if}
                        <a href="/video/{entry.hash}" class="entry-link">{entry.name}</a>
                    </li>
                {/each}

                {#if overflow > 0}
                    <li>
                        <button class="expand-btn" onclick={() => expandMore(key)}>…and {overflow} more</button>
                    </li>
                {:else if count > MAX_SHOWN}
                    <li>
                        <button class="expand-btn" onclick={() => contract(key)}>contract list</button>
                    </li>
                {/if}
            </ul>
        </details>
    {/each}
</section>
{/if}

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
        gap: 0.75rem;
    }
    .warn-card { border-color: rgba(200, 136, 42, 0.2); }

    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .section-title {
        font-size: 0.68rem; letter-spacing: 0.13em;
        text-transform: uppercase; color: #555; font-weight: 600; margin: 0;
    }

    .refresh-btn {
        background: none; border: 1px solid rgba(255,255,255,0.07);
        border-radius: 5px; padding: 0.15rem 0.5rem;
        color: #444; font-size: 0.85rem; cursor: pointer;
        transition: color 0.1s, border-color 0.1s; line-height: 1;
    }
    .refresh-btn:hover:not(:disabled) { color: #888; border-color: rgba(255,255,255,0.15); }
    .refresh-btn:disabled { opacity: 0.4; cursor: default; }

    @keyframes spin { to { transform: rotate(360deg); } }
    .spinning { display: inline-block; animation: spin 0.7s linear infinite; }

    .controls-row {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .filter-input {
        width: 210px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 5px;
        padding: 0.3rem 0.6rem;
        font-size: 0.78rem;
        color: #999;
        outline: none;
        transition: border-color 0.12s;
    }
    .filter-input::placeholder { color: #3a3a3a; }
    .filter-input:focus { border-color: rgba(255,255,255,0.15); color: #bbb; }

    .hide-btn {
        font-size: 0.73rem; color: #484848;
        background: none; border: 1px solid rgba(255,255,255,0.06);
        border-radius: 5px; padding: 0.28rem 0.65rem;
        cursor: pointer; white-space: nowrap;
        transition: color 0.1s, border-color 0.1s, background 0.1s;
    }
    .hide-btn:hover { color: #777; border-color: rgba(255,255,255,0.1); }
    .hide-btn.active { color: #aaa; background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.13); }

    .group { border-top: 1px solid rgba(255,255,255,0.04); padding-top: 0.6rem; }
    .group:first-of-type { border-top: none; padding-top: 0; }

    .group-header {
        display: flex; align-items: center; gap: 0.5rem;
        cursor: pointer; list-style: none; user-select: none;
    }
    .group-header::-webkit-details-marker { display: none; }
    .group-label { font-size: 0.8rem; color: #9a6020; font-weight: 600; }
    .group-count {
        font-size: 0.7rem; color: #555;
        background: rgba(255,255,255,0.04);
        border-radius: 10px; padding: 0.1rem 0.45rem;
    }

    .entry-list {
        list-style: none; margin: 0.5rem 0 0; padding: 0 0 0 0.5rem;
        display: flex; flex-direction: column; gap: 0.5rem;
        border-left: 1px solid rgba(255,255,255,0.05);
    }

    .entry {
        display: flex; align-items: center; gap: 0.5rem;
        min-width: 0;
    }

    .copy-btn {
        font-size: 0.65rem; color: #444;
        background: none; border: 1px solid rgba(255,255,255,0.07);
        border-radius: 4px; padding: 0.1rem 0.4rem;
        cursor: pointer; transition: color 0.1s, border-color 0.1s;
        flex-shrink: 0;
    }
    .copy-btn:hover { color: #888; border-color: rgba(255,255,255,0.15); }

    .hash-btn {
        font-size: 0.63rem; color: #333;
        font-family: monospace; letter-spacing: 0.04em;
        background: none; border: none; padding: 0;
        cursor: pointer; transition: color 0.1s;
        flex-shrink: 0;
    }
    .hash-btn:hover { color: #666; }

    .value-badge {
        font-size: 0.65rem; color: #555;
        background: rgba(255,255,255,0.04);
        border-radius: 4px; padding: 0.1rem 0.35rem;
        white-space: nowrap; flex-shrink: 0;
    }

    .fine-btn {
        font-size: 0.65rem; color: #333;
        background: none; border: 1px solid rgba(255,255,255,0.05);
        border-radius: 4px; padding: 0.1rem 0.35rem;
        cursor: pointer; transition: color 0.1s, border-color 0.1s;
        flex-shrink: 0; line-height: 1;
    }
    .fine-btn:hover         { color: #5a8a5a; border-color: rgba(80,180,80,0.2); }
    .fine-btn.marked        { color: #4a9a4a; border-color: rgba(80,180,80,0.25); }

    .fav-icon {
        width: 11px; height: 11px;
        flex-shrink: 0; display: block;
    }

    .entry-link {
        font-size: 0.8rem; color: #888; text-decoration: none;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        min-width: 0; flex-shrink: 1;
    }
    .entry-link:hover { color: #bbb; text-decoration: underline; }

    .expand-btn {
        font-size: 0.72rem; color: #484848;
        background: none; border: none; padding: 0.1rem 0;
        cursor: pointer; transition: color 0.1s;
    }
    .expand-btn:hover { color: #888; }
</style>
