<script lang="ts">
    import { onMount } from 'svelte';
    import { navigate, routerState } from '$lib/router/router.svelte';
    import { settings, type ResultsPerPage } from '$lib/stores/settings.svelte';
    import SimilarItemsPanel from './SimilarItemsPanel.svelte';

    const PER_PAGE_OPTIONS: ResultsPerPage[] = [4, 8, 16, 24, 36];

    let searchString   = $state('');
    let actor          = $state('');
    let studio         = $state('');
    let collection     = $state('');
    let includeTerms   = $state('');
    let excludeTerms   = $state('');
    let tags           = $state('');
    let onlyFavourites = $state(false);
    let sortField      = $state('date_downloaded');
    let sortDir        = $state<'asc' | 'desc'>('desc');
    let sortDropOpen   = $state(false);

    const SORT_OPTIONS = [
        { field: 'date_downloaded', label: 'date downloaded',  defaultDir: 'desc' as const, alphabetic: false, group: 0 },
        { field: 'date_added',      label: 'date added',      defaultDir: 'desc' as const, alphabetic: false, group: 0 },
        { field: 'date_released',   label: 'date released',   defaultDir: 'desc' as const, alphabetic: false, group: 0 },
        { field: 'title',           label: 'title',           defaultDir: 'asc'  as const, alphabetic: true,  group: 0 },
        { field: 'filename',        label: 'filename',        defaultDir: 'asc'  as const, alphabetic: true,  group: 0 },
        { field: 'path',            label: 'filepath',        defaultDir: 'asc'  as const, alphabetic: true,  group: 0 },
        { field: 'duration',        label: 'duration',        defaultDir: 'desc' as const, alphabetic: false, group: 0 },
        { field: 'bitrate',         label: 'bitrate',         defaultDir: 'desc' as const, alphabetic: false, group: 0 },
        { field: 'views',           label: 'views',           defaultDir: 'desc' as const, alphabetic: false, group: 1 },
        { field: 'likes',           label: 'likes',           defaultDir: 'desc' as const, alphabetic: false, group: 1 },
        { field: 'popularity',      label: 'popularity',      defaultDir: 'desc' as const, alphabetic: false, group: 2 },
        { field: 'viewtime',        label: 'viewtime',        defaultDir: 'desc' as const, alphabetic: false, group: 2 },
        { field: 'last_viewed',     label: 'last watched',    defaultDir: 'desc' as const, alphabetic: false, group: 2 },
        { field: 'favourited_date', label: 'favourited time', defaultDir: 'desc' as const, alphabetic: false, group: 2 },
        { field: 'random',          label: 'random',          defaultDir: null,             alphabetic: false, group: 3 },
    ];

    const GROUP_HEADERS: Record<number, { label: string; color: string } | null> = {
        0: null,
        1: { label: 'platform data',     color: '#D79C29' },
        2: { label: 'user interactions', color: '#3EA7A7' },
        3: null,
    };

    function hydrateFromUrl() {
        const p = new URLSearchParams(window.location.search);
        searchString   = p.get('q')          ?? '';
        actor          = p.get('actor')       ?? '';
        studio         = p.get('studio')      ?? '';
        collection     = p.get('collection')  ?? '';
        includeTerms   = p.get('include')     ?? '';
        excludeTerms   = p.get('exclude')     ?? '';
        tags           = p.get('tags')        ?? '';
        onlyFavourites = p.get('favourites') === '1';
        const rawSortby = p.get('sortby') ?? 'date_downloaded_desc';
        if (rawSortby.startsWith('random')) {
            sortField = 'random';
        } else {
            const cut = rawSortby.lastIndexOf('_');
            sortField = rawSortby.slice(0, cut);
            sortDir   = rawSortby.slice(cut + 1) as 'asc' | 'desc';
        }
    }

    function buildSortParam(): string {
        if (sortField === 'random') return `random-${Math.floor(Math.random() * 1_000_000)}`;
        return `${sortField}_${sortDir}`;
    }

    function apply() {
        const p = new URLSearchParams();
        if (searchString)   p.set('q',          searchString);
        if (actor)          p.set('actor',       actor);
        if (studio)         p.set('studio',      studio);
        if (collection)     p.set('collection',  collection);
        if (includeTerms)   p.set('include',     includeTerms);
        if (excludeTerms)   p.set('exclude',     excludeTerms);
        if (tags)           p.set('tags',        tags);
        if (onlyFavourites) p.set('favourites',  '1');
        const sortParam = buildSortParam();
        if (sortParam !== 'date_downloaded_desc') p.set('sortby', sortParam);
        const qs = p.toString();
        navigate('/search' + (qs ? '?' + qs : ''));
    }

    function clickSortLabel(field: string, alphabetic: boolean) {
        if (sortField === field) {
            sortDir = sortDir === 'asc' ? 'desc' : 'asc';
        } else {
            sortField = field;
            sortDir   = alphabetic ? 'asc' : 'desc';
        }
        sortDropOpen = false;
        apply();
    }

    function clickSortDir(field: string, dir: 'asc' | 'desc') {
        sortField    = field;
        sortDir      = dir;
        sortDropOpen = false;
        apply();
    }

    const currentSortLabel = $derived.by(() => {
        if (sortField === 'random') return 'random';
        const opt = SORT_OPTIONS.find(o => o.field === sortField);
        if (!opt) return sortField;
        return opt.alphabetic
            ? `${opt.label} ${sortDir === 'asc' ? 'A→Z' : 'Z→A'}`
            : `${opt.label} ${sortDir === 'asc' ? '↑' : '↓'}`;
    });

    let searchInputEl:  HTMLInputElement;
    let includeInputEl: HTMLInputElement;

    function onFieldKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            e.stopPropagation();
            apply();
            (e.currentTarget as HTMLElement).blur();
        }
    }

    function randomVideo() {
        const seed = Math.floor(Math.random() * 1_000_000);
        navigate(`/search?sortby=random-${seed}`);
    }

    let expansionType = $state<'actors' | 'studios' | null>(null);

    // Committed (URL-applied) values — panels only re-fetch when these change, not on every keystroke
    const committedActor  = $derived(new URLSearchParams(routerState.search).get('actor')  ?? '');
    const committedStudio = $derived(new URLSearchParams(routerState.search).get('studio') ?? '');
    const singleActor     = $derived(committedActor  !== '' && !committedActor.includes(','));
    const singleStudio    = $derived(committedStudio !== '');

    // Re-hydrate inputs on any URL change (handles navigate() pushState and browser popstate)
    $effect(() => {
        routerState.search;
        hydrateFromUrl();
    });

    // Close expansion when its committed field is cleared
    $effect(() => {
        if (expansionType === 'actors'  && !singleActor)  expansionType = null;
        if (expansionType === 'studios' && !singleStudio) expansionType = null;
    });

    function toggleExpansion(type: 'actors' | 'studios') {
        expansionType = expansionType === type ? null : type;
    }

    function activeIsInput(): boolean {
        const el = document.activeElement;
        if (!el) return false;
        const tag = el.tagName.toLowerCase();
        return tag === 'input' || tag === 'textarea' || tag === 'select' || (el as HTMLElement).isContentEditable;
    }

    function onGlobalKeydown(e: KeyboardEvent) {
        if (activeIsInput()) return;
        if (e.key === 'Enter') {
            e.preventDefault();
            includeInputEl?.focus();
        } else if (e.key === '/') {
            e.preventDefault();
            searchInputEl?.focus();
        }
    }

    onMount(() => {
        window.addEventListener('keydown', onGlobalKeydown);
        return () => {
            window.removeEventListener('keydown', onGlobalKeydown);
        };
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="panel">

    <!-- TOP BAR -->
    <div class="top-bar">
        <div class="top-left">
            <button class="apply-btn" onclick={apply}>apply</button>
            <input
                class="search-input"
                type="text"
                placeholder="search query..."
                bind:value={searchString}
                bind:this={searchInputEl}
                onkeydown={onFieldKeydown}
            />
        </div>
        <div class="top-right">
            <span class="sort-label">sort by</span>
            <div class="sort-control">
                <button class="sort-trigger" onclick={() => sortDropOpen = !sortDropOpen}>
                    {currentSortLabel} <span class="sort-caret">▾</span>
                </button>
                {#if sortDropOpen}
                    <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
                    <div class="sort-backdrop" onclick={() => sortDropOpen = false}></div>
                    <div class="sort-dropdown">
                        {#each SORT_OPTIONS as opt, i}
                            {#if i > 0 && opt.group !== SORT_OPTIONS[i - 1].group}
                                {#if GROUP_HEADERS[opt.group]}
                                    <div class="sort-group-header" style="color: {GROUP_HEADERS[opt.group]!.color}">
                                        <span class="sort-group-label">{GROUP_HEADERS[opt.group]!.label}</span>
                                    </div>
                                {:else}
                                    <hr class="sort-sep" />
                                {/if}
                            {/if}
                            <div class="sort-row" class:active={sortField === opt.field}>
                                <button class="sort-row-label" onclick={() => clickSortLabel(opt.field, opt.alphabetic)}>
                                    {opt.label}
                                </button>
                                {#if opt.field !== 'random'}
                                    <div class="dir-group">
                                        {#if opt.alphabetic}
                                            <button class="dir-btn" class:dir-active={sortField === opt.field && sortDir === 'asc'} onclick={() => clickSortDir(opt.field, 'asc')}>A→Z</button>
                                            <button class="dir-btn" class:dir-active={sortField === opt.field && sortDir === 'desc'} onclick={() => clickSortDir(opt.field, 'desc')}>Z→A</button>
                                        {:else}
                                            <button class="dir-btn" class:dir-active={sortField === opt.field && sortDir === 'asc'} onclick={() => clickSortDir(opt.field, 'asc')}>↑</button>
                                            <button class="dir-btn" class:dir-active={sortField === opt.field && sortDir === 'desc'} onclick={() => clickSortDir(opt.field, 'desc')}>↓</button>
                                        {/if}
                                    </div>
                                {/if}
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
            <span class="sort-label">per page</span>
            <select class="sort-select" bind:value={settings.resultsPerPage} onchange={apply}>
                {#each PER_PAGE_OPTIONS as n}
                    <option value={n}>{n}</option>
                {/each}
            </select>
        </div>
    </div>

    <!-- BODY -->
    <div class="body">

        <div class="tag-filters">
            <h3 class="section-label">tag filters</h3>
            <div class="filter-columns">
                <div class="filter-col">
                    <div class="field">
                        <label for="sp-actors">actors</label>
                        <input id="sp-actors" type="text" bind:value={actor} onkeydown={onFieldKeydown} />
                    </div>
                    <div class="field">
                        <label for="sp-studio">studio</label>
                        <input id="sp-studio" type="text" bind:value={studio} onkeydown={onFieldKeydown} />
                    </div>
                    <div class="field">
                        <label for="sp-collection">collection</label>
                        <input id="sp-collection" type="text" bind:value={collection} onkeydown={onFieldKeydown} />
                    </div>
                </div>
                <div class="filter-col">
                    <div class="field">
                        <label for="sp-include">include</label>
                        <input id="sp-include" type="text" bind:value={includeTerms} bind:this={includeInputEl} onkeydown={onFieldKeydown} placeholder="comma-separated" />
                    </div>
                    <div class="field">
                        <label for="sp-exclude">exclude</label>
                        <input id="sp-exclude" type="text" bind:value={excludeTerms} onkeydown={onFieldKeydown} placeholder="comma-separated" />
                    </div>
                    <div class="field">
                        <label for="sp-tags">tags</label>
                        <input id="sp-tags" type="text" bind:value={tags} onkeydown={onFieldKeydown} placeholder="comma-separated" />
                    </div>
                </div>
            </div>
        </div>

        <div class="extra-filters">
            <h3 class="section-label">filters</h3>
            <div class="extra-filters-body">
                <label class="fav-toggle">
                    <input type="checkbox" bind:checked={onlyFavourites} onchange={apply} />
                    <span>favourites only</span>
                </label>
            </div>
        </div>

    </div>

    <!-- BOTTOM BAR -->
    <div class="bottom-bar">
        <div class="bottom-left">
            <button class="tool-btn">date added dist</button>
            <button class="tool-btn">date released dist</button>
            <button class="tool-btn">word cloud</button>
            <button
                class="tool-btn"
                class:disabled={!singleActor}
                class:active={expansionType === 'actors'}
                disabled={!singleActor}
                onclick={() => toggleExpansion('actors')}
            >similar actors</button>
            <button
                class="tool-btn"
                class:disabled={!singleStudio}
                class:active={expansionType === 'studios'}
                disabled={!singleStudio}
                onclick={() => toggleExpansion('studios')}
            >similar studios</button>
        </div>
        <div class="bottom-right">
            <button class="tool-btn" onclick={randomVideo}>random video</button>
        </div>
    </div>

    {#if singleActor}
        <SimilarItemsPanel type="actors" target={committedActor} visible={expansionType === 'actors'} />
    {/if}
    {#if singleStudio}
        <SimilarItemsPanel type="studios" target={committedStudio} visible={expansionType === 'studios'} />
    {/if}

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .panel {
        display: flex;
        flex-direction: column;
        width: 80rem;
        max-width: 90vw;
        background: black;
        border: 1.9px solid #bbb4;
        border-radius: 0.8rem;
        margin: 1rem 2rem;
        padding: 2px 0.5rem;
        box-shadow: 0 0 7px #444;
    }

    /* ── Top bar ─────────────────────────────────────────────────────────────── */

    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px;
        border-bottom: 2px solid #bbb3;
        gap: 0.5rem;
    }

    .top-left {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex: 1;
        min-width: 0;
    }

    .top-right {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-shrink: 0;
    }

    .apply-btn {
        font-family: 'Jaro', sans-serif;
        font-size: 1.2rem;
        background: #752868;
        color: white;
        border: 1px solid #7773;
        border-radius: 5px;
        padding: 0 1.2rem 2px;
        cursor: pointer;
        flex-shrink: 0;
    }
    .apply-btn:hover  { opacity: 0.85; }
    .apply-btn:active { opacity: 1; }
    .apply-btn:focus  { outline: 2px solid #ff4ba2; }

    .search-input {
        font-size: 1rem;
        background: #7773;
        color: #ddd;
        padding: 4px 0.8rem;
        border: none;
        outline: none;
        border-radius: 5px;
        width: 100%;
        min-width: 0;
    }
    .search-input::placeholder { color: #555; }
    .search-input:focus        { background: #7775; }

    .sort-label {
        color: #888;
        font-size: 0.9rem;
        white-space: nowrap;
    }

    /* ── Sort control ─────────────────────────────────────────────────────────── */

    .sort-control {
        position: relative;
    }

    .sort-trigger {
        background: #111;
        color: #ccc;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 3px 8px;
        font-size: 0.9rem;
        cursor: pointer;
        white-space: nowrap;
        min-width: 11rem;
        text-align: left;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.4rem;
    }
    .sort-trigger:hover { border-color: #666; }
    .sort-trigger:focus { outline: 1px solid #666; }

    .sort-caret {
        color: #555;
        font-size: 0.75rem;
    }

    .sort-backdrop {
        position: fixed;
        inset: 0;
        z-index: 99;
    }

    .sort-dropdown {
        position: absolute;
        top: calc(100% + 4px);
        right: 0;
        background: #0d0d0d;
        border: 1px solid #3a3a3a;
        border-radius: 6px;
        padding: 4px;
        z-index: 100;
        min-width: 14rem;
        box-shadow: 0 6px 18px #0009;
    }

    .sort-sep {
        border: none;
        border-top: 1px solid #222;
        margin: 3px 4px;
    }

    .sort-row {
        display: flex;
        align-items: stretch;
        border-radius: 4px;
        padding: 0 0 0 2px;
        gap: 2px;
        min-height: 1.7rem;
    }
    .sort-row:hover      { background: #161616; }
    .sort-row.active     { background: #1c1c1c; }

    .sort-row-label {
        flex: 1;
        text-align: left;
        background: none;
        border: none;
        color: #999;
        font-size: 0.88rem;
        padding: 4px 6px;
        cursor: pointer;
        display: flex;
        align-items: center;
        border-radius: 3px;
        white-space: nowrap;
    }
    .sort-row-label:hover  { color: #eee; }
    .sort-row.active .sort-row-label { color: #ddd; }

    .dir-group {
        display: flex;
        align-self: stretch;
    }

    .dir-btn {
        background: none;
        border: none;
        border-left: 1px solid #1e1e1e;
        color: #444;
        font-size: 0.8rem;
        width: 3rem;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        white-space: nowrap;
    }
    .dir-btn:first-child { border-left: none; }
    .dir-btn:hover    { color: #aaa; background: #1a1a1a; }
    .dir-btn.dir-active {
        color: #ddd;
        background: #252525;
    }

    .sort-group-header {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 8px 3px;
    }
    .sort-group-header::before,
    .sort-group-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: currentColor;
        opacity: 0.25;
    }
    .sort-group-label {
        font-size: 0.7rem;
        font-family: 'Inter', sans-serif;
        opacity: 0.6;
        letter-spacing: 0.04em;
        white-space: nowrap;
    }

    /* ── Per-page select ─────────────────────────────────────────────────────── */

    .sort-select {
        background: #111;
        color: #ccc;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 3px 6px;
        font-size: 0.9rem;
        cursor: pointer;
    }
    .sort-select:focus { outline: 1px solid #666; }

    /* ── Body ────────────────────────────────────────────────────────────────── */

    .body {
        display: flex;
        gap: 2rem;
        padding: 0.5rem;
        flex-wrap: wrap;
    }

    .section-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        width: 4rem;
        text-align: right;
        color: #666;
        margin: 0.5rem 0.8rem 0 0;
        flex-shrink: 0;
    }

    /* Tag filters */

    .tag-filters {
        display: flex;
        align-items: flex-start;
    }

    .filter-columns {
        display: flex;
        flex-wrap: wrap;
        gap: 0.25rem 1.5rem;
    }

    .filter-col {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .field {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        height: 1.6rem;
    }

    .field label {
        font-size: 0.85rem;
        color: #777;
        width: 5.5rem;
        text-align: right;
        white-space: nowrap;
        flex-shrink: 0;
    }

    .field input[type="text"] {
        width: 14rem;
        background: #ffffff0f;
        color: #ddd;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 2px 0.5rem;
        font-size: 0.9rem;
        outline: none;
    }
    .field input[type="text"]::placeholder { color: #3d3d3d; }
    .field input[type="text"]:focus {
        border-color: #555;
        background: #ffffff18;
    }

    /* Extra filters */

    .extra-filters {
        display: flex;
        align-items: flex-start;
    }

    .extra-filters-body {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        padding-top: 0.5rem;
    }

    .fav-toggle {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        cursor: pointer;
        font-size: 0.85rem;
        color: #777;
        user-select: none;
    }
    .fav-toggle:hover { color: #bbb; }
    .fav-toggle input[type="checkbox"] {
        cursor: pointer;
        accent-color: #752868;
    }

    /* ── Bottom bar ──────────────────────────────────────────────────────────── */

    .bottom-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #bbb2;
        margin-top: 2px;
        padding: 3px 0.3rem;
        flex-wrap: wrap;
        gap: 3px;
    }

    .bottom-left,
    .bottom-right {
        display: flex;
        gap: 3px;
        flex-wrap: wrap;
    }

    .tool-btn {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        background: #111;
        color: #ccc;
        border: 1px solid #aaa8;
        border-radius: 0.3rem;
        padding: 1px 7px;
        cursor: pointer;
        white-space: nowrap;
    }
    .tool-btn:not(.disabled):hover  { opacity: 0.8; }
    .tool-btn:not(.disabled):active { border-color: white; }
    .tool-btn.disabled {
        color: #555;
        cursor: default;
        border-color: #333;
    }
    .tool-btn.active {
        color: #D79C29;
        border-color: #D79C29;
    }
</style>
