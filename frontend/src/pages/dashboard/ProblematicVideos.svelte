<script lang="ts">
    import { onMount } from 'svelte';

    interface VideoEntry {
        hash:       string;
        name:       string;
        value:      string;
        path:       string;
        parent_dir: string;
    }
    interface ProblematicData {
        vfr:           VideoEntry[];
        audio_codec:   VideoEntry[];
        pix_fmt_10bit: VideoEntry[];
        hevc:          VideoEntry[];
        hdr:           VideoEntry[];
    }

    const LABELS: Record<keyof ProblematicData, string> = {
        vfr:           'Variable Frame Rate',
        audio_codec:   'Unsupported Audio Codec',
        pix_fmt_10bit: '10-bit / 12-bit Pixel Format',
        hevc:          'HEVC (H.265)',
        hdr:           'HDR Color Transfer',
    };

    const MAX_SHOWN = 20;

    let data = $state<ProblematicData | null>(null);

    const groups    = $derived(data ? (Object.keys(LABELS) as (keyof ProblematicData)[]).filter(k => data![k].length > 0) : []);
    const hasIssues = $derived(groups.length > 0);

    onMount(async () => {
        data = await fetch('/api/dashboard/problematic-videos').then(r => r.json()).catch(() => null);
    });

    function copy(text: string) {
        navigator.clipboard.writeText(text).catch(() => {});
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

{#if hasIssues}
<section class="card warn-card">
    <h2 class="section-title">Potentially Problematic Videos</h2>

    {#each groups as key}
        {@const entries = data![key]}
        <details class="group">
            <summary class="group-header">
                <span class="group-label">{LABELS[key]}</span>
                <span class="group-count">{entries.length}</span>
            </summary>

            <ul class="entry-list">
                {#each entries.slice(0, MAX_SHOWN) as entry}
                    <li class="entry">
                        <span class="value-badge">{entry.value}</span>
                        <a href="/video/{entry.hash}" class="entry-link">{entry.name}</a>
                        <span class="spacer"></span>
                        <button class="copy-btn" onclick={() => copy(entry.path)}       title={entry.path}>path</button>
                        <button class="copy-btn" onclick={() => copy(entry.parent_dir)} title={entry.parent_dir}>dir</button>
                        <span class="hash-text">{entry.hash}</span>
                    </li>
                {/each}
                {#if entries.length > MAX_SHOWN}
                    <li class="more-note">…and {entries.length - MAX_SHOWN} more</li>
                {/if}
            </ul>
        </details>
    {/each}
</section>
{/if}

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .card {
        background: #0d1212;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 1.2rem 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    .warn-card { border-color: rgba(200, 136, 42, 0.2); }

    .section-title {
        font-size: 0.68rem; letter-spacing: 0.13em;
        text-transform: uppercase; color: #555; font-weight: 600; margin: 0;
    }

    .group { border-top: 1px solid rgba(255,255,255,0.04); padding-top: 0.6rem; }
    .group:first-of-type { border-top: none; padding-top: 0; }

    .group-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        list-style: none;
        user-select: none;
    }
    .group-header::-webkit-details-marker { display: none; }
    .group-label { font-size: 0.8rem; color: #9a6020; font-weight: 600; }
    .group-count {
        font-size: 0.7rem; color: #555;
        background: rgba(255,255,255,0.04);
        border-radius: 10px; padding: 0.1rem 0.45rem;
    }

    .entry-list {
        list-style: none; margin: 0.5rem 0 0; padding: 0 0 0 0.5rem;
        display: flex; flex-direction: column; gap: 0.5rem;
        border-left: 1px solid rgba(255,255,255,0.05);
    }

    .entry {
        display: flex; align-items: baseline; gap: 0.5rem;
        min-width: 0;
    }

    .value-badge {
        font-size: 0.65rem; color: #555;
        background: rgba(255,255,255,0.04);
        border-radius: 4px; padding: 0.1rem 0.35rem;
        white-space: nowrap; flex-shrink: 0;
    }

    .entry-link {
        font-size: 0.8rem; color: #888; text-decoration: none;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        min-width: 0; flex-shrink: 1;
    }
    .entry-link:hover { color: #bbb; text-decoration: underline; }

    .spacer { flex: 1; }

    .hash-text {
        font-size: 0.68rem; color: #3a3a3a;
        font-family: monospace; letter-spacing: 0.05em;
        flex-shrink: 0;
    }

    .copy-btn {
        font-size: 0.65rem; color: #444;
        background: none; border: 1px solid rgba(255,255,255,0.07);
        border-radius: 4px; padding: 0.1rem 0.4rem;
        cursor: pointer; transition: color 0.1s, border-color 0.1s;
    }
    .copy-btn:hover { color: #888; border-color: rgba(255,255,255,0.15); }

    .more-note { font-size: 0.72rem; color: #3a3a3a; padding: 0.1rem 0; }
</style>
