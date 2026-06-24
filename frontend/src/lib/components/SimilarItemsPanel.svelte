<script lang="ts">
    import { navigate } from '$lib/router/router.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    // @ts-ignore — no type declarations for this package
    import { detect as detectGender } from 'gender-detection';

    /* Props */
    let { type, target, visible }: {
        type: 'actors' | 'studios';
        target: string;
        visible: boolean;
    } = $props();

    let loading           = $state(false);
    let items             = $state<{ name: string; rawSim: number; penalty: number; sim: number }[]>([]);
    let counts            = $state<Record<string, number>>({});
    let error             = $state<string | null>(null);
    let filterMale        = $state(false);
    let filterNumeric     = $state(false);
    let minVideosStr      = $state('');
    let lastFetchedTarget = $state('');

    const minVideos = $derived(parseInt(minVideosStr) || 0);

    // Names come in lowercase from the DB; capitalize for dictionary lookup
    function isMale(name: string): boolean {
        const capitalized = name.replace(/\b\w/g, c => c.toUpperCase());
        return detectGender(capitalized) === 'male';
    }

    // Each shared word between target and candidate name halves the score
    function nameWordPenalty(t: string, name: string): number {
        const targetWords = new Set(t.toLowerCase().split(/\s+/).filter(Boolean));
        const shared = name.toLowerCase().split(/\s+/).filter(w => w && targetWords.has(w)).length;
        return Math.pow(0.5, shared);
    }

    const visibleItems = $derived(items.filter(item => {
        if (filterMale    && isMale(item.name))                           return false;
        if (filterNumeric && /\d/.test(item.name))                        return false;
        if (minVideos > 0 && (counts[item.name] ?? Infinity) < minVideos) return false;
        return true;
    }));

    // Lazy fetch: only fires when first made visible, or when target changes
    $effect(() => {
        const t = target;
        const v = visible;
        if (!v || t === lastFetchedTarget) return;
        lastFetchedTarget = t;
        doFetch(t);
    });

    async function doFetch(t: string) {
        loading = true;
        items   = [];
        counts  = {};
        error   = null;
        const endpoint = type === 'actors'
            ? `/api/query/get/similar-actors/${encodeURIComponent(t)}`
            : `/api/query/get/similar-studios/${encodeURIComponent(t)}`;
        try {
            const res = await fetch(endpoint);
            if (!res.ok) { error = `Request failed (${res.status})`; return; }
            const data = await res.json();
            const names: string[]                = data.NamesList ?? [];
            const scores: Record<string, number> = data.SimScores ?? {};
            // skip index 0 — always the queried name itself
            items = names.slice(1).map(name => {
                const raw     = scores[name] ?? 0;
                const penalty = type === 'actors' ? nameWordPenalty(t, name) : 1;
                return { name, rawSim: raw, penalty, sim: raw * penalty };
            });

            // fire-and-forget: fetch counts then reweight + re-sort by (1 + ln(min(n,100)))
            const itemType = type === 'actors' ? 'actor' : 'studio';
            fetch('/api/query/get/item-counts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: itemType, names: names.slice(1) }),
            }).then(r => r.ok ? r.json() : null)
              .then(d => {
                  if (!d?.counts) return;
                  counts = d.counts;
                  items = items
                      .map(item => {
                          const n = counts[item.name];
                          if (!n) return item;
                          return { ...item, sim: item.rawSim * item.penalty * (1 + Math.log(Math.min(n, 100))) };
                      })
                      .sort((a, b) => b.sim - a.sim);
              })
              .catch(() => {});
        } catch (e) {
            error = String(e);
        } finally {
            loading = false;
        }
    }

    function chipHref(name: string): string {
        const key = type === 'actors' ? 'actor' : 'studio';
        return `/search?${key}=${encodeURIComponent(name)}`;
    }

    function navChip(e: MouseEvent, name: string) {
        e.preventDefault();
        navigate(chipHref(name));
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="expansion" style:display={visible ? '' : 'none'}>
    <div class="expansion-header">
        <span class="expansion-title">
            similar {type} to <em>{target}</em>
        </span>
        <div class="expansion-actions">
            {#if type === 'actors'}
                <button
                    class="filter-btn"
                    class:active={filterMale}
                    onclick={() => filterMale = !filterMale}
                    title="Hide male-sounding names"
                >filter male</button>
            {/if}
            <button
                class="filter-btn"
                class:active={filterNumeric}
                onclick={() => filterNumeric = !filterNumeric}
                title="Hide names containing numbers"
            >filter numeric</button>
            <input
                class="min-videos-input"
                type="number"
                min="0"
                placeholder="? videos"
                bind:value={minVideosStr}
            />
        </div>
    </div>

    <div class="item-list">
        {#if loading}
            <div class="status"><Spinner size={18} /></div>
        {:else if error}
            <div class="status error">{error}</div>
        {:else if visibleItems.length === 0}
            <div class="status muted">no results</div>
        {:else}
            {#each visibleItems as item}
                <a
                    class="item-chip"
                    href={chipHref(item.name)}
                    onclick={(e) => navChip(e, item.name)}
                >
                    <span class="chip-top">
                        <span class="chip-name">{item.name}</span>
                        <span class="chip-score">{(item.sim * 100).toFixed(0)}%</span>
                    </span>
                    <span class="chip-count">
                        {counts[item.name] !== undefined ? `${counts[item.name]} videos` : '? videos'}
                    </span>
                </a>
            {/each}
        {/if}
    </div>
</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .expansion {
        border-top: 1px solid #bbb2;
        padding: 0.4rem 0.5rem 0.5rem;
    }

    .expansion-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.4rem;
        gap: 0.5rem;
    }

    .expansion-title {
        font-size: 0.82rem;
        color: #888;
        font-family: 'Inter', sans-serif;
    }
    .expansion-title em {
        font-style: normal;
        color: #bbb;
    }

    .expansion-actions {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        flex-shrink: 0;
    }

    .filter-btn {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        background: #111;
        color: #888;
        border: 1px solid #333;
        border-radius: 0.25rem;
        padding: 1px 6px;
        cursor: pointer;
    }
    .filter-btn:hover { color: #bbb; border-color: #555; }
    .filter-btn.active { color: #D79C29; border-color: #D79C29; }

    .item-list {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 0.5rem;
        overflow-x: auto;
        padding-bottom: 0.25rem;
        min-height: 2.5rem;
    }
    .item-list::-webkit-scrollbar       { height: 4px; }
    .item-list::-webkit-scrollbar-track { background: #111; }
    .item-list::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }

    .status {
        display: flex;
        align-items: center;
        padding: 0 0.25rem;
    }
    .status.muted { font-size: 0.85rem; color: #555; }
    .status.error { font-size: 0.85rem; color: #a04040; }

    .item-chip {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.1rem;
        background: #0d0d0d;
        border: 1px solid #2a2a2a;
        border-radius: 1rem;
        padding: 5px 0.75rem;
        text-decoration: none;
        white-space: nowrap;
        flex-shrink: 0;
        transition: border-color 0.1s;
    }
    .item-chip:hover { border-color: #555; }

    .chip-top {
        display: flex;
        align-items: baseline;
        gap: 0.3rem;
    }

    .chip-name {
        font-size: 0.85rem;
        color: #ccc;
    }

    .chip-score {
        font-size: 0.75rem;
        color: #555;
    }

    .chip-count {
        font-size: 0.72rem;
        color: #555;
    }

    .min-videos-input {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        background: #111;
        color: #888;
        border: 1px solid #333;
        border-radius: 0.25rem;
        padding: 1px 6px;
        width: 6rem;
        outline: none;
    }
    .min-videos-input::placeholder { color: #444; }
    .min-videos-input:focus { border-color: #555; color: #bbb; }
    /* hide browser spinner arrows */
    .min-videos-input::-webkit-outer-spin-button,
    .min-videos-input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    .min-videos-input[type=number] { -moz-appearance: textfield; }
</style>
