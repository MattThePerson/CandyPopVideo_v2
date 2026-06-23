<script lang="ts">
    import Spinner from './Spinner.svelte';
    import VideoCard from './VideoCard.svelte';
    import { createPager } from '$lib/util/pager.svelte';
    import type { VideoData } from '$lib/types/video';

    /* Props */
    let {
        video,
        similar,
        loading,
        queryTime,
        relatedHashes,
    }: {
        video: VideoData;
        similar: VideoData[];
        loading: boolean;
        queryTime: number | null;
        relatedHashes?: Set<string>;
    } = $props();

    type SameOrDiff = 'same' | 'different' | null;

    let filterRelated    = $state(false);
    let filterStudio     = $state<SameOrDiff>(null);
    let filterCollection = $state<SameOrDiff>(null);
    let filterActors     = $state<SameOrDiff>(null);

    let includeInput = $state('');
    let excludeInput = $state('');
    let includeTags  = $state<string[]>([]);
    let excludeTags  = $state<string[]>([]);

    const relatedInSimilar = $derived(similar.filter(v => relatedHashes?.has(v.hash)).length);

    const activeFilterTags = $derived(
        [
            filterStudio === 'same'          && video.studio         ? `same studio: "${video.studio}"` : null,
            filterStudio === 'different'     && video.studio         ? `diff studio: "${video.studio}"` : null,
            filterCollection === 'same'      && video.collection     ? `same collection: "${video.collection}"` : null,
            filterCollection === 'different' && video.collection     ? `diff collection: "${video.collection}"` : null,
            filterActors === 'same'          && video.actors?.length ? `same actors: "${video.actors.join(', ')}"` : null,
            filterActors === 'different'     && video.actors?.length ? `diff actors: "${video.actors.join(', ')}"` : null,
        ].filter(Boolean).join(' | ')
    );

    function searchText(v: VideoData): string {
        return [
            v.title, v.scene_title, v.studio, v.collection, v.line,
            v.description, v.actors?.join(' '), v.tags?.join(' '),
        ].filter(Boolean).join(' ').toLowerCase();
    }

    const pager = createPager(() => {
        let out = similar;
        if (filterRelated && relatedHashes)       out = out.filter(v => !relatedHashes.has(v.hash));
        if (filterStudio === 'same')              out = out.filter(v => v.studio === video.studio);
        if (filterStudio === 'different')         out = out.filter(v => v.studio !== video.studio);
        if (filterCollection === 'same')          out = out.filter(v => v.collection === video.collection);
        if (filterCollection === 'different')     out = out.filter(v => v.collection !== video.collection);
        if (filterActors === 'same')              out = out.filter(v => v.actors?.some(a => video.actors?.includes(a)));
        if (filterActors === 'different')         out = out.filter(v => !v.actors?.some(a => video.actors?.includes(a)));
        if (includeTags.length)                   out = out.filter(v => includeTags.every(t => searchText(v).includes(t)));
        if (excludeTags.length)                   out = out.filter(v => !excludeTags.some(t => searchText(v).includes(t)));
        return out;
    }, 8);

    $effect(() => { filterRelated; filterStudio; filterCollection; filterActors; includeTags; excludeTags; pager.reset(); });

    function processTerms(raw: string): string[] {
        return raw.split(',').map(t => t.trim().toLowerCase()).filter(t => t.length > 0);
    }

    function handleIncludeKey(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            const terms = processTerms(includeInput);
            if (terms.length) { includeTags = [...includeTags, ...terms]; includeInput = ''; }
        } else if ((e.key === 'Backspace' || e.key === 'Delete') && includeInput === '') {
            includeTags = includeTags.slice(0, -1);
        }
    }

    function handleExcludeKey(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            const terms = processTerms(excludeInput);
            if (terms.length) { excludeTags = [...excludeTags, ...terms]; excludeInput = ''; }
        } else if ((e.key === 'Backspace' || e.key === 'Delete') && excludeInput === '') {
            excludeTags = excludeTags.slice(0, -1);
        }
    }

    function removeIncludeTag(i: number) { includeTags = includeTags.filter((_, idx) => idx !== i); }
    function removeExcludeTag(i: number) { excludeTags = excludeTags.filter((_, idx) => idx !== i); }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<section class="similar-section">
    <div class="similar-header">
        <div class="similar-title-row">
            <h2 class="similar-title">SIMILAR VIDEOS</h2>
            {#if queryTime !== null}
                <span class="query-time">{queryTime.toFixed(2)}s</span>
            {/if}
            {#if activeFilterTags}
                <span class="active-filter-tags">{activeFilterTags}</span>
            {/if}
        </div>

        <div class="filter-btns">
            {#if relatedHashes !== undefined}
                <button
                    class="filter-btn"
                    class:active={filterRelated}
                    disabled={relatedInSimilar === 0}
                    onclick={() => { filterRelated = !filterRelated; }}
                >
                    FILTER RELATED{relatedInSimilar > 0 ? ` (${relatedInSimilar})` : ''}
                </button>
            {/if}

            <div class="filter-group" class:group-disabled={!video.collection}>
                <span class="group-label">Collection:</span>
                <div class="btn-pair">
                    <button
                        class="filter-btn"
                        class:active={filterCollection === 'same'}
                        disabled={!video.collection}
                        onclick={() => { filterCollection = filterCollection === 'same' ? null : 'same'; }}
                    >SAME</button>
                    <button
                        class="filter-btn diff-btn"
                        class:active-diff={filterCollection === 'different'}
                        disabled={!video.collection}
                        onclick={() => { filterCollection = filterCollection === 'different' ? null : 'different'; }}
                    >DIFFERENT</button>
                </div>
            </div>

            <div class="filter-group" class:group-disabled={!video.studio}>
                <span class="group-label">Studio:</span>
                <div class="btn-pair">
                    <button
                        class="filter-btn"
                        class:active={filterStudio === 'same'}
                        disabled={!video.studio}
                        onclick={() => { filterStudio = filterStudio === 'same' ? null : 'same'; }}
                    >SAME</button>
                    <button
                        class="filter-btn diff-btn"
                        class:active-diff={filterStudio === 'different'}
                        disabled={!video.studio}
                        onclick={() => { filterStudio = filterStudio === 'different' ? null : 'different'; }}
                    >DIFFERENT</button>
                </div>
            </div>

            <div class="filter-group" class:group-disabled={!video.actors?.length}>
                <span class="group-label">Actors:</span>
                <div class="btn-pair">
                    <button
                        class="filter-btn"
                        class:active={filterActors === 'same'}
                        disabled={!video.actors?.length}
                        onclick={() => { filterActors = filterActors === 'same' ? null : 'same'; }}
                    >SAME</button>
                    <button
                        class="filter-btn diff-btn"
                        class:active-diff={filterActors === 'different'}
                        disabled={!video.actors?.length}
                        onclick={() => { filterActors = filterActors === 'different' ? null : 'different'; }}
                    >DIFFERENT</button>
                </div>
            </div>

            <div class="filter-group">
                <span class="group-label">Include:</span>
                <input
                    class="term-input"
                    type="text"
                    placeholder="term1, term2... (Enter)"
                    bind:value={includeInput}
                    onkeydown={handleIncludeKey}
                />
                {#each includeTags as tag, i}
                    <span class="term-chip include">
                        {tag}<button class="chip-remove" onclick={() => removeIncludeTag(i)}>×</button>
                    </span>
                {/each}
            </div>

            <div class="filter-group">
                <span class="group-label">Exclude:</span>
                <input
                    class="term-input"
                    type="text"
                    placeholder="term1, term2... (Enter)"
                    bind:value={excludeInput}
                    onkeydown={handleExcludeKey}
                />
                {#each excludeTags as tag, i}
                    <span class="term-chip exclude">
                        {tag}<button class="chip-remove" onclick={() => removeExcludeTag(i)}>×</button>
                    </span>
                {/each}
            </div>
        </div>
    </div>

    {#if loading}
        <div class="similar-center">
            <Spinner />
        </div>
    {:else if pager.visible.length > 0}
        <div class="card-grid">
            {#each pager.visible as v (v.hash)}
                <VideoCard video={v} />
            {/each}
        </div>
        {#if pager.hasMore}
            <div class="load-more-wrap">
                <button class="load-more" onclick={pager.loadMore}>
                    LOAD MORE RESULTS
                </button>
            </div>
        {/if}
    {:else if !loading && similar.length > 0}
        <p class="no-results">No results match the active filters.</p>
    {/if}
</section>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .similar-section {
        max-width: 120rem;
        width: 100%;
        margin: 0 auto;
        padding: 1.5rem 4rem 2rem;
        border-top: 1px solid #1a1a1a;
    }

    .similar-header {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        margin-bottom: 1rem;
        margin-left: 5rem;
    }

    .similar-title-row {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
    }

    .similar-title {
        color: #aaa;
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .query-time {
        font-size: 0.72rem;
        color: #444;
        font-weight: 400;
        letter-spacing: 0;
    }

    .active-filter-tags {
        font-size: 0.72rem;
        color: #666;
        font-style: italic;
        font-weight: 400;
        letter-spacing: 0;
    }

    .filter-btns {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        align-items: center;
    }

    /* Base filter button */
    .filter-btn {
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
    .filter-btn:hover:not(:disabled):not(.active):not(.active-diff) {
        border-color: #555;
        color: #ccc;
    }
    .filter-btn.active {
        border-color: #D79C29;
        color: #D79C29;
    }
    .filter-btn.active:hover:not(:disabled) {
        border-color: #b07e1a;
        color: #b07e1a;
    }
    .filter-btn.active-diff {
        border-color: #c94040;
        color: #e06060;
    }
    .filter-btn.active-diff:hover:not(:disabled) {
        border-color: #a03030;
        color: #c04040;
    }
    .filter-btn:disabled {
        opacity: 0.3;
        cursor: default;
        pointer-events: none;
    }

    /* Label + button/input group */
    .filter-group {
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }
    .filter-group.group-disabled {
        opacity: 0.3;
        pointer-events: none;
    }

    .group-label {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #555;
        white-space: nowrap;
    }

    /* Paired SAME / DIFFERENT buttons */
    .btn-pair {
        display: flex;
    }
    .btn-pair .filter-btn:first-child {
        border-radius: 4px 0 0 4px;
        margin-right: -1px;
    }
    .btn-pair .diff-btn {
        border-radius: 0 4px 4px 0;
    }
    .btn-pair .filter-btn.active,
    .btn-pair .filter-btn.active-diff {
        position: relative;
        z-index: 1;
    }

    .term-input {
        background: #111;
        border: 1px solid #2a2a2a;
        color: #aaa;
        border-radius: 4px;
        padding: 0.25rem 0.5rem;
        font-size: 0.72rem;
        width: 10.5rem;
        outline: none;
        transition: border-color 0.15s, color 0.15s;
    }
    .term-input:focus {
        border-color: #555;
        color: #ccc;
    }
    .term-input::placeholder {
        color: #333;
    }

    .term-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        border-radius: 3px;
        padding: 0.15rem 0.3rem 0.15rem 0.5rem;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }
    .term-chip.include {
        background: #1a2a1a;
        color: #5a9a5a;
        border: 1px solid #2a4a2a;
    }
    .term-chip.exclude {
        background: #2a1a1a;
        color: #9a5a5a;
        border: 1px solid #4a2a2a;
    }

    .chip-remove {
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        padding: 0 0.1rem;
        font-size: 0.8rem;
        line-height: 1;
        opacity: 0.6;
        transition: opacity 0.1s;
    }
    .chip-remove:hover {
        opacity: 1;
    }

    /* Results */
    .card-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 3px;
    }

    .similar-center {
        display: flex;
        justify-content: center;
        padding: 3rem 0;
    }

    .no-results {
        color: #555;
        font-size: 0.85rem;
        padding: 1rem 0;
        margin-bottom: 50rem;
    }

    .load-more-wrap {
        display: flex;
        justify-content: center;
        margin-top: 1.5rem;
    }

    .load-more {
        background: #151515;
        color: #aaa;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 0.5rem 2rem;
        font-size: 0.8rem;
        font-weight: bold;
        letter-spacing: 0.1em;
        cursor: pointer;
        transition: border-color 0.15s, color 0.15s;
    }
    .load-more:hover {
        border-color: #666;
        color: #eee;
    }
</style>
