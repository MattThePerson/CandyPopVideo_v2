<!-- pages/home/Page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import type { VideoData } from '$lib/types/video';
    import VideoCard from '$lib/components/VideoCard.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import { createPager } from '$lib/util/pager.svelte';

    let video          = $state<VideoData | null>(null);
    let similar        = $state<VideoData[]>([]);
    let queryTime      = $state<number | null>(null);
    let error          = $state<string | null>(null);
    let similarLoading = $state(false);

    const BATCH = 8;
    const pager = createPager(() => similar, BATCH);

    const today = new Date().toDateString();

    onMount(async () => {
        try {
            // const hash = await fetch('/api/get/random-spotlight-video-hash').then(r => r.text());
            const hash = await fetch('/api/get/random-video-hash')
                .then(r => r.json()).then(r => r['hash'] as string)
            video = await fetch(`/api/get/video-data/${hash}`)
                .then(r => r.json()) as VideoData;
            similarLoading = true;
            const res = await fetch(`/api/query/get/similar-videos/${hash}`)
                .then(r => r.json());
            similar   = (res.Videos as VideoData[]).slice(1);
            queryTime = res.TimeTaken as number;
        } catch (e) {
            error = String(e);
        } finally {
            similarLoading = false;
        }
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="p-8">

    <!-- Spotlight -->
    <section class="flex flex-col items-center mb-8">
        <h2 class="mb-4 text-[#aaa] uppercase tracking-widest text-sm font-semibold">
            Spotlight · {today}
        </h2>
        {#if error}
            <p class="text-red-400">{error}</p>
        {:else if video === null}
            <div class="flex justify-center py-16">
                <Spinner />
            </div>
        {:else}
            <VideoCard {video} width="72rem" aspectRatio="21/9" />
        {/if}
    </section>

    <!-- Similar videos -->
    {#if similarLoading}
        <section>
            <h2 class="mb-4 text-[#aaa] uppercase tracking-widest text-sm font-semibold">
                Similar Videos
            </h2>
            <div class="flex justify-center py-12">
                <Spinner />
            </div>
        </section>
    {:else if similar.length > 0}
        <section>
            <h2 class="mb-4 text-[#aaa] uppercase tracking-widest text-sm font-semibold">
                Similar Videos{queryTime !== null ? ` (${queryTime.toFixed(2)}s)` : ''}
            </h2>
            <div class="flex flex-wrap gap-4">
                {#each pager.visible as video (video.hash)}
                    <VideoCard {video} />
                {/each}
            </div>
            {#if pager.hasMore}
                <div class="flex justify-center mt-6">
                    <button class="load-more" onclick={pager.loadMore}>
                        LOAD MORE RESULTS
                    </button>
                </div>
            {/if}
        </section>
    {/if}

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
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
