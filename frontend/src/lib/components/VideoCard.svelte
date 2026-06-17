<script lang="ts">
    import type { VideoData } from '$lib/types/video';
    import type { CardSize } from '$lib/stores/settings.svelte';
    import { settings } from '$lib/stores/settings.svelte';
    import DefaultCard from '$lib/components/cards/DefaultCard.svelte';

    let { video, size }: { video: VideoData; size?: CardSize } = $props();
</script>

{#if settings.cardVariant === 'default'}
    <DefaultCard {video} size={size ?? settings.cardSize} />
{/if}
