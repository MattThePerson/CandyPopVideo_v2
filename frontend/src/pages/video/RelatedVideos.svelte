<script lang="ts">
    import { onMount, tick } from 'svelte';
    import type { VideoData } from '$lib/types/video';
    import VideoCard from '$lib/components/VideoCard.svelte';

    /* Props */
    let { video, onRelatedLoaded }: {
        video: VideoData;
        onRelatedLoaded: (hashes: Set<string>) => void;
    } = $props();

    type Category = { title: string; videos: VideoData[] };
    type CatKey = 'movie-series' | 'movie' | 'from-line' | 'from-actors' | 'from-actor-studio';

    const ORDER: CatKey[] = ['movie-series', 'movie', 'from-line', 'from-actors', 'from-actor-studio'];

    const LABELS: Record<CatKey, string> = {
        'movie-series':      'Movie Series',
        'movie':             'Movie',
        'from-line':         'Line',
        'from-actors':       'Actors',
        'from-actor-studio': 'Actor × Studio',
    };

    let categories = $state<Partial<Record<CatKey, Category>>>({});
    let activeKey  = $state<CatKey | null>(null);
    let loadedSets = $state<Record<string, Set<number>>>({});

    // Property-access derived — avoids Object.keys() which may not track reliably in Svelte 5.
    const categoryKeys = $derived(ORDER.filter(k => categories[k] != null));

    const firstActivated = new Set<string>();
    const carouselRefs: Record<string, HTMLElement | null> = {};

    // --- Fetchers ---

    async function fetchList(url: string): Promise<VideoData[]> {
        try {
            const r = await fetch(url);
            return r.ok ? (await r.json() as VideoData[]) : [];
        } catch { return []; }
    }

    async function fetchSearch(query: object): Promise<VideoData[]> {
        try {
            const r = await fetch('/api/query/search-videos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(query),
            });
            if (!r.ok) return [];
            return ((await r.json()).search_results as VideoData[]) ?? [];
        } catch { return []; }
    }

    function baseQuery() {
        return {
            search_string: null, actor: null, studio: null, collection: null,
            include_terms: null, exclude_terms: null, tags: null,
            date_added_from: null, date_added_to: null,
            date_released_from: null, date_released_to: null,
            only_favourites: 'false', sortby: 'date_released', limit: 99, startfrom: 0,
        };
    }

    // --- Mount: fetch all categories concurrently ---

    onMount(async () => {
        type RelatedCategoryEntry = [CatKey, Category | null];
        const pending: Promise<RelatedCategoryEntry>[] = [];

        if (video.movie_series) {
            pending.push(
                fetchList(`/api/get/movie-series/${encodeURIComponent(video.movie_series)}`)
                    .then(vs => {
                        console.debug(`[related] movie-series: ${vs.length} result(s)${vs.length === 1 ? ' — only current video, skipping' : ''}`);
                        const cat = vs.length > 1
                            ? { title: `Movie Series: "${video.movie_series}"`, videos: vs }
                            : null;
                        return ['movie-series', cat] as RelatedCategoryEntry;
                    })
            );
        }
        if (video.movie_title) {
            pending.push(
                fetchList(`/api/get/movie/${encodeURIComponent(video.movie_title)}`)
                    .then(vs => {
                        console.debug(`[related] movie: ${vs.length} result(s)${vs.length === 1 ? ' — only current video, skipping' : ''}`);
                        const cat = vs.length > 1
                            ? { title: `Movie: "${video.movie_title}"`, videos: vs }
                            : null;
                        return ['movie', cat] as RelatedCategoryEntry;
                    })
            );
        }
        if (video.line) {
            pending.push(
                fetchList(`/api/get/line/${encodeURIComponent(video.line)}`)
                    .then(vs => {
                        console.debug(`[related] from-line: ${vs.length} result(s)${vs.length === 1 ? ' — only current video, skipping' : ''}`);
                        const cat = vs.length > 1
                            ? { title: `Line: ${video.line}`, videos: vs }
                            : null;
                        return ['from-line', cat] as RelatedCategoryEntry;
                    })
            );
        }
        if ((video.actors?.length ?? 0) > 1) {
            const q = { ...baseQuery(), actor: video.actors.join(',') };
            const label = video.actors.slice(0, -1).join(', ') + ' & ' + video.actors.at(-1);
            pending.push(
                fetchSearch(q)
                    .then(vs => {
                        console.debug(`[related] from-actors: ${vs.length} result(s)${vs.length === 1 ? ' — only current video, skipping' : ''}`);
                        const cat = vs.length > 1
                            ? { title: `With: ${label}`, videos: vs }
                            : null;
                        return ['from-actors', cat] as RelatedCategoryEntry;
                    })
            );
        }
        if (video.primary_actors?.length === 1 && video.studio) {
            const q = { ...baseQuery(), actor: video.primary_actors[0], studio: video.studio };
            pending.push(
                fetchSearch(q)
                    .then(vs => {
                        console.debug(`[related] from-actor-studio: ${vs.length} result(s)${vs.length === 1 ? ' — only current video, skipping' : ''}`);
                        const cat = vs.length > 1
                            ? { title: `${video.primary_actors[0]} in ${video.studio}`, videos: vs }
                            : null;
                        return ['from-actor-studio', cat] as RelatedCategoryEntry;
                    })
            );
        }

        const results = await Promise.all(pending);
        const built: Partial<Record<CatKey, Category>> = {};
        for (const [key, cat] of results) {
            if (cat) built[key] = cat;
        }
        console.debug('[related] categories loaded:', Object.keys(built));
        categories = built;

        const allHashes = new Set(
            (Object.values(built) as Category[]).flatMap(c => c.videos.map(v => v.hash))
        );
        onRelatedLoaded(allHashes);

        const firstKey = ORDER.find(k => k in built) ?? null;
        if (firstKey) {
            await tick();
            selectCategory(firstKey);
        }
    });

    // --- Carousel activation ---

    async function selectCategory(key: CatKey) {
        if (activeKey === key) return;
        activeKey = key;
        if (!firstActivated.has(key)) {
            firstActivated.add(key);
            await tick();
            initCarousel(key);
        }
    }

    // Sets up scroll centering + IntersectionObserver on first view of a carousel.
    function initCarousel(key: string) {
        const cat = categories[key as CatKey];
        const el  = carouselRefs[key];
        if (!cat || !el) return;

        const targetIdx = cat.videos.findIndex(v => v.hash === video.hash);
        const toLoad = new Set<number>();
        for (let d = -2; d <= 2; d++) {
            const i = targetIdx + d;
            if (i >= 0 && i < cat.videos.length) toLoad.add(i);
        }
        loadedSets[key] = toLoad;

        tick().then(() => {
            const targetEl = el.querySelector<HTMLElement>('.carousel-target');
            if (targetEl) {
                el.scrollLeft = targetEl.offsetLeft - el.clientWidth / 2 + targetEl.clientWidth / 2;
            }

            const observer = new IntersectionObserver((entries) => {
                for (const entry of entries) {
                    if (!entry.isIntersecting) continue;
                    observer.unobserve(entry.target);
                    const idx = parseInt((entry.target as HTMLElement).dataset.idx ?? '-1');
                    if (idx >= 0) loadedSets[key].add(idx);
                }
            }, { root: el, threshold: 0.1 });

            el.querySelectorAll<HTMLElement>('.carousel-placeholder').forEach(ph => observer.observe(ph));
        });
    }

    function scrollCarousel(delta: number) {
        if (!activeKey) return;
        carouselRefs[activeKey]?.scrollBy({ left: delta, behavior: 'smooth' });
    }

    let visible = $state(localStorage.getItem('related-videos-visible') !== 'false');

    function toggleVisible() {
        visible = !visible;
        localStorage.setItem('related-videos-visible', String(visible));
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

{#if categoryKeys.length > 0}
<section class="related-section">

    <div class="section-header">
        <div class="header-left">
            <button class="toggle-btn" onclick={toggleVisible} aria-label="Toggle related videos">
                {#if visible}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                </svg>
                {:else}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
                {/if}
            </button>
            <h2 class="section-title" class:dimmed={!visible}>RELATED VIDEOS</h2>
        </div>
        {#if visible}
        <div class="scroll-btns">
            <button class="scroll-btn" onclick={() => scrollCarousel(-800)}>‹</button>
            <button class="scroll-btn" onclick={() => scrollCarousel(800)}>›</button>
        </div>
        {/if}
    </div>

    {#if visible}
    <div class="cat-nav">
        {#each ORDER as key}
            {@const cat = categories[key]}
            <button
                class="cat-btn"
                class:selected={activeKey === key}
                disabled={!cat}
                onclick={() => selectCategory(key)}
            >
                {LABELS[key]}{cat ? ` (${cat.videos.length})` : ''}
            </button>
        {/each}
    </div>

    <div class="carousels">
        {#each categoryKeys as key}
            {@const cat = categories[key]!}
            <div
                class="carousel"
                class:active={activeKey === key}
                bind:this={carouselRefs[key]}
            >
                {#each cat.videos as v, i}
                    {#if loadedSets[key]?.has(i)}
                        <div class:carousel-target={v.hash === video.hash}>
                            <VideoCard video={v} size="small" />
                        </div>
                    {:else}
                        <div class="carousel-placeholder" data-idx={i}>
                            <div class="ph-thumb"></div>
                            <div class="ph-title">{v.title || v.filename}</div>
                        </div>
                    {/if}
                {/each}
            </div>
        {/each}
    </div>
    {/if}

</section>
{/if}

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .related-section {
        padding: 1rem 2rem 1.5rem;
        border-top: 1px solid #1a1a1a;
        max-width: 89.375rem;
        margin: 0 auto;
    }

    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
    }

    .header-left {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .toggle-btn {
        background: none;
        border: none;
        color: #555;
        cursor: pointer;
        padding: 0.1rem 0.2rem;
        line-height: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: color 0.15s;
    }
    .toggle-btn:hover {
        color: #aaa;
    }

    .section-title {
        color: #aaa;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        transition: color 0.18s;
    }
    .section-title.dimmed {
        color: #444;
    }

    .scroll-btns {
        display: flex;
        gap: 0.25rem;
    }

    .scroll-btn {
        background: #151515;
        border: 1px solid #333;
        color: #aaa;
        border-radius: 4px;
        width: 2rem;
        height: 2rem;
        font-size: 1.2rem;
        line-height: 1;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: border-color 0.15s, color 0.15s;
    }
    .scroll-btn:hover {
        border-color: #666;
        color: #eee;
    }

    .cat-nav {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.65rem;
    }

    .cat-btn {
        background: #111;
        border: 1px solid #2a2a2a;
        color: #666;
        border-radius: 4px;
        padding: 0.3rem 0.75rem;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        cursor: pointer;
        transition: border-color 0.15s, color 0.15s;
    }
    .cat-btn:disabled {
        opacity: 0.3;
        cursor: default;
    }
    .cat-btn.selected {
        border-color: #D79C29;
        color: #D79C29;
    }
    .cat-btn:not(:disabled):not(.selected):hover {
        border-color: #555;
        color: #ccc;
    }

    .carousel {
        display: none;
        gap: 0.75rem;
        overflow-x: hidden;
    }
    .carousel.active {
        display: flex;
    }
    .carousel::-webkit-scrollbar { display: none; }

    .carousel-target {
        outline: 2px solid #D79C29;
        outline-offset: 3px;
        border-radius: 6px;
        flex-shrink: 0;
    }

    .carousel-placeholder {
        width: 20.5rem;
        flex-shrink: 0;
        background: #0e0e0e;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #1a1a1a;
    }
    .ph-thumb {
        width: 100%;
        aspect-ratio: 14/9;
        background: #181818;
    }
    .ph-title {
        padding: 0.4rem 0.6rem;
        font-size: 0.72rem;
        color: #444;
        height: 3.5rem;
        overflow: hidden;
    }
</style>
