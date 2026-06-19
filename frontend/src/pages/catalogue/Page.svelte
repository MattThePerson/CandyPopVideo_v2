<!-- pages/catalogue/Page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { routerState, navigate } from '$lib/router/router.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import CatalogueItem from './CatalogueItem.svelte';
    import type { CatalogueQuery, Catalogue, ItemInfo, CatalogueTab, SortMode } from './types';

    let catalogue      = $state<Catalogue | null>(null);
    let loading        = $state(true);
    let error          = $state<string | null>(null);
    let countThreshold = $state(5);

    const activeTab = $derived(
        (new URLSearchParams(routerState.search).get('type') as CatalogueTab) ?? 'actors'
    );
    const sortMode = $derived(
        (new URLSearchParams(routerState.search).get('sortby') as SortMode) ?? 'alphabetic'
    );

    const TAB_KEY: Record<CatalogueTab, keyof Catalogue> = {
        actors:      'actor_info',
        studios:     'studio_info',
        collections: 'collection_info',
        tags:        'tag_info',
    };

    const rawItems      = $derived(catalogue ? (catalogue[TAB_KEY[activeTab]] as ItemInfo[]) : []);
    const filteredItems = $derived(rawItems.filter(item => item.video_count >= countThreshold));

    const sortedItems = $derived.by((): ItemInfo[] => {
        const copy = [...filteredItems];
        if      (sortMode === 'count')        copy.sort((a, b) => b.video_count - a.video_count);
        else if (sortMode === 'newest-video') copy.sort((a, b) => b.newest_video.localeCompare(a.newest_video));
        else                                  copy.sort((a, b) => a.name.localeCompare(b.name));
        return copy;
    });

    const alphGroups = $derived.by((): { letter: string; items: ItemInfo[] }[] => {
        if (sortMode !== 'alphabetic') return [];
        const groups = new Map<string, ItemInfo[]>();
        for (const item of sortedItems) {
            const letter = item.name[0]?.toUpperCase() ?? '#';
            const arr = groups.get(letter) ?? [];
            arr.push(item);
            groups.set(letter, arr);
        }
        return [...groups.entries()].map(([letter, items]) => ({ letter, items }));
    });

    const presentLetters = $derived(alphGroups.map(g => g.letter));

    onMount(async () => {
        const query: CatalogueQuery = {
            query_type: 'actors', query_string: '', use_primary_actors: true,
            filter_actor: '', filter_studio: '', filter_collection: '', filter_tag: '',
        };
        try {
            const r = await fetch('/api/query/get/catalogue', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(query),
            });
            if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
            catalogue = await r.json() as Catalogue;
            console.debug("catalogue:", catalogue);
        } catch (e) {
            error = String(e);
        } finally {
            loading = false;
        }
    });

    function setTab(tab: CatalogueTab) {
        navigate(`/catalogue?type=${tab}&sortby=${sortMode}`);
        window.scrollTo(0, 0);
    }

    function setSortMode(mode: SortMode) {
        navigate(`/catalogue?type=${activeTab}&sortby=${mode}`);
        window.scrollTo(0, 0);
    }

    // Uses ID-based lookup to avoid bind:this complexity in keyed #each blocks.
    function scrollToLetter(letter: string) {
        const el = document.getElementById(`alph-group-${letter}`);
        if (!el) return;
        window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 80, behavior: 'smooth' });
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="page-wrapper">

    <!-- Left panel -->
    <aside class="left-panel">
        <div class="filter-section">
            <p class="filter-label">Min. videos</p>
            <div class="slider-row">
                <input type="range" min="1" max="50" bind:value={countThreshold} class="threshold-slider" />
                <span class="threshold-val">{countThreshold}</span>
            </div>
        </div>
    </aside>

    <!-- Main content -->
    <div class="content">

        <!-- Sticky header: tabs + sort + letter nav -->
        <div class="section-header">
            <div class="btn-group">
                {#each (['actors', 'studios', 'collections', 'tags'] as CatalogueTab[]) as tab}
                    <button class="tab-btn" class:active={activeTab === tab} onclick={() => setTab(tab)}>
                        {tab}
                    </button>
                {/each}
            </div>
            <div class="sort-row">
                <div class="btn-group">
                    {#each ([['alphabetic','alphabetic'],['count','by count'],['newest-video','newest']] as [SortMode,string][]) as [mode, label]}
                        <button class="sort-btn" class:active={sortMode === mode} onclick={() => setSortMode(mode)}>
                            {label}
                        </button>
                    {/each}
                </div>
                <span class="item-count-label">{filteredItems.length} {activeTab}</span>
            </div>
            {#if sortMode === 'alphabetic' && presentLetters.length > 0}
                <div class="letter-nav">
                    {#each presentLetters as letter}
                        <button class="letter-btn" onclick={() => scrollToLetter(letter)}>{letter}</button>
                    {/each}
                </div>
            {/if}
        </div>

        <!-- List -->
        <div class="list-area">
            {#if loading}
                <div class="center-pad"><Spinner /></div>
            {:else if error}
                <p class="error-text">{error}</p>
            {:else if sortMode === 'alphabetic'}
                {#each alphGroups as group (group.letter)}
                    <div class="alph-group" id="alph-group-{group.letter}">
                        <h2 class="group-letter">{group.letter}</h2>
                        <div class="group-items">
                            {#each group.items as item (item.name)}
                                <CatalogueItem {item} tab={activeTab} />
                            {/each}
                        </div>
                    </div>
                {/each}
            {:else}
                <div class="group-items flat">
                    {#each sortedItems as item (item.name)}
                        <CatalogueItem {item} tab={activeTab} />
                    {/each}
                </div>
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
    .page-wrapper {
        display: flex;
        width: 100%;
        min-height: 100vh;
    }

    /* Left panel */
    .left-panel {
        width: 16rem;
        flex-shrink: 0;
        border-right: 1px solid #1e1e1e;
        position: sticky;
        top: 0;
        align-self: flex-start;
        height: 100vh;
        padding: 1.5rem 1rem;
        overflow-y: auto;
    }

    .filter-section { display: flex; flex-direction: column; gap: 0.5rem; }

    .filter-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #555;
    }

    .slider-row { display: flex; align-items: center; gap: 0.6rem; }
    .threshold-slider { flex: 1; accent-color: #3e94b6; }
    .threshold-val { font-size: 0.85rem; color: #999; min-width: 1.5rem; }

    /* Main content */
    .content { display: flex; flex-direction: column; flex: 1; min-width: 0; }

    .section-header {
        position: sticky;
        top: 0;
        z-index: 10;
        background: #060A0A;
        box-shadow: 0 6px 18px 10px #060A0A;
        padding: 1rem 2rem 0.5rem;
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }

    .btn-group { display: flex; border-radius: 8px; overflow: hidden; }

    .tab-btn, .sort-btn {
        background: #333;
        color: #bbb;
        border: none;
        padding: 0.35rem 0.9rem;
        font-size: 0.8rem;
        cursor: pointer;
        text-transform: capitalize;
        transition: background 0.15s, color 0.15s;
    }
    .tab-btn:hover, .sort-btn:hover { background: #444; color: #eee; }
    .tab-btn.active, .sort-btn.active { background: #3e94b6; color: #fff; }

    .sort-row { display: flex; align-items: center; gap: 1rem; }

    .item-count-label { font-size: 0.75rem; color: #444; }

    .letter-nav {
        display: flex;
        flex-wrap: wrap;
        gap: 2px;
    }

    .letter-btn {
        background: #111;
        color: #888;
        border: none;
        width: 2rem;
        height: 2rem;
        font-size: 0.8rem;
        cursor: pointer;
        border-radius: 4px;
        transition: background 0.1s, color 0.1s;
    }
    .letter-btn:hover { background: #ff5500; color: #fff; }

    /* List area */
    .list-area { padding: 1rem 2rem 4rem; }

    .center-pad { display: flex; justify-content: center; padding: 4rem 0; }

    .error-text { color: #f87171; font-size: 0.9rem; padding: 2rem 0; }

    .alph-group { margin-bottom: 1.5rem; }

    .group-letter {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 0.3rem;
        width: 2rem;
    }

    .group-items { margin-left: 2.5rem; }
    .group-items.flat { margin-left: 0; }
</style>
