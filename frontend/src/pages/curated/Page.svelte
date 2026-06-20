<!-- pages/curated/Page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { routerState, navigate } from '$lib/router/router.svelte';
    import { settings } from '$lib/stores/settings.svelte';
    import VideoCard from '$lib/components/VideoCard.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import PageNav from '../search/PageNav.svelte';
    import type { VideoData } from '$lib/types/video';
    import type { SearchQuery, SearchResponse } from '../search/types';
    import type { CuratedCollectionMeta, CuratedQuery } from './types';

    let collections  = $state<CuratedCollectionMeta[]>([]);
    let loading      = $state(true);
    let error        = $state<string | null>(null);
    let detailResult = $state<SearchResponse | null>(null);
    let detailLoad   = $state(false);

    const activeName = $derived(
        new URLSearchParams(routerState.search).get('c') ?? ''
    );
    const activeCollection = $derived(
        collections.find(c => c.name === activeName) ?? null
    );
    const currentPage = $derived(
        parseInt(new URLSearchParams(routerState.search).get('page') ?? '1', 10)
    );
    const totalPages = $derived(
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

    onMount(async () => {
        try {
            const r = await fetch('/api/get/curated-collections');
            if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
            collections = await r.json();
        } catch (e) {
            error = String(e);
        } finally {
            loading = false;
        }
    });

    // Fetch detail results whenever the active collection or page changes.
    $effect(() => {
        if (!activeName || !activeCollection) return;

        const controller = new AbortController();
        detailLoad = true;
        detailResult = null;

        fetch('/api/query/search-videos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(buildQuery(activeCollection.query, currentPage)),
            signal: controller.signal,
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

<div class="curated-page">

    {#if activeName}

        <!-- Detail view -->
        <div class="detail-header">
            <button class="btn-back" onclick={() => navigate('/curated')}>← Curated</button>
            <h1 class="detail-title">{activeCollection?.name ?? activeName}</h1>
            {#if activeCollection?.description}
                <p class="detail-desc">{activeCollection.description}</p>
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
        {#if loading}
            <div class="center-pad"><Spinner /></div>
        {:else if error}
            <p class="msg-error">{error}</p>
        {:else if collections.length === 0}
            <p class="msg-empty">No curated collections defined. Add them to config.yaml.</p>
        {:else}
            <div class="collection-grid">
                {#each collections as col (col.name)}
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

    /* List view */
    .collection-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        padding-top: 0.5rem;
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

    .col-name { font-size: 1rem; color: #ddd; font-weight: 500; }
    .col-desc  { font-size: 0.82rem; color: #666; line-height: 1.45; }

    /* Detail view */
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
