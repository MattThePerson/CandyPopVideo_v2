<script lang="ts">
    import { onMount } from 'svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import type { ViewingRow } from './types';

    const DAYS       = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const HOUR_LABELS = Array.from({ length: 24 }, (_, i) => {
        if (i === 0)  return '12a';
        if (i === 12) return '12p';
        return i < 12 ? `${i}a` : `${i - 12}p`;
    });

    let loading      = $state(true);
    let error        = $state<string | null>(null);
    let grid         = $state<number[][]>(Array.from({ length: 7 }, () => new Array(24).fill(0)));
    let maxSec       = $state(1);
    let totalSec     = $state(0);
    let peakHour     = $state(0);
    let peakDay      = $state(0);
    let hovered      = $state<{ dow: number; hour: number } | null>(null);

    function cellColor(sec: number): string {
        if (sec === 0) return '#111';
        const t = Math.sqrt(sec / maxSec);
        const r = Math.round(28 + t * (204 - 28));
        const g = Math.round(28 + t * (105 - 28));
        const b = Math.round(28 + t * (179 - 28));
        return `rgb(${r},${g},${b})`;
    }

    function fmtSec(s: number): string {
        if (s < 60)  return `${Math.round(s)}s`;
        const m = Math.floor(s / 60);
        if (m >= 60) return `${Math.floor(m / 60)}h ${m % 60}m`;
        return `${m}m`;
    }

    onMount(async () => {
        try {
            const rows: ViewingRow[] = await fetch('/api/interact/viewings?limit=1000').then(r => r.json());
            const g = Array.from({ length: 7 }, () => new Array(24).fill(0));
            let total = 0;
            for (const v of rows) {
                const dt = new Date(v.datetime);
                g[dt.getDay()][dt.getHours()] += v.duration_sec;
                total += v.duration_sec;
            }
            grid    = g;
            maxSec  = Math.max(...g.flat(), 1);
            totalSec = total;
            // find peak hour (column sum) and peak day (row sum)
            let maxCol = 0, maxRow = 0;
            for (let h = 0; h < 24; h++) {
                const col = g.reduce((s, r) => s + r[h], 0);
                if (col > maxCol) { maxCol = col; peakHour = h; }
            }
            for (let d = 0; d < 7; d++) {
                const row = g[d].reduce((a, b) => a + b, 0);
                if (row > maxRow) { maxRow = row; peakDay = d; }
            }
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
{:else}
    <div class="clock-page">

        <div class="stats-row">
            <div class="stat">
                <div class="stat-val">{fmtSec(totalSec)}</div>
                <div class="stat-lbl">total recorded</div>
            </div>
            {#if totalSec > 0}
                <div class="stat">
                    <div class="stat-val">{DAYS[peakDay]}s</div>
                    <div class="stat-lbl">busiest day</div>
                </div>
                <div class="stat">
                    <div class="stat-val">{HOUR_LABELS[peakHour]}</div>
                    <div class="stat-lbl">busiest hour</div>
                </div>
            {/if}
        </div>

        <div class="grid-wrap">
            <!-- Hour column headers (every 3h) -->
            <div class="header-row">
                <div class="day-spacer"></div>
                {#each { length: 24 } as _, h}
                    <div class="hour-lbl">{h % 3 === 0 ? HOUR_LABELS[h] : ''}</div>
                {/each}
            </div>

            <!-- Day rows -->
            {#each { length: 7 } as _, dow}
                <div class="day-row">
                    <div class="day-lbl">{DAYS[dow]}</div>
                    {#each { length: 24 } as _, hour}
                        {@const sec = grid[dow][hour]}
                        <div
                            class="cell"
                            class:peak={sec === maxSec && sec > 0}
                            style="background:{cellColor(sec)}"
                            onmouseenter={() => hovered = { dow, hour }}
                            onmouseleave={() => hovered = null}
                            role="gridcell"
                            tabindex="-1"
                            aria-label="{DAYS[dow]} {HOUR_LABELS[hour]}: {fmtSec(sec)}"
                        ></div>
                    {/each}
                </div>
            {/each}

            <!-- Hover status bar -->
            <div class="status-bar" class:visible={!!hovered}>
                {#if hovered}
                    <strong>{DAYS[hovered.dow]}</strong>
                    {HOUR_LABELS[hovered.hour]}–{HOUR_LABELS[(hovered.hour + 1) % 24]}
                    · {fmtSec(grid[hovered.dow][hovered.hour])} watched
                {:else}
                    &nbsp;
                {/if}
            </div>

            <div class="legend">
                <span>less</span>
                <div class="legend-grad"></div>
                <span>more</span>
            </div>
        </div>

    </div>
{/if}

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .clock-page { display: flex; flex-direction: column; gap: 2.5rem; }

    .stats-row { display: flex; gap: 3rem; flex-wrap: wrap; }

    .stat-val {
        font-family: 'Jaro';
        font-size: 2rem;
        color: #ddd;
        line-height: 1;
    }
    .stat-lbl {
        font-size: 0.7rem;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-family: 'Inter', sans-serif;
        margin-top: 4px;
    }

    .grid-wrap { display: flex; flex-direction: column; gap: 3px; overflow-x: auto; padding-bottom: 4px; }

    .header-row, .day-row {
        display: flex;
        gap: 3px;
        align-items: center;
    }

    .day-spacer, .day-lbl {
        width: 34px;
        flex-shrink: 0;
    }
    .day-lbl {
        font-size: 0.68rem;
        color: #555;
        text-align: right;
        padding-right: 6px;
        font-family: 'Inter', sans-serif;
    }

    .hour-lbl {
        width: 30px;
        font-size: 0.58rem;
        color: #444;
        text-align: center;
        font-family: 'Inter', sans-serif;
        flex-shrink: 0;
    }

    .cell {
        width: 30px;
        height: 30px;
        border-radius: 4px;
        flex-shrink: 0;
        cursor: pointer;
        transition: transform 0.1s, filter 0.1s;
    }
    .cell:hover { transform: scale(1.3); filter: brightness(1.35); z-index: 5; position: relative; }
    .cell.peak  { box-shadow: 0 0 8px rgba(204, 105, 179, 0.6); }

    .status-bar {
        height: 20px;
        margin-top: 0.5rem;
        font-size: 0.8rem;
        color: #777;
        font-family: 'Inter', sans-serif;
        opacity: 0;
        transition: opacity 0.12s;
    }
    .status-bar.visible { opacity: 1; }
    .status-bar strong  { color: rgb(204, 105, 179); }

    .legend {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.68rem;
        color: #444;
        font-family: 'Inter', sans-serif;
        margin-top: 0.25rem;
    }
    .legend-grad {
        width: 100px;
        height: 10px;
        border-radius: 5px;
        background: linear-gradient(90deg, #111, rgb(204, 105, 179));
    }
</style>
