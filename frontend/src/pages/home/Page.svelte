<script lang="ts">
    import { onMount } from 'svelte';

    let title = $state<string | null>(null);
    let error = $state<string | null>(null);

    onMount(async () => {
        try {
            // const hash = await fetch('/api/get/random-spotlight-video-hash').then(r => r.text());
            const hash = await fetch('/api/get/random-video-hash').then(r => r.json()).then(r => r["hash"]);
            console.debug('spotlight video hash:', hash)
            const data = await fetch(`/api/get/video-data/${hash}`).then(r => r.json());
            title = data.title ?? data.scene_title ?? data.filename ?? hash;
        } catch (e) {
            error = String(e);
        }
    });
</script>

<div class="p-8">
    <h2 class="text-xl font-semibold mb-3 text-[#aaa] uppercase tracking-widest text-sm">
        Today's Spotlight
    </h2>
    {#if error}
        <p class="text-red-400">{error}</p>
    {:else if title === null}
        <p class="text-[#555]">Loading...</p>
    {:else}
        <p class="text-2xl font-semibold">{title}</p>
    {/if}
</div>
