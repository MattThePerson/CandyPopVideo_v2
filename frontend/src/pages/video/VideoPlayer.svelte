<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { PassionPlayer } from '$lib/player/PassionPlayer.js';

    /* Props */
    let { hash, title }: { hash: string; title: string } = $props();

    let hostEl: HTMLDivElement;
    let player: PassionPlayer | null = null;

    // Ensures the seek spritesheet is generated server-side, then fetches both
    // the VTT and the JPEG and passes them to PassionPlayer as a data URL.
    // PassionPlayer's setSeekThumbs requires an inline data URL, not a path.
    async function loadSeekThumbs(p: PassionPlayer) {
        p.setSeekThumbsLoading(true);
        try {
            const ensureRes = await fetch(`/media/ensure/seek-thumbnails/${hash}`);
            if (!ensureRes.ok) { p.setSeekThumbsLoading(false); return; }

            const [vttText, imgBlob] = await Promise.all([
                fetch(`/static/preview-media/0x${hash}/seekthumbs.vtt`).then(r => r.ok ? r.text() : Promise.reject()),
                fetch(`/static/preview-media/0x${hash}/seekthumbs.jpg`).then(r => r.ok ? r.blob() : Promise.reject()),
            ]);

            const dataUrl = await new Promise<string>((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result as string);
                reader.onerror = reject;
                reader.readAsDataURL(imgBlob);
            });

            p.setSeekThumbs(vttText, dataUrl);
        } catch { p.setSeekThumbsLoading(false); }
    }

    onMount(async () => {
        let subsUrl: string | null = null;
        try {
            const res = await fetch(`/media/get/subtitles/${hash}?check=true`);
            if (res.ok) subsUrl = `/media/get/subtitles/${hash}`;
        } catch { /* no subs */ }

        player = new PassionPlayer({
            hostEl,
            src: `/media/get/video/${hash}`,
            poster: `/media/get/poster/${hash}`,
            title,
            subtitles_srt_src: subsUrl,
            autoplay: false,
            quiet: false,
            resumeKey: hash,
        });

        loadSeekThumbs(player);

        fetch(`/api/interact/last-viewed/add/${hash}`, { method: 'POST' }).catch(() => {});
    });

    onDestroy(() => {
        player?.destroy();
        player = null;
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div bind:this={hostEl} class="player-host"></div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .player-host {
        width: 100%;
        height: 100%;
    }
</style>
