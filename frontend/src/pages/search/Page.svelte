<!-- pages/search/Page.svelte -->
<script lang="ts">
    import { routerState, navigate } from '$lib/router/router.svelte';
    import { settings } from '$lib/stores/settings.svelte';
    import SearchPanel from '$lib/components/SearchPanel.svelte';
    import VideoCard from '$lib/components/VideoCard.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import PageNav from './PageNav.svelte';
    import type { VideoData } from '$lib/types/video';
    import type { SearchQuery, SearchResponse } from './types';

    let response    = $state<SearchResponse>();
    let results     = $state<VideoData[]>([]);
    let loading     = $state(false);
    let hasSearched = $state(false);
    let error       = $state<string | null>(null);

    const currentPage = $derived(
        parseInt(new URLSearchParams(routerState.search).get('page') ?? '1', 10)
    );

    const totalPages = $derived(
        response ? Math.ceil(response.videos_filtered_count / settings.resultsPerPage) : 0
    );

    function queryFromParams(search: string): SearchQuery {
        const p = new URLSearchParams(search);
        const split = (key: string): string[] => {
            const v = p.get(key);
            return v ? v.split(',').map(s => s.trim()).filter(Boolean) : [];
        };
        const page    = parseInt(p.get('page') ?? '1', 10);
        const perPage = settings.resultsPerPage;
        return {
            search_string:      p.get('q')          ?? '',
            actor:              p.get('actor')       ?? '',
            studio:             p.get('studio')      ?? '',
            collection:         p.get('collection')  ?? '',
            include_terms:      split('include'),
            exclude_terms:      split('exclude'),
            tags:               split('tags'),
            date_added_from:    '',
            date_added_to:      '',
            date_released_from: '',
            date_released_to:   '',
            only_favourites:    p.get('favourites') === '1' ? 'true' : '',
            sortby:             p.get('sortby')      ?? 'date_added_desc',
            limit:              perPage,
            startfrom:          (page - 1) * perPage,
        };
    }

    function goToPage(n: number) {
        const p = new URLSearchParams(routerState.search);
        if (n <= 1) { p.delete('page'); } else { p.set('page', String(n)); }
        const qs = p.toString();
        navigate('/search' + (qs ? '?' + qs : ''));
    }

    $effect(() => {
        const p          = new URLSearchParams(routerState.search);
        const q          = p.get('q');
        const actor      = p.get('actor');
        const studio     = p.get('studio');
        const collection = p.get('collection');
        const include    = p.get('include');
        const exclude    = p.get('exclude');
        const tags       = p.get('tags');
        const favourites = p.get('favourites');
        const parts: string[] = [];
        if (q)                   parts.push(`"${q}"`);
        if (actor)               parts.push(actor);
        if (studio)              parts.push(studio);
        if (collection)          parts.push(collection);
        if (include)             parts.push(...include.split(',').map(t => t.trim()).filter(Boolean));
        if (exclude)             parts.push(`(exclude) ${exclude.split(',').map(t => t.trim()).filter(Boolean).join(', ')}`);
        if (tags)                parts.push(...tags.split(',').map(t => `#${t.trim()}`));
        if (favourites === '1')  parts.push('favs');
        document.title = parts.length ? `${parts.join(' - ')} | Search | CandyPop` : 'Search | CandyPop';
    });

    $effect(() => {
        if (!routerState.search) return;

        const q = queryFromParams(routerState.search);
        const controller = new AbortController();

        console.debug('search-query:', q);

        loading     = true;
        hasSearched = true;
        error       = null;

        fetch('/api/query/search-videos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(q),
            signal: controller.signal,
        })
            .then(r => {
                if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
                return r.json() as Promise<SearchResponse>;
            })
            .then(data => {
                console.log("response: ", data);
                response = data;
                results = response.search_results;
            })
            .catch(e => {
                if ((e as Error).name !== 'AbortError') error = String(e);
            })
            .finally(() => { loading = false; });

        return () => controller.abort();
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="search-page">

    <SearchPanel />

    <div class="results-section">
        {#if loading}
            <div class="results-center">
                <Spinner />
            </div>
        {:else if hasSearched}
            {#if error}
                <p class="results-error">{error}</p>
            {:else}
                <p class="results-count">
                    {response?.videos_filtered_count} result(s)
                    {#if totalPages > 1}· page {currentPage} of {totalPages}{/if}
                    · {response?.time_taken}s
                </p>
                {#if results.length > 0}
                    <div class="card-grid">
                        {#each results as v (v.hash)}
                            <VideoCard video={v} />
                        {/each}
                    </div>
                    {#if totalPages > 1}
                        <PageNav page={currentPage} {totalPages} onNavigate={goToPage} />
                    {/if}
                {/if}
            {/if}
        {/if}
    </div>

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .search-page {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        padding-bottom: 4rem;
    }

    .results-section {
        width: 100%;
        max-width: 120rem;
        padding: 0.5rem 4rem 0;
    }

    .results-center {
        display: flex;
        justify-content: center;
        padding: 4rem 0;
    }

    .results-error {
        color: #f87171;
        font-size: 0.9rem;
        padding: 2rem 0;
        text-align: center;
    }

    .results-count {
        color: #444;
        font-size: 0.8rem;
        margin-bottom: 0.75rem;
        letter-spacing: 0.03em;
    }

    .card-grid {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 3px;
    }
</style>
