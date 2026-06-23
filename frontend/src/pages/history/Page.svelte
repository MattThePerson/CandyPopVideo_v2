<!-- pages/history/Page.svelte -->
<script lang="ts">
    import { routerState, navigate } from '$lib/router/router.svelte';
    import { onMount } from 'svelte';
    import TabFilmStrip  from './TabFilmStrip.svelte';
    import TabHeatTape   from './TabHeatTape.svelte';
    import TabWatchClock from './TabWatchClock.svelte';

    const tabs = [
        {
            id:    'filmstrip',
            label: 'Film Strip',
            icon:  '🎞',
            desc:  'Your sessions as a scrollable strip of poster cards — hover to preview.',
        },
        {
            id:    'heattape',
            label: 'Heat Tape',
            icon:  '📼',
            desc:  'Per-video coverage bars showing exactly which parts you\'ve watched.',
        },
        {
            id:    'clock',
            label: 'Watch Clock',
            icon:  '⏰',
            desc:  'A 7×24 heatmap of when during the week you watch most.',
        },
        {
            id:    'sessions',
            label: 'Sessions',
            icon:  '🎬',
            desc:  'Viewing sessions reconstructed by time gaps — each binge as one block.',
        },
        {
            id:    'stats',
            label: 'Stats',
            icon:  '📈',
            desc:  'Top videos, top actors and studios, total watch time, and more.',
        },
    ];

    let activeTab = $derived(
        new URLSearchParams(routerState.search).get('tab') ?? 'filmstrip'
    );

    function goTab(id: string) {
        navigate(`/history?tab=${id}`);
    }

    onMount(() => {
        document.title = 'View History · CandyPop';
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="page">

    <div class="page-header">
        <h1 class="page-title">View History</h1>
        <p class="page-subtitle">Explore how you've been watching your library.</p>
    </div>

    <nav class="tab-bar">
        {#each tabs as tab (tab.id)}
            <button
                type="button"
                class="tab-btn"
                class:active={activeTab === tab.id}
                onclick={() => goTab(tab.id)}
            >
                <span class="tab-icon">{tab.icon}</span>
                {tab.label}
            </button>
        {/each}
    </nav>

    <div class="tab-content">

        {#if activeTab === 'filmstrip'}
            <TabFilmStrip />

        {:else if activeTab === 'heattape'}
            <TabHeatTape />

        {:else if activeTab === 'clock'}
            <TabWatchClock />

        {:else if activeTab === 'sessions'}
            <div class="placeholder">
                <div class="ph-icon">🎬</div>
                <h2>Sessions</h2>
                <p>Viewing sessions reconstructed from segment gaps — each binge as one block.</p>
                <span class="coming-soon">Coming soon</span>
            </div>

        {:else if activeTab === 'stats'}
            <div class="placeholder">
                <div class="ph-icon">📈</div>
                <h2>Stats</h2>
                <p>Aggregate numbers: top videos, busiest hours, total watch time, and more.</p>
                <span class="coming-soon">Coming soon</span>
            </div>

        {:else}
            <div class="placeholder">
                <p class="text-[#666]">Unknown tab.</p>
            </div>
        {/if}

    </div>

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .page {
        padding: 2.5rem 3rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    .page-header { margin-bottom: 1.8rem; }

    .page-title {
        font-family: 'Jaro';
        font-size: 2.4rem;
        color: #eee;
        margin-bottom: 0.3rem;
    }

    .page-subtitle { color: #555; font-size: 0.95rem; }

    .tab-bar {
        display: flex;
        gap: 0.2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 2.2rem;
    }

    .tab-btn {
        background: none;
        border: none;
        border-bottom: 2px solid transparent;
        color: #666;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: color 0.12s, border-color 0.12s;
        margin-bottom: -1px;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }
    .tab-btn:hover { color: #bbb; }
    .tab-btn.active {
        color: rgb(204, 105, 179);
        border-bottom-color: rgb(204, 105, 179);
    }

    .tab-icon { font-size: 0.85rem; }

    .tab-content { min-height: 400px; }

    /* Placeholder styles for not-yet-implemented tabs */
    .placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
        text-align: center;
        padding: 5rem 2rem;
        color: #aaa;
    }
    .ph-icon { font-size: 3rem; margin-bottom: 0.5rem; filter: grayscale(0.4); }
    .placeholder h2 { font-family: 'Jaro'; font-size: 1.8rem; color: #ccc; margin: 0; }
    .placeholder p  { max-width: 38ch; font-size: 0.9rem; line-height: 1.6; color: #555; margin: 0; }

    .coming-soon {
        margin-top: 0.5rem;
        display: inline-block;
        background: rgba(204, 105, 179, 0.1);
        color: rgba(204, 105, 179, 0.7);
        border: 1px solid rgba(204, 105, 179, 0.25);
        border-radius: 999px;
        font-size: 0.76rem;
        padding: 0.18rem 0.75rem;
        letter-spacing: 0.04em;
        font-family: 'Inter', sans-serif;
    }
</style>
