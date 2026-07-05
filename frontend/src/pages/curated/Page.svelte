<!-- pages/curated/Page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { routerState, navigate } from '$lib/router/router.svelte';
    import { settings } from '$lib/stores/settings.svelte';
    import VideoCard from '$lib/components/VideoCard.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import PageNav from '../search/PageNav.svelte';
    import type { SearchQuery, SearchResponse } from '../search/types';
    import type { CuratedCollectionMeta, CuratedSiteMeta, CuratedQuery } from './types';

    let searchCollections = $state<CuratedCollectionMeta[]>([]);
    let siteCollections   = $state<CuratedSiteMeta[]>([]);
    let loading           = $state(true);
    let error             = $state<string | null>(null);
    let detailResult      = $state<SearchResponse | null>(null);
    let detailLoad        = $state(false);

    const params           = $derived(new URLSearchParams(routerState.search));
    const activeSearchName = $derived(params.get('c') ?? '');
    const activeSiteId     = $derived(params.get('s') ?? '');

    $effect(() => {
        const name = activeSearchName || activeSiteId;
        document.title = name ? `${name} | Curated | CandyPop` : 'Curated | CandyPop';
    });

    const activeSearchCollection = $derived(
        searchCollections.find(c => c.name === activeSearchName) ?? null
    );
    const activeSite = $derived(
        siteCollections.find(s => s.id === activeSiteId) ?? null
    );
    const currentPage = $derived(parseInt(params.get('page') ?? '1', 10));
    const totalPages  = $derived(
        detailResult ? Math.ceil(detailResult.videos_filtered_count / settings.resultsPerPage) : 0
    );

    function buildQuery(q: CuratedQuery, page: number): SearchQuery {
        const perPage = settings.resultsPerPage;
        return {
            search_string:      q.search_string      ?? '',
            actor:              q.actor              ?? '',
            studio:             q.studio             ?? '',
            collection:         q.collection         ?? '',
            include_terms:      q.include_terms      ?? [],
            exclude_terms:      q.exclude_terms      ?? [],
            tags:               q.tags               ?? [],
            date_added_from:    '',
            date_added_to:      '',
            date_released_from: '',
            date_released_to:   '',
            only_favourites:    q.only_favourites    ?? '',
            sortby:             q.sortby             ?? 'date_added_desc',
            limit:              perPage,
            startfrom:          (page - 1) * perPage,
        };
    }

    async function loadCollections() {
        loading = true;
        error   = null;
        try {
            const [searchRes, sitesRes] = await Promise.all([
                fetch('/api/get/curated-collections'),
                fetch('/api/curated-sites'),
            ]);
            if (!searchRes.ok) throw new Error(`collections: ${searchRes.status}`);
            if (!sitesRes.ok)  throw new Error(`sites: ${sitesRes.status}`);
            searchCollections = await searchRes.json();
            siteCollections   = await sitesRes.json();
        } catch (e) {
            error = String(e);
        } finally {
            loading = false;
        }
    }

    onMount(loadCollections);

    $effect(() => {
        if (!activeSearchName || !activeSearchCollection) return;

        const controller = new AbortController();
        detailLoad   = true;
        detailResult = null;

        fetch('/api/query/search-videos', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(buildQuery(activeSearchCollection.query, currentPage)),
            signal:  controller.signal,
        })
            .then(r => {
                if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
                return r.json() as Promise<SearchResponse>;
            })
            .then(data => { detailResult = data; })
            .catch(e => { if ((e as Error).name !== 'AbortError') error = String(e); })
            .finally(() => { detailLoad = false; });

        return () => controller.abort();
    });

    function goToPage(n: number) {
        const p = new URLSearchParams(routerState.search);
        if (n <= 1) { p.delete('page'); } else { p.set('page', String(n)); }
        navigate('/curated?' + p.toString());
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="curated-page" class:site-mode={!!activeSiteId}>

    {#if activeSiteId}

        <!-- Site iframe view -->
        <div class="site-bar">
            <button class="btn-back" onclick={() => navigate('/curated')}>← Curated</button>
            <span class="site-bar-title">{activeSite?.name ?? activeSiteId}</span>
            {#if activeSite?.description}
                <span class="site-bar-desc">{activeSite.description}</span>
            {/if}
        </div>
        <iframe
            class="site-iframe"
            src="/curated-sites/{activeSiteId}/index.html"
            title={activeSite?.name ?? activeSiteId}
        ></iframe>

    {:else if activeSearchName}

        <!-- Search collection detail view -->
        <div class="detail-header">
            <button class="btn-back" onclick={() => navigate('/curated')}>← Curated</button>
            <h1 class="detail-title">{activeSearchCollection?.name ?? activeSearchName}</h1>
            {#if activeSearchCollection?.description}
                <p class="detail-desc">{activeSearchCollection.description}</p>
            {/if}
        </div>

        {#if detailLoad}
            <div class="center-pad"><Spinner /></div>
        {:else if error}
            <p class="msg-error">{error}</p>
        {:else if detailResult}
            {#if detailResult.search_results.length === 0}
                <p class="msg-empty">No videos match this collection's filters.</p>
            {:else}
                <p class="results-meta">
                    {detailResult.videos_filtered_count} video(s)
                    {#if totalPages > 1} · page {currentPage} of {totalPages}{/if}
                    · {detailResult.time_taken}s
                </p>
                <div class="card-grid">
                    {#each detailResult.search_results as v (v.hash)}
                        <VideoCard video={v} />
                    {/each}
                </div>
                {#if totalPages > 1}
                    <PageNav page={currentPage} {totalPages} onNavigate={goToPage} />
                {/if}
            {/if}
        {/if}

    {:else}

        <!-- List view -->
        <div class="list-header">
            <h1 class="list-title">Curated</h1>
            <button class="btn-reload" onclick={loadCollections} title="Reload collections">↺</button>
        </div>

        {#if loading}
            <div class="center-pad"><Spinner /></div>
        {:else if error}
            <p class="msg-error">{error}</p>
        {:else if searchCollections.length === 0 && siteCollections.length === 0}
            <p class="msg-empty">
                No curated collections yet. Add saved searches to <code>config.yaml</code>
                or drop HTML sites into <code>curated_sites/</code>.
            </p>
        {:else}
            <div class="collection-grid">
                {#each searchCollections as col (col.name)}
                    <button
                        class="col-card"
                        onclick={() => navigate('/curated?c=' + encodeURIComponent(col.name))}
                    >
                        <span class="col-name">{col.name}</span>
                        {#if col.description}
                            <span class="col-desc">{col.description}</span>
                        {/if}
                    </button>
                {/each}
                {#each siteCollections as site (site.id)}
                    <button
                        class="col-card site-card"
                        onclick={() => navigate('/curated?s=' + encodeURIComponent(site.id))}
                    >
                        <span class="col-name">
                            {site.name}
                            <span class="site-badge">site</span>
                        </span>
                        {#if site.description}
                            <span class="col-desc">{site.description}</span>
                        {/if}
                    </button>
                {/each}
            </div>
        {/if}

    {/if}

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .curated-page {
        width: 100%;
        max-width: 1500px;
        padding: 1.5rem 2rem 4rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    /* Site iframe mode — full-bleed, fills viewport below header */
    .curated-page.site-mode {
        max-width: none;
        padding: 0;
        gap: 0;
        height: calc(100vh - 3.1rem);
    }

    .site-bar {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.45rem 1rem;
        border-bottom: 1px solid #1a1a1a;
        background: #060a0a;
    }

    .site-bar-title {
        font-size: 0.95rem;
        color: #ccc;
        font-weight: 500;
    }

    .site-bar-desc {
        font-size: 0.8rem;
        color: #555;
    }

    .site-iframe {
        flex: 1;
        width: 100%;
        border: none;
        display: block;
        background: #fff;
    }

    /* List view */
    .list-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-bottom: 0.25rem;
    }

    .list-title {
        font-size: 1.1rem;
        color: #888;
        font-weight: 400;
        margin: 0;
    }

    .btn-reload {
        background: transparent;
        border: 1px solid #222;
        border-radius: 5px;
        color: #555;
        font-size: 1rem;
        line-height: 1;
        padding: 0.1rem 0.4rem;
        cursor: pointer;
        transition: color 0.15s, border-color 0.15s;
    }
    .btn-reload:hover { color: #aaa; border-color: #444; }

    .collection-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        padding-top: 0.25rem;
    }

    .col-card {
        background: #0d1212;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        width: 22rem;
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        text-align: left;
        cursor: pointer;
        transition: border-color 0.15s, background 0.15s;
    }
    .col-card:hover { border-color: rgba(255,255,255,0.2); background: #111818; }

    .site-card { border-color: rgba(62, 167, 167, 0.15); }
    .site-card:hover { border-color: rgba(62, 167, 167, 0.4); }

    .col-name {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
        color: #ddd;
        font-weight: 500;
    }
    .col-desc { font-size: 0.82rem; color: #666; line-height: 1.45; }

    .site-badge {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #3ea7a7;
        border: 1px solid #3ea7a7;
        border-radius: 3px;
        padding: 0.05rem 0.3rem;
        line-height: 1.4;
        flex-shrink: 0;
    }

    /* Search detail view */
    .detail-header {
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #1a1a1a;
        margin-bottom: 0.25rem;
    }

    .btn-back {
        background: transparent;
        border: none;
        color: #555;
        font-size: 0.82rem;
        cursor: pointer;
        padding: 0;
        align-self: flex-start;
        margin-bottom: 0.2rem;
    }
    .btn-back:hover { color: #aaa; }

    .detail-title { font-size: 1.3rem; color: #ddd; font-weight: 600; margin: 0; }
    .detail-desc  { font-size: 0.85rem; color: #666; margin: 0; }

    /* Shared */
    .center-pad { display: flex; justify-content: center; padding: 4rem 0; }

    .msg-error { color: #f87171; font-size: 0.9rem; padding: 2rem 0; }
    .msg-empty { color: #555;    font-size: 0.9rem; padding: 2rem 0; }

    .msg-empty code {
        font-family: monospace;
        background: #111;
        border-radius: 3px;
        padding: 0.1em 0.35em;
        color: #888;
    }

    .results-meta {
        color: #444;
        font-size: 0.8rem;
        letter-spacing: 0.03em;
    }

    .card-grid {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 3px;
    }
</style>
