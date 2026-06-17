<script lang="ts">
    import { onMount } from 'svelte';
    import type { VideoData } from '$lib/types/video';

    let video = $state<VideoData | null>(null);
    let error = $state<string | null>(null);

    onMount(async () => {
        try {
            const hash = await fetch('/api/get/random-video-hash').then(r => r.json()).then(r => r["hash"] as string);
            console.debug('spotlight video hash:', hash);
            video = await fetch(`/api/get/video-data/e1822743989d`).then(r => r.json()) as VideoData;
        } catch (e) {
            error = String(e);
        }
    });
    $inspect(video);

    let displayTitle = $derived(
        video ? (video.title || video.scene_title || video.filename || video.hash) : null
    );
</script>

<div class="p-8">
    <h2 class="text-xl font-semibold mb-3 text-[#aaa] uppercase tracking-widest text-sm">
        Today's Spotlight
    </h2>
    {#if error}
        <p class="text-red-400">{error}</p>
    {:else if video === null}
        <p class="text-[#555]">Loading...</p>
    {:else}
        <p class="text-2xl font-semibold">{displayTitle}</p>
    {/if}
</div>
