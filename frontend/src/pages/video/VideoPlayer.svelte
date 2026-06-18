<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { PassionPlayer } from '$lib/player/PassionPlayer.js';

    /* Props */
    let { hash, title }: { hash: string; title: string } = $props();

    let hostEl: HTMLDivElement;
    let player: PassionPlayer | null = null;

    function patchPlayer(shadow: ShadowRoot) {
        const obs = new MutationObserver(() => {
            const vid = shadow.querySelector('video') as HTMLVideoElement | null;
            if (!vid) return;
            obs.disconnect();

            vid.poster = `/media/get/poster/${hash}`;

            // PassionPlayer hardcodes `muted`; slider handler never sets video.volume
            vid.muted = false;
            vid.volume = 1.0;

            const slider = shadow.querySelector('.pp-volume-slider') as HTMLInputElement | null;
            if (slider) {
                slider.addEventListener('input', () => {
                    vid.volume = Number(slider.value) / 100;
                    if (Number(slider.value) > 0) vid.muted = false;
                });
            }
        });
        obs.observe(shadow, { childList: true, subtree: true });
    }

    async function loadSeekThumbs(p: PassionPlayer) {
        try {
            const ensureRes = await fetch(`/media/ensure/seek-thumbnails/${hash}`);
            if (!ensureRes.ok) return;

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
        } catch { /* seek thumbs optional */ }
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
        });

        // attachShadow runs synchronously in PassionPlayer constructor
        if (hostEl.shadowRoot) patchPlayer(hostEl.shadowRoot);

        loadSeekThumbs(player);

        fetch(`/api/interact/last-viewed/add/${hash}`, { method: 'POST' }).catch(() => {});
    });

    onDestroy(() => {
        player?.destroy();
        player = null;
    });
</script>

<div bind:this={hostEl} class="player-host"></div>

<style>
    .player-host {
        width: 100%;
        height: 100%;
    }
</style>
