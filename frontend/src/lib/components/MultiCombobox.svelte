<script lang="ts">
    /* Props */
    let {
        items       = [] as string[],
        value       = $bindable([] as string[]),
        placeholder = 'Search…',
        disabled    = false,
        dimmed      = false,
        exclude     = [] as string[],
        variant     = 'default' as 'default' | 'exclude',
    }: {
        items?:       string[];
        value?:       string[];
        placeholder?: string;
        disabled?:    boolean;
        dimmed?:      boolean;
        exclude?:     string[];
        variant?:     'default' | 'exclude';
    } = $props();

    let searchText     = $state('');
    let dropdownOpen   = $state(false);
    let highlightedIdx = $state(0);

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

    let filtered = $derived((() => {
        const q    = searchText.trim();
        const skip = new Set([...value, ...exclude]);
        const pool = items.filter(i => !skip.has(i));
        if (!q) return pool;
        return pool
            .map(i => ({ name: i, score: fuzzyScore(q, i) }))
            .filter(x => x.score >= 0)
            .sort((a, b) => b.score - a.score)
            .map(x => x.name);
    })());

    $effect(() => { filtered; highlightedIdx = 0; });

    function commit(name: string) {
        if (!value.includes(name)) value = [...value, name];
        searchText   = '';
        dropdownOpen = false;
    }

    function remove(name: string) { value = value.filter(v => v !== name); }

    function handleKeydown(e: KeyboardEvent) {
        if (!dropdownOpen || filtered.length === 0) return;
        if      (e.key === 'ArrowDown') { highlightedIdx = Math.min(highlightedIdx + 1, filtered.length - 1); e.preventDefault(); }
        else if (e.key === 'ArrowUp')   { highlightedIdx = Math.max(highlightedIdx - 1, 0);                   e.preventDefault(); }
        else if (e.key === 'Enter')     { commit(filtered[highlightedIdx]); e.preventDefault(); }
        else if (e.key === 'Escape')    { dropdownOpen = false; }
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="wrap" class:dimmed>
    <div class="combobox">
        <input
            class="ctrl"
            type="text"
            {placeholder}
            autocomplete="off"
            bind:value={searchText}
            onfocus={() => dropdownOpen = true}
            onblur={() => setTimeout(() => { dropdownOpen = false; }, 150)}
            oninput={() => { dropdownOpen = true; }}
            onkeydown={handleKeydown}
            {disabled}
        />
        {#if dropdownOpen && filtered.length > 0}
            <ul class="dropdown" role="listbox">
                {#each filtered as item, i}
                    <!-- svelte-ignore a11y_no_static_element_interactions a11y_mouse_events_have_key_events -->
                    <li
                        class="dropdown-item"
                        class:hl={i === highlightedIdx}
                        role="option"
                        aria-selected={i === highlightedIdx}
                        onmousedown={() => commit(item)}
                        onmouseover={() => highlightedIdx = i}
                    >{item}</li>
                {/each}
            </ul>
        {/if}
    </div>
    {#if value.length > 0}
        <div class="chips">
            {#each value as v}
                <span class="chip" class:exclude={variant === 'exclude'}>
                    {v}
                    <button class="chip-x" onclick={() => remove(v)} aria-label="Remove {v}">×</button>
                </span>
            {/each}
        </div>
    {/if}
</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    /* Apply dimming to children only — avoids creating a stacking context on .wrap,
       which would trap the dropdown's z-index and put it beneath sibling columns. */
    .wrap.dimmed .ctrl  { opacity: 0.35; }
    .wrap.dimmed .chips { opacity: 0.35; }

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
        list-style: none; max-height: 360px; overflow-y: auto;
        box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    }
    .dropdown-item { padding: 0.38rem 0.75rem; font-size: 0.82rem; color: #bbb; cursor: pointer; }
    .dropdown-item.hl,
    .dropdown-item:hover { background: rgba(1, 184, 184, 0.12); color: #e0e0e0; }

    .chips { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.35rem; }
    .chip {
        display: inline-flex; align-items: center; gap: 0.3rem;
        font-size: 0.78rem; color: #bbb;
        background: rgba(1, 184, 184, 0.08); border: 1px solid rgba(1, 184, 184, 0.2);
        border-radius: 4px; padding: 0.15rem 0.5rem 0.15rem 0.6rem;
    }
    .chip.exclude {
        background: rgba(192, 72, 72, 0.1);
        border-color: rgba(192, 72, 72, 0.28);
        color: #c08888;
    }
    .chip-x {
        background: none; border: none; color: #555; cursor: pointer;
        font-size: 0.9rem; line-height: 1; padding: 0; transition: color 0.1s;
    }
    .chip-x:hover { color: #ccc; }
    .chip.exclude .chip-x:hover { color: #e0a0a0; }
</style>
