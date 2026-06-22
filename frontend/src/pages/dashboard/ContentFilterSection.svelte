<script lang="ts">
    import { onMount } from 'svelte';
    import { globalFilter, type GlobalFilter } from '../../lib/stores/globalFilter.svelte';
    import MultiCombobox from '../../lib/components/MultiCombobox.svelte';
    import type { Catalogue } from '../catalogue/types';

    /* Props */
    let { disabled = false }: { disabled?: boolean } = $props();

    let catalogue = $state<Catalogue | null>(null);
    let loading   = $state(true);

    // Draft state — uncommitted until Apply is clicked
    let collInclude   = $state<string[]>([]);
    let collExclude   = $state<string[]>([]);
    let collMode      = $state<'include' | 'exclude'>('include');
    let studioInclude = $state<string[]>([]);
    let studioExclude = $state<string[]>([]);
    let studioMode    = $state<'include' | 'exclude'>('include');
    let actorsInclude = $state<string[]>([]);
    let actorsExclude = $state<string[]>([]);

    // Dirty-checking via snapshots
    type Snap = { ci: string[]; ce: string[]; cm: string; si: string[]; se: string[]; sm: string; ai: string[]; ae: string[] };
    function snap(): Snap { return { ci: [...collInclude], ce: [...collExclude], cm: collMode, si: [...studioInclude], se: [...studioExclude], sm: studioMode, ai: [...actorsInclude], ae: [...actorsExclude] }; }
    const eqArr  = (a: string[], b: string[]) => JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
    const snapEq = (a: Snap, b: Snap) => eqArr(a.ci, b.ci) && eqArr(a.ce, b.ce) && a.cm === b.cm && eqArr(a.si, b.si) && eqArr(a.se, b.se) && a.sm === b.sm && eqArr(a.ai, b.ai) && eqArr(a.ae, b.ae);

    let applied = $state<Snap>({ ci: [], ce: [], cm: 'include', si: [], se: [], sm: 'include', ai: [], ae: [] });
    let isDirty = $derived.by(() => !snapEq(snap(), applied));

    let sortedCollections = $derived((catalogue?.collection_info ?? []).map(i => i.name).sort((a, b) => a.localeCompare(b)));
    let sortedStudios     = $derived((catalogue?.studio_info     ?? []).map(i => i.name).sort((a, b) => a.localeCompare(b)));
    let sortedActors      = $derived((catalogue?.actor_info      ?? []).map(i => i.name).sort((a, b) => a.localeCompare(b)));

    onMount(async () => {
        try {
            const [catRes, filterRes] = await Promise.all([
                fetch('/api/query/get/catalogue', {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:    JSON.stringify({
                        query_type: '', query_string: '', use_primary_actors: false,
                        filter_actor: '', filter_studio: '', filter_collection: '', filter_tag: '',
                    }),
                }),
                fetch('/api/global-filter'),
            ]);
            catalogue = await catRes.json();
            if (filterRes.ok) {
                const f: GlobalFilter = await filterRes.json();
                globalFilter.set(f);
                collInclude   = [...(f.collections_include ?? [])];
                collExclude   = [...(f.collections_exclude ?? [])];
                collMode      = (f.collections_mode as 'include' | 'exclude') || 'include';
                studioInclude = [...(f.studios_include ?? [])];
                studioExclude = [...(f.studios_exclude ?? [])];
                studioMode    = (f.studios_mode as 'include' | 'exclude') || 'include';
                actorsInclude = [...(f.actors_include ?? [])];
                actorsExclude = [...(f.actors_exclude ?? [])];
                applied = snap();
            }
        } finally {
            loading = false;
        }
    });

    async function apply() {
        const f: GlobalFilter = {
            collections_include: collInclude, collections_exclude: collExclude, collections_mode: collMode,
            studios_include:     studioInclude, studios_exclude: studioExclude, studios_mode: studioMode,
            actors_include:      actorsInclude, actors_exclude: actorsExclude,
        };
        const res = await fetch('/api/global-filter', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(f),
        });
        if (res.ok) { globalFilter.set(f); applied = snap(); }
    }

    async function clear() {
        collInclude = []; collExclude = []; collMode = 'include';
        studioInclude = []; studioExclude = []; studioMode = 'include';
        actorsInclude = []; actorsExclude = [];
        const empty: GlobalFilter = {
            collections_include: [], collections_exclude: [], collections_mode: 'include',
            studios_include:     [], studios_exclude:     [], studios_mode:     'include',
            actors_include:      [], actors_exclude:      [],
        };
        await fetch('/api/global-filter', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(empty),
        });
        globalFilter.clear();
        applied = snap();
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<section class="card" class:active={globalFilter.isActive}>
    <div class="title-row">
        <h2 class="section-title">Content Filter</h2>
        {#if globalFilter.isActive}<span class="active-badge">ACTIVE</span>{/if}
    </div>

    <p class="card-desc">Limits results site-wide — search, recommendations, random video.</p>

    {#if loading}
        <p class="card-desc">Loading catalogue…</p>
    {:else if catalogue}
        <div class="filters">

            <!-- Collections -->
            <div class="row-label">Collections</div>
            <div class="filter-row">
                <MultiCombobox items={sortedCollections} bind:value={collInclude}
                    placeholder="Include…" dimmed={collMode === 'exclude'} exclude={collExclude} {disabled} />
                <button class="mode-pill" onclick={() => collMode = collMode === 'include' ? 'exclude' : 'include'}
                    disabled={disabled}>
                    <span class:active={collMode === 'include'}>INCL</span>
                    <span class:active={collMode === 'exclude'}>EXCL</span>
                </button>
                <MultiCombobox items={sortedCollections} bind:value={collExclude}
                    placeholder="Exclude…" dimmed={collMode === 'include'} exclude={collInclude} {disabled} />
            </div>

            <!-- Studios -->
            <div class="row-label">Studios</div>
            <div class="filter-row">
                <MultiCombobox items={sortedStudios} bind:value={studioInclude}
                    placeholder="Include…" dimmed={studioMode === 'exclude'} exclude={studioExclude} {disabled} />
                <button class="mode-pill" onclick={() => studioMode = studioMode === 'include' ? 'exclude' : 'include'}
                    disabled={disabled}>
                    <span class:active={studioMode === 'include'}>INCL</span>
                    <span class:active={studioMode === 'exclude'}>EXCL</span>
                </button>
                <MultiCombobox items={sortedStudios} bind:value={studioExclude}
                    placeholder="Exclude…" dimmed={studioMode === 'include'} exclude={studioInclude} {disabled} />
            </div>

            <!-- Actors -->
            <div class="row-label">Actors</div>
            <div class="performers-row">
                <div>
                    <div class="col-label">INCLUDE</div>
                    <MultiCombobox items={sortedActors} bind:value={actorsInclude}
                        placeholder="Include actors…" exclude={actorsExclude} {disabled} />
                </div>
                <!-- invisible spacer — same dimensions as .mode-pill to align columns with rows above -->
                <div class="pill-spacer" aria-hidden="true"><span>INCL</span><span>EXCL</span></div>
                <div>
                    <div class="col-label">EXCLUDE</div>
                    <MultiCombobox items={sortedActors} bind:value={actorsExclude}
                        placeholder="Exclude actors…" exclude={actorsInclude} {disabled} />
                </div>
            </div>

        </div>

        <div class="actions">
            <button class="btn-primary" onclick={apply} disabled={disabled || !isDirty}>Apply Filter</button>
            {#if globalFilter.isActive}
                <button class="btn-secondary" onclick={clear} {disabled}>Clear</button>
            {/if}
        </div>
    {:else}
        <p class="card-desc warn-text">Failed to load catalogue.</p>
    {/if}
</section>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .card {
        background: #0d1212;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px; padding: 1.2rem 1.4rem;
        display: flex; flex-direction: column; gap: 0.75rem;
        transition: border-color 0.2s;
    }
    .card.active { border-color: rgba(1, 184, 184, 0.35); }

    .title-row { display: flex; align-items: center; gap: 0.6rem; }
    .section-title {
        font-size: 0.68rem; letter-spacing: 0.13em;
        text-transform: uppercase; color: #555; font-weight: 600; margin: 0;
    }
    .active-badge {
        font-size: 0.58rem; letter-spacing: 0.1em; text-transform: uppercase;
        background: rgba(1, 184, 184, 0.15); color: #01b8b8;
        border: 1px solid rgba(1, 184, 184, 0.3);
        border-radius: 3px; padding: 0.1rem 0.4rem; font-weight: 600;
    }

    .card-desc { font-size: 0.82rem; color: #666; margin: 0; line-height: 1.5; }
    .warn-text { color: #9a6020; }

    .filters { display: flex; flex-direction: column; gap: 0.4rem; }

    .row-label {
        font-size: 0.72rem; color: #555; letter-spacing: 0.05em;
        text-transform: uppercase; margin-top: 0.4rem;
    }
    .col-label {
        font-size: 0.62rem; color: #444; letter-spacing: 0.08em;
        text-transform: uppercase; margin-bottom: 0.3rem;
    }

    .filter-row {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 0.75rem;
        align-items: start;
    }
    .performers-row {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 0.75rem;
        align-items: start;
    }

    /* Toggle pill — sits between include/exclude columns */
    .mode-pill {
        margin-top: 0.38rem;
        display: flex;
        background: #070c0c;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 0;
        cursor: pointer;
        transition: border-color 0.15s;
    }
    .mode-pill:hover:not(:disabled) { border-color: rgba(1, 184, 184, 0.3); }
    .mode-pill:disabled { opacity: 0.35; cursor: not-allowed; }
    .mode-pill span {
        font-size: 0.62rem; letter-spacing: 0.08em; font-weight: 600;
        padding: 0.28rem 0.45rem; color: #3a3a3a;
        border-radius: 3px; transition: color 0.15s, background 0.15s;
        user-select: none;
    }
    .mode-pill span:first-child.active { color: #01b8b8; background: rgba(1, 184, 184, 0.15); }
    .mode-pill span:last-child.active  { color: #c04848; background: rgba(192, 72, 72, 0.12); }
    .pill-spacer {
        margin-top: 0.38rem; display: flex; visibility: hidden; pointer-events: none;
        border: 1px solid transparent; border-radius: 4px; padding: 0;
    }
    .pill-spacer span { font-size: 0.62rem; letter-spacing: 0.08em; font-weight: 600; padding: 0.28rem 0.45rem; }

    .actions { display: flex; gap: 0.6rem; align-items: center; margin-top: 0.15rem; }

    .btn-primary {
        background: #01b8b8; color: #000; font-weight: 700; font-size: 0.85rem;
        border: none; border-radius: 5px; padding: 0.5rem 1.2rem;
        cursor: pointer; transition: background 0.15s;
    }
    .btn-primary:hover:not(:disabled) { background: #00d0d0; }
    .btn-primary:disabled { opacity: 0.35; cursor: not-allowed; }

    .btn-secondary {
        background: transparent; border: 1px solid rgba(255, 255, 255, 0.15);
        color: #aaa; font-size: 0.83rem; border-radius: 5px;
        padding: 0.45rem 1rem; cursor: pointer; transition: border-color 0.15s, color 0.15s;
    }
    .btn-secondary:hover:not(:disabled) { border-color: rgba(255,255,255,0.35); color: #ddd; }
    .btn-secondary:disabled { opacity: 0.35; cursor: not-allowed; }
</style>
