<script lang="ts">
    import { onMount } from 'svelte';
    import { navigate } from '$lib/router/router.svelte';
    import type { VideoData } from '$lib/types/video';
    import Spinner from '$lib/components/Spinner.svelte';
    import type { ViewingRow, ViewingSession } from './types';

    type EnrichedSession = ViewingSession & { video?: VideoData };

    let loading = $state(true);
    let error   = $state<string | null>(null);
    let groups  = $state<{ date: string; sessions: EnrichedSession[] }[]>([]);

    const SESSION_GAP_MS = 30 * 60 * 1000;

    function buildSessions(rows: ViewingRow[]): ViewingSession[] {
        const sorted = [...rows].sort((a, b) =>
            new Date(a.datetime).getTime() - new Date(b.datetime).getTime()
        );
        const out: ViewingSession[] = [];
        let cur: ViewingSession | null = null;
        for (const v of sorted) {
            const dt = new Date(v.datetime);
            if (cur && cur.video_hash === v.video_hash &&
                dt.getTime() - cur.start_dt.getTime() < SESSION_GAP_MS
            ) {
                cur.segments.push(v);
                cur.total_sec += v.duration_sec;
            } else {
                if (cur) out.push(cur);
                cur = { video_hash: v.video_hash, start_dt: dt, total_sec: v.duration_sec, segments: [v] };
            }
        }
        if (cur) out.push(cur);
        return out.reverse();
    }

    function groupByDate(sessions: ViewingSession[]) {
        const m = new Map<string, ViewingSession[]>();
        for (const s of sessions) {
            const key = s.start_dt.toLocaleDateString('en-US', {
                weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
            });
            if (!m.has(key)) m.set(key, []);
            m.get(key)!.push(s);
        }
        return m;
    }

    function fmtDuration(sec: number): string {
        if (sec < 60)  return `${Math.round(sec)}s`;
        const m = Math.floor(sec / 60);
        if (m >= 60)   return `${Math.floor(m / 60)}h ${m % 60}m`;
        return `${m}m`;
    }

    function fmtTime(dt: Date): string {
        return dt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    }

    function getTitle(v?: VideoData): string {
        return v ? (v.scene_title || v.title || v.filename) : '?';
    }

    function onCardEnter(e: MouseEvent) {
        const vid = (e.currentTarget as HTMLElement).querySelector('video');
        if (vid) { vid.currentTime = 0; vid.play().catch(() => {}); }
    }

    function onCardLeave(e: MouseEvent) {
        const vid = (e.currentTarget as HTMLElement).querySelector('video');
        if (vid) { vid.pause(); vid.currentTime = 0; }
    }

    onMount(async () => {
        try {
            const rows: ViewingRow[] = await fetch('/api/interact/viewings?limit=500').then(r => r.json());
            const sessions = buildSessions(rows);
            const hashes = [...new Set(sessions.map(s => s.video_hash))];
            const videoMap = new Map<string, VideoData>();
            await Promise.all(hashes.map(async h => {
                try { videoMap.set(h, await fetch(`/api/get/video-data/${h}`).then(r => r.json())); }
                catch { /* ignore */ }
            }));
            const byDate = groupByDate(sessions);
            groups = Array.from(byDate.entries()).map(([date, slist]) => ({
                date,
                sessions: slist.map(s => ({ ...s, video: videoMap.get(s.video_hash) })),
            }));
        } catch (e) {
            error = String(e);
        } finally {
            loading = false;
        }
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

{#if loading}
    <div class="flex justify-center py-20"><Spinner /></div>
{:else if error}
    <p class="text-red-400 p-8">{error}</p>
{:else if groups.length === 0}
    <div class="empty"><p>No viewing history yet.</p></div>
{:else}
    <div class="strip-page">
        {#each groups as group (group.date)}
            <section class="date-section">
                <div class="date-label">{group.date}</div>
                <div class="sprocket top"></div>
                <div class="film-row">
                    {#each group.sessions as session (session.start_dt.getTime())}
                        {@const title = getTitle(session.video)}
                        <div
                            class="frame"
                            onclick={() => navigate(`/video/${session.video_hash}`)}
                            onmouseenter={onCardEnter}
                            onmouseleave={onCardLeave}
                            role="button"
                            tabindex="0"
                            onkeydown={(e) => e.key === 'Enter' && navigate(`/video/${session.video_hash}`)}
                            aria-label="{title} — {fmtDuration(session.total_sec)} watched"
                        >
                            <div class="card-media" style="--init: '{title[0].toUpperCase()}'">
                                <img
                                    src="/media/get/poster/{session.video_hash}"
                                    alt=""
                                    class="poster"
                                />
                                <!-- Progressive enhancement: teaser plays on hover if it exists -->
                                <video
                                    src="/static/preview-media/0x{session.video_hash}/teaser_small.mp4"
                                    muted
                                    loop
                                    preload="none"
                                    class="teaser"
                                    onerror={(e) => { (e.currentTarget as HTMLVideoElement).style.display = 'none'; }}
                                ></video>
                                <div class="card-info">
                                    <div class="card-title">{title}</div>
                                    <div class="card-meta">
                                        <span class="dur">{fmtDuration(session.total_sec)}</span>
                                        <span class="time">{fmtTime(session.start_dt)}</span>
                                    </div>
                                </div>
                                {#if session.segments.length > 1}
                                    <div class="seg-badge">{session.segments.length} clips</div>
                                {/if}
                            </div>
                        </div>
                    {/each}
                </div>
                <div class="sprocket bottom"></div>
            </section>
        {/each}
    </div>
{/if}

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .strip-page { display: flex; flex-direction: column; gap: 2.5rem; }

    .date-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #3a3a3a;
        margin-bottom: 0.4rem;
    }

    /* Film perforations — dark rectangles punched through the strip */
    .sprocket {
        height: 16px;
        background: repeating-linear-gradient(
            90deg,
            #181818 0, #181818 10px,
            #060a0a 10px, #060a0a 22px
        );
    }
    .sprocket.top    { border-radius: 5px 5px 0 0; }
    .sprocket.bottom { border-radius: 0 0 5px 5px; }

    .film-row {
        display: flex;
        gap: 3px;
        background: #141414;
        padding: 8px 10px;
        overflow-x: auto;
        scrollbar-width: thin;
        scrollbar-color: #252525 transparent;
        min-height: 234px;
        align-items: center;
    }

    .frame {
        flex-shrink: 0;
        cursor: pointer;
        border-radius: 3px;
        overflow: hidden;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        position: relative;
    }
    .frame:hover {
        transform: scale(1.07) translateY(-6px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
        z-index: 10;
    }

    .card-media {
        width: 148px;
        height: 208px;
        background: linear-gradient(145deg, #1a1030, #0d1826);
        position: relative;
        overflow: hidden;
    }

    /* Fallback initial letter shown when poster is missing */
    .card-media::before {
        content: var(--init, '?');
        position: absolute;
        top: 38%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-family: 'Jaro';
        font-size: 3.8rem;
        color: #232345;
        pointer-events: none;
    }

    .poster, .teaser {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .poster { z-index: 1; }
    .teaser { z-index: 2; opacity: 0; transition: opacity 0.3s; }
    .frame:hover .teaser { opacity: 1; }

    .card-info {
        position: absolute;
        bottom: 0; left: 0; right: 0;
        padding: 28px 7px 5px;
        background: linear-gradient(to top, rgba(0,0,0,0.92) 0%, transparent 100%);
        z-index: 3;
    }

    .card-title {
        font-size: 0.67rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #ddd;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 3px;
    }

    .card-meta {
        display: flex;
        justify-content: space-between;
        font-size: 0.58rem;
        font-family: 'Inter', sans-serif;
    }
    .dur  { color: rgb(204, 105, 179); }
    .time { color: #555; }

    .seg-badge {
        position: absolute;
        top: 6px;
        right: 6px;
        background: rgba(0, 0, 0, 0.72);
        color: #999;
        font-size: 0.58rem;
        font-family: 'Inter', sans-serif;
        padding: 2px 5px;
        border-radius: 3px;
        z-index: 4;
    }

    .empty { text-align: center; padding: 5rem; color: #555; }
</style>
