<script lang="ts">
    import { onMount } from 'svelte';
    import type { ViewingRow } from './types';

    /* Props */
    let { viewings, duration }: { viewings: ViewingRow[]; duration: number } = $props();

    let canvas: HTMLCanvasElement;

    onMount(() => {
        const ctx = canvas.getContext('2d')!;
        const W = canvas.width, H = canvas.height;
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, W, H);
        if (duration > 0) {
            ctx.fillStyle = 'rgba(204, 105, 179, 0.85)';
            for (const v of viewings) {
                const x = (v.time_start / duration) * W;
                const w = Math.max((v.duration_sec / duration) * W, 2);
                ctx.fillRect(Math.floor(x), 1, Math.ceil(w), H - 2);
            }
        }
    });
</script>

<canvas bind:this={canvas} width="600" height="14" class="bar"></canvas>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .bar {
        display: block;
        width: 100%;
        height: 14px;
        border-radius: 3px;
    }
</style>
