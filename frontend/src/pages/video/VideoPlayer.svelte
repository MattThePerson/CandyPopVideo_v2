<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { PassionPlayer, type TrackInfo } from '$lib/player/PassionPlayer.js';
    import { settings } from '$lib/stores/settings.svelte';

    /* Props */
    let { hash, title, fps = null, markers = [], datedMarkers = [], onVideoReady = null }: {
        hash: string;
        title: string;
        fps?: number | null;
        markers?: [number, string, string][];
        datedMarkers?: [number, string][];
        onVideoReady?: ((el: HTMLVideoElement) => void) | null;
    } = $props();

    let hostEl: HTMLDivElement;
    let player: PassionPlayer | null = null;

    // Viewing section tracking
    let sectionStart: number | null = null;
    let lastKnownTime = 0;
    // Prevents timeupdate from overwriting lastKnownTime during the seek event sequence
    // (browser fires: seeking → timeupdate → seeked; timeupdate fires with the NEW time).
    let isSeeking = false;

    // Subtitle state
    let subsTrackEl: HTMLTrackElement | null = null;
    let subsVttUrl: string | null = null;
    let subsActiveSid = 0;
    const subsTracks: TrackInfo[] = [{ id: 1, type: 'sub', lang: 'en', title: 'Subtitles' }];

    // Cleanup refs for event listeners
    let seekThumbsVisibilityHandler: (() => void) | undefined;
    let videoEl: HTMLVideoElement | null = null;
    let onTimeUpdate:   (() => void) | null = null;
    let onPlay:         (() => void) | null = null;
    let onPause:        (() => void) | null = null;
    let onSeeking:      (() => void) | null = null;
    let onSeeked:       (() => void) | null = null;
    let onEnded:        (() => void) | null = null;
    let onBeforeUnload: (() => void) | null = null;

    // Sends a completed section to the backend (start position + duration).
    // Sections shorter than 1.5s are dropped — the backend enforces the same floor.
    // On success, refreshes the viewed-segments overlay so new sections appear immediately.
    function submitSection(start: number | null, end: number) {
        if (start === null) return;
        const duration = Math.round((end - start) * 1000) / 1000;
        if (duration < 1.5) return;
        fetch(`/api/interact/viewing/add/${hash}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                time_start:   Math.round(start * 1000) / 1000,
                duration_sec: duration,
            }),
        }).then((res) => {
            if (res.ok && player) loadViewedSegments(player);
        }).catch(() => {});
    }

    async function loadViewedSegments(p: PassionPlayer) {
        try {
            const res = await fetch(`/api/interact/viewings/${hash}`);
            if (!res.ok) return;
            const data = await res.json();
            p.setViewedSegments(data);
        } catch { /* non-critical */ }
    }

    // Fetch SRT, convert to WebVTT blob, attach <track> to video, wire cuechange → setSubtitleState.
    async function loadSubtitles(p: PassionPlayer, srtUrl: string, vid: HTMLVideoElement) {
        try {
            const res = await fetch(srtUrl);
            if (!res.ok) return;
            const srt = await res.text();
            const vtt = 'WEBVTT\n\n' + srt.replace(/(\d{2}:\d{2}:\d{2}),(\d{3})/g, '$1.$2');
            subsVttUrl = URL.createObjectURL(new Blob([vtt], { type: 'text/vtt' }));

            subsTrackEl = document.createElement('track');
            subsTrackEl.kind = 'subtitles';
            subsTrackEl.label = 'Subtitles';
            subsTrackEl.srclang = 'en';
            subsTrackEl.src = subsVttUrl;
            vid.appendChild(subsTrackEl);

            // Set mode immediately — don't wait for 'load' (unreliable in Shadow DOM / blob URLs).
            // Setting mode='hidden' triggers the browser to start loading the track resource.
            subsTrackEl.track.mode = 'hidden';
            subsActiveSid = 1;
            p.setSubtitleState(null, subsTracks, 1);

            subsTrackEl.track.addEventListener('cuechange', () => {
                if (subsActiveSid === 0) return;
                const cues = subsTrackEl!.track.activeCues;
                const text = cues?.length ? (cues[0] as VTTCue).text : null;
                p.setSubtitleState(text, subsTracks, 1);
            });
        } catch { /* no subtitles */ }
    }

    // Ensures the seek spritesheet is generated server-side, then fetches both
    // the VTT and the JPEG and passes them to PassionPlayer as a data URL.
    // PassionPlayer's setSeekThumbs requires an inline data URL, not a path.
    async function loadSeekThumbs(p: PassionPlayer) {
        p.setSeekThumbsLoading(true);
        try {
            const ensureRes = await fetch(`/media/ensure/seek-thumbnails/${hash}${settings.devParam}`);
            if (!ensureRes.ok) { p.setSeekThumbsLoading(false); return; }

            const [vttText, imgBlob] = await Promise.all([
                fetch(`/media/preview/${hash}/seekthumbs.vtt${settings.devParam}`).then(r => r.ok ? r.text() : Promise.reject()),
                fetch(`/media/preview/${hash}/seekthumbs.jpg${settings.devParam}`).then(r => r.ok ? r.blob() : Promise.reject()),
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
            src: `/media/get/video/${hash}${settings.devParam}`,
            poster: `/media/get/poster/${hash}${settings.devParam}`,
            title,
            subtitles_srt_src: subsUrl,
            autoplay: false,
            quiet: false,
            resumeKey: hash,
            fps,
            onMarkersUpdate: (updated) => {
                fetch(`/api/interact/markers/update/${hash}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updated),
                }).catch(() => {});
            },
            onDatedMarkersUpdate: (updated) => {
                fetch(`/api/interact/dated-markers/update/${hash}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updated),
                }).catch(() => {});
            },
            onSubtitleChange: (sid: number) => {
                subsActiveSid = sid;
                if (!subsTrackEl || !player) return;
                if (sid === 0) {
                    subsTrackEl.track.mode = 'disabled';
                    player.setSubtitleState(null, subsTracks, 0);
                } else {
                    subsTrackEl.track.mode = 'hidden';
                    const cues = subsTrackEl.track.activeCues;
                    const text = cues?.length ? (cues[0] as VTTCue).text : null;
                    player.setSubtitleState(text, subsTracks, sid);
                }
            },
        });

        if (document.visibilityState === 'visible') {
            loadSeekThumbs(player);
        } else {
            seekThumbsVisibilityHandler = () => {
                document.removeEventListener('visibilitychange', seekThumbsVisibilityHandler!);
                seekThumbsVisibilityHandler = undefined;
                if (player) loadSeekThumbs(player);
            };
            document.addEventListener('visibilitychange', seekThumbsVisibilityHandler);
        }
        setTimeout(() => { if (player) loadViewedSegments(player); }, 500);
        if (markers.length)      player.setMarkers(markers);
        if (datedMarkers.length) player.setDatedMarkers(datedMarkers);

        // PassionPlayer's _init() is async: it awaits a style injection before calling
        // _addHTML (which inserts <video>). Query immediately after construction returns
        // null. Wait for the element to appear via MutationObserver instead.
        const shadow = hostEl.shadowRoot!;
        videoEl = await new Promise<HTMLVideoElement>((resolve) => {
            const existing = shadow.querySelector('video');
            if (existing) { resolve(existing as HTMLVideoElement); return; }
            const mo = new MutationObserver(() => {
                const el = shadow.querySelector('video');
                if (el) { mo.disconnect(); resolve(el as HTMLVideoElement); }
            });
            mo.observe(shadow, { childList: true, subtree: true });
        });

        if (subsUrl) loadSubtitles(player, subsUrl, videoEl);
        onVideoReady?.(videoEl);

        // Gate timeupdate on !isSeeking: the browser fires seeking→timeupdate→seeked,
        // so timeupdate would overwrite lastKnownTime with the new position before seeked runs.
        onTimeUpdate = () => { if (!isSeeking) lastKnownTime = videoEl!.currentTime; };
        onPlay       = () => { sectionStart = videoEl!.currentTime; };
        onPause      = () => { submitSection(sectionStart, videoEl!.currentTime); sectionStart = null; };
        onSeeking    = () => { isSeeking = true; };
        onSeeked     = () => {
            submitSection(sectionStart, lastKnownTime);
            isSeeking = false;
            sectionStart = videoEl!.paused ? null : videoEl!.currentTime;
        };
        onEnded      = () => { submitSection(sectionStart, videoEl!.currentTime); sectionStart = null; };
        // sendBeacon is the only reliable way to fire a POST on tab close.
        onBeforeUnload = () => {
            if (sectionStart === null) return;
            const duration = Math.round((lastKnownTime - sectionStart) * 1000) / 1000;
            if (duration < 1.5) return;
            navigator.sendBeacon(
                `/api/interact/viewing/add/${hash}`,
                new Blob([JSON.stringify({
                    time_start:   Math.round(sectionStart * 1000) / 1000,
                    duration_sec: duration,
                })], { type: 'application/json' })
            );
        };

        videoEl.addEventListener('timeupdate',  onTimeUpdate);
        videoEl.addEventListener('play',        onPlay);
        videoEl.addEventListener('pause',       onPause);
        videoEl.addEventListener('seeking',     onSeeking);
        videoEl.addEventListener('seeked',      onSeeked);
        videoEl.addEventListener('ended',       onEnded);
        window.addEventListener('beforeunload', onBeforeUnload);
    });

    onDestroy(() => {
        // Flush any in-progress section before the component unmounts (client-side navigation).
        if (sectionStart !== null && videoEl !== null) {
            submitSection(sectionStart, videoEl.currentTime);
            sectionStart = null;
        }
        if (videoEl) {
            if (onTimeUpdate)   videoEl.removeEventListener('timeupdate',  onTimeUpdate);
            if (onPlay)         videoEl.removeEventListener('play',        onPlay);
            if (onPause)        videoEl.removeEventListener('pause',       onPause);
            if (onSeeking)      videoEl.removeEventListener('seeking',     onSeeking);
            if (onSeeked)       videoEl.removeEventListener('seeked',      onSeeked);
            if (onEnded)        videoEl.removeEventListener('ended',       onEnded);
        }
        if (onBeforeUnload) window.removeEventListener('beforeunload', onBeforeUnload);
        if (seekThumbsVisibilityHandler) {
            document.removeEventListener('visibilitychange', seekThumbsVisibilityHandler);
            seekThumbsVisibilityHandler = undefined;
        }
        if (subsVttUrl) { URL.revokeObjectURL(subsVttUrl); subsVttUrl = null; }
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
