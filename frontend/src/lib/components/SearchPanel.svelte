<script lang="ts">
    import { onMount } from 'svelte';
    import { navigate } from '$lib/router/router.svelte';
    import { settings, type ResultsPerPage } from '$lib/stores/settings.svelte';

    const PER_PAGE_OPTIONS: ResultsPerPage[] = [4, 8, 16, 24, 36];

    let searchString   = $state('');
    let actor          = $state('');
    let studio         = $state('');
    let collection     = $state('');
    let includeTerms   = $state('');
    let excludeTerms   = $state('');
    let tags           = $state('');
    let onlyFavourites = $state(false);
    let sortby         = $state('date_added_desc');

    const SORT_OPTIONS = [
        { value: 'date_added_desc',      label: 'date added ↓' },
        { value: 'date_added_asc',       label: 'date added ↑' },
        { value: 'date_released_desc',   label: 'date released ↓' },
        { value: 'date_released_asc',    label: 'date released ↑' },
        { value: 'title_asc',            label: 'title A–Z' },
        { value: 'title_desc',           label: 'title Z–A' },
        { value: 'duration_desc',        label: 'longest first' },
        { value: 'duration_asc',         label: 'shortest first' },
        { value: 'viewtime_desc',        label: 'most watched' },
        { value: 'last_viewed_desc',     label: 'recently watched' },
        { value: 'favourited_date_desc', label: 'recently favourited' },
        { value: 'random',               label: 'random' },
    ];

    function hydrateFromUrl() {
        const p      = new URLSearchParams(window.location.search);
        searchString   = p.get('q')          ?? '';
        actor          = p.get('actor')       ?? '';
        studio         = p.get('studio')      ?? '';
        collection     = p.get('collection')  ?? '';
        includeTerms   = p.get('include')     ?? '';
        excludeTerms   = p.get('exclude')     ?? '';
        tags           = p.get('tags')        ?? '';
        onlyFavourites = p.get('favourites') === '1';
        const rawSortby = p.get('sortby') ?? 'date_added_desc';
        sortby         = rawSortby.startsWith('random') ? 'random' : rawSortby;
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
        if (sortby && sortby !== 'date_added_desc') {
            const sortbyParam = sortby === 'random'
                ? `random-${Math.floor(Math.random() * 1_000_000)}`
                : sortby;
            p.set('sortby', sortbyParam);
        }
        const qs = p.toString();
        navigate('/search' + (qs ? '?' + qs : ''));
    }

    let searchInputEl:  HTMLInputElement;
    let includeInputEl: HTMLInputElement;

    /* Enter in any panel field applies the search and drops focus. */
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

    /* Returns true if the currently focused element is any kind of text input. */
    function activeIsInput(): boolean {
        const el = document.activeElement;
        if (!el) return false;
        const tag = el.tagName.toLowerCase();
        return tag === 'input' || tag === 'textarea' || tag === 'select' || (el as HTMLElement).isContentEditable;
    }

    /* Global shortcuts: Enter → focus include field; / → focus search bar. */
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
        hydrateFromUrl();
        window.addEventListener('popstate', hydrateFromUrl);
        window.addEventListener('keydown', onGlobalKeydown);
        return () => {
            window.removeEventListener('popstate', hydrateFromUrl);
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
            <select class="sort-select" bind:value={sortby} onchange={apply}>
                {#each SORT_OPTIONS as opt}
                    <option value={opt.value}>{opt.label}</option>
                {/each}
            </select>
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
            <button class="tool-btn disabled" disabled>similar performers</button>
            <button class="tool-btn disabled" disabled>similar studios</button>
        </div>
        <div class="bottom-right">
            <button class="tool-btn" onclick={randomVideo}>random video</button>
        </div>
    </div>

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
</style>
