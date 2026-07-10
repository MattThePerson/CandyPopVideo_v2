<script lang="ts">
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import SuggestedPanel from './SuggestedPanel.svelte';

    /* Props */
    let { hash, video, interact, suggested = [], suggestedLoading = false, onRefetch }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
        suggested?: VideoData[];
        suggestedLoading?: boolean;
        onRefetch?: (p: { ignoreLast: string; popMult: number; platMult: number; poolSize: number }) => void;
    } = $props();
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="focus-layout">
    <SuggestedPanel {suggested} loading={suggestedLoading} {onRefetch} />
</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .focus-layout {
        width: 100%;
        background: #000;
        display: flex;
        justify-content: flex-end;
        padding: 0.5rem 0 0.5rem 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }
</style>
