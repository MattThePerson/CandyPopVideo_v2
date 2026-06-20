<script lang="ts">
    import { onMount } from 'svelte';
    import { globalFilter, type GlobalFilter } from '../../lib/stores/globalFilter.svelte';
    import FuzzyCombobox from '../../lib/components/FuzzyCombobox.svelte';
    import type { Catalogue } from '../catalogue/types';

    /* Props */
    let { disabled = false }: { disabled?: boolean } = $props();

    let catalogue = $state<Catalogue | null>(null);
    let loading   = $state(true);

    // Draft state — uncommitted until Apply is clicked
    let draftCollection = $state(globalFilter.current.collection);
    let draftStudio     = $state(globalFilter.current.studio);
    let draftActors     = $state<string[]>([...globalFilter.current.actors]);

    // Actor combobox
    let actorSearch    = $state('');
    let highlightedIdx = $state(0);
    let dropdownOpen   = $state(false);

    let isDirty = $derived(
        draftCollection !== globalFilter.current.collection ||
        draftStudio     !== globalFilter.current.studio     ||
        JSON.stringify([...draftActors].sort()) !== JSON.stringify([...globalFilter.current.actors].sort())
    );

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
                draftCollection = f.collection ?? '';
                draftStudio     = f.studio     ?? '';
                draftActors     = [...(f.actors ?? [])];
            }
        } finally {
            loading = false;
        }
    });

    // Score a fuzzy match. Returns -1 if no match.
    function fuzzyScore(query: string, target: string): number {
        const q = query.toLowerCase();
        const t = target.toLowerCase();
        if (t.startsWith(q)) return 1000 - t.length;
        let score = 0, qi = 0, lastHit = -1;
        for (let ti = 0; ti < t.length && qi < q.length; ti++) {
            if (t[ti] === q[qi]) { score += (ti === lastHit + 1) ? 3 : 1; lastHit = ti; qi++; }
        }
        return qi === q.length ? score : -1;
    }

    let sortedCollections = $derived((catalogue?.collection_info ?? []).map(i => i.name).sort((a, b) => a.localeCompare(b)));
    let sortedStudios     = $derived((catalogue?.studio_info     ?? []).map(i => i.name).sort((a, b) => a.localeCompare(b)));
    let sortedActors      = $derived((catalogue?.actor_info      ?? []).map(i => i.name).sort((a, b) => a.localeCompare(b)));

    let filteredActors = $derived((() => {
        const q    = actorSearch.trim();
        const pool = sortedActors.filter(a => !draftActors.includes(a));
        if (!q) return pool.slice(0, 8);
        return pool
            .map(a => ({ name: a, score: fuzzyScore(q, a) }))
            .filter(x => x.score >= 0)
            .sort((a, b) => b.score - a.score)
            .map(x => x.name)
            .slice(0, 10);
    })());

    $effect(() => { filteredActors; highlightedIdx = 0; });

    function commitActor(name: string) {
        if (name && !draftActors.includes(name)) draftActors = [...draftActors, name];
        actorSearch  = '';
        dropdownOpen = false;
    }

    function removeActor(name: string) { draftActors = draftActors.filter(a => a !== name); }

    function handleActorKeydown(e: KeyboardEvent) {
        if (!dropdownOpen || filteredActors.length === 0) return;
        if      (e.key === 'ArrowDown') { highlightedIdx = Math.min(highlightedIdx + 1, filteredActors.length - 1); e.preventDefault(); }
        else if (e.key === 'ArrowUp')   { highlightedIdx = Math.max(highlightedIdx - 1, 0);                         e.preventDefault(); }
        else if (e.key === 'Enter')     { commitActor(filteredActors[highlightedIdx]); e.preventDefault(); }
        else if (e.key === 'Escape')    { dropdownOpen = false; }
    }

    async function apply() {
        const f: GlobalFilter = { collection: draftCollection, studio: draftStudio, actors: draftActors };
        const res = await fetch('/api/global-filter', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(f),
        });
        if (res.ok) globalFilter.set(f);
    }

    async function clear() {
        draftCollection = ''; draftStudio = ''; draftActors = [];
        await fetch('/api/global-filter', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ collection: '', studio: '', actors: [] }),
        });
        globalFilter.clear();
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

    <p class="card-desc">
        Limits results site-wide — search, recommendations, random video.
        {#if globalFilter.isActive}<span class="active-hint"> Filter is active.</span>{/if}
    </p>

    {#if loading}
        <p class="card-desc">Loading catalogue…</p>
    {:else if catalogue}
        <div class="fields">
            <label class="field-label" for="cf-collection">Collection</label>
            <FuzzyCombobox id="cf-collection" items={sortedCollections} bind:value={draftCollection} placeholder="All collections" {disabled} />

            <label class="field-label" for="cf-studio">Studio / Line</label>
            <FuzzyCombobox id="cf-studio" items={sortedStudios} bind:value={draftStudio} placeholder="All studios" {disabled} />

            <!-- Performers: fuzzy combobox (multi) -->
            <label class="field-label" for="cf-actors">Performers</label>
            <div class="combobox">
                <input
                    id="cf-actors"
                    class="ctrl"
                    type="text"
                    placeholder="Type to search performers…"
                    autocomplete="off"
                    bind:value={actorSearch}
                    onfocus={() => dropdownOpen = true}
                    onblur={() => setTimeout(() => { dropdownOpen = false; }, 150)}
                    oninput={() => { dropdownOpen = true; }}
                    onkeydown={handleActorKeydown}
                    {disabled}
                />
                {#if dropdownOpen && filteredActors.length > 0}
                    <ul class="dropdown" role="listbox">
                        {#each filteredActors as actor, i}
                            <!-- svelte-ignore a11y_no_static_element_interactions -->
                            <li
                                class="dropdown-item"
                                class:hl={i === highlightedIdx}
                                role="option"
                                aria-selected={i === highlightedIdx}
                                onmousedown={() => commitActor(actor)}
                                onmouseover={() => highlightedIdx = i}
                            >{actor}</li>
                        {/each}
                    </ul>
                {/if}
            </div>
            {#if draftActors.length > 0}
                <div class="chips">
                    {#each draftActors as a}
                        <span class="chip">
                            {a}
                            <button class="chip-x" onclick={() => removeActor(a)} aria-label="Remove {a}">×</button>
                        </span>
                    {/each}
                </div>
            {/if}
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

    .card-desc   { font-size: 0.82rem; color: #666; margin: 0; line-height: 1.5; }
    .active-hint { color: #01b8b8; }
    .warn-text   { color: #9a6020; }

    .fields { display: flex; flex-direction: column; gap: 0.4rem; }
    .field-label {
        font-size: 0.72rem; color: #555; letter-spacing: 0.05em;
        text-transform: uppercase; margin-top: 0.3rem;
    }

    /* Actor combobox (multi-select variant, inline) */
    .combobox { position: relative; }

    .ctrl {
        background: #060a0a;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 5px; color: #ccc; font-size: 0.82rem;
        padding: 0.42rem 0.7rem; outline: none; width: 100%;
        box-sizing: border-box;
    }
    .ctrl:focus    { border-color: rgba(1, 184, 184, 0.5); }
    .ctrl:disabled { opacity: 0.4; cursor: not-allowed; }

    .dropdown {
        position: absolute; top: calc(100% + 3px); left: 0; right: 0; z-index: 50;
        background: #0a1010; border: 1px solid rgba(1, 184, 184, 0.25);
        border-radius: 5px; margin: 0; padding: 0.2rem 0;
        list-style: none; max-height: 200px; overflow-y: auto;
        box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    }
    .dropdown-item {
        padding: 0.38rem 0.75rem; font-size: 0.82rem; color: #bbb; cursor: pointer;
    }
    .dropdown-item.hl,
    .dropdown-item:hover { background: rgba(1, 184, 184, 0.12); color: #e0e0e0; }

    .chips { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.35rem; }
    .chip {
        display: inline-flex; align-items: center; gap: 0.3rem;
        font-size: 0.78rem; color: #bbb;
        background: rgba(1, 184, 184, 0.08); border: 1px solid rgba(1, 184, 184, 0.2);
        border-radius: 4px; padding: 0.15rem 0.5rem 0.15rem 0.6rem;
    }
    .chip-x {
        background: none; border: none; color: #555; cursor: pointer;
        font-size: 0.9rem; line-height: 1; padding: 0; transition: color 0.1s;
    }
    .chip-x:hover { color: #ccc; }

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
