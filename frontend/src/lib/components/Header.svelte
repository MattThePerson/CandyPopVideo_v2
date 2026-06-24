<script lang="ts">
    import { routerState, navigate } from '../router/router.svelte';

    let configMenuOpen = $state(false);
    let scanDropOpen   = $state(false);
    let scanning       = $state(false);

    const pageLinks = [
        { href: '/', label: 'home' },
        { href: '/search', label: 'search' },
        { href: '/catalogue', label: 'catalogue' },
        { href: '/curated', label: 'curated' },
        { href: '/history', label: 'history' },
    ];

    function isActive(href: string) {
        return routerState.path === href;
    }

    function toggleConfigMenu() {
        configMenuOpen = !configMenuOpen;
    }

    // Closes dropdowns when the user clicks outside them.
    function handleWindowMouseDown(e: MouseEvent) {
        const target = e.target as Element;
        if (configMenuOpen) {
            if (!target.closest('#config-menu-button') && !target.closest('.config-menu'))
                configMenuOpen = false;
        }
        if (scanDropOpen) {
            if (!target.closest('.header-scan-split'))
                scanDropOpen = false;
        }
    }

    function goRandomVideo() {
        navigate('/video/random');
    }

    async function fireScan(novelOnly: boolean) {
        scanDropOpen = false;
        if (scanning) return;
        scanning = true;
        await fetch('/api/dashboard/run-scan', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ quick_scan: true, novel_files_only: novelOnly, read_json: true }),
        }).catch(() => null);
        setTimeout(() => { scanning = false; }, 2500);
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<svelte:window onmousedown={handleWindowMouseDown} />

<header>
    <nav class="flex justify-between px-[2.5%] bg-black border border-white/20 min-h-[3.1rem]">
        <span class="flex items-center justify-center gap-1">
            <a href="/" class="no-underline px-1">
                <span class="flex items-center gap-[0.2rem]">
                    <div class="logo-main">CandyPop</div>
                    <div class="logo-secondary">Video</div>
                </span>
            </a>
        </span>

        <span class="flex items-center justify-center gap-1">
            <span class="flex gap-[1px] translate-y-[2px]">
                {#each pageLinks as link (link.href)}
                    <a
                        href={link.href}
                        class="page-link px-2 py-[0.4rem] text-[1.15rem] font-medium text-[#ddd] no-underline hover:text-[#eee] hover:underline hover:decoration-dotted hover:decoration-gray-500"
                        class:active={isActive(link.href)}
                    >{link.label}</a>
                {/each}
            </span>

            <button type="button" class="icon-button" onclick={goRandomVideo} aria-label="Random video">
                <svg fill="#000000" width="32" height="32" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                    <path d="M504.971 359.029c9.373 9.373 9.373 24.569 0 33.941l-80 79.984c-15.01 15.01-40.971 4.49-40.971-16.971V416h-58.785a12.004 12.004 0 0 1-8.773-3.812l-70.556-75.596 53.333-57.143L352 336h32v-39.981c0-21.438 25.943-31.998 40.971-16.971l80 79.981zM12 176h84l52.781 56.551 53.333-57.143-70.556-75.596A11.999 11.999 0 0 0 122.785 96H12c-6.627 0-12 5.373-12 12v56c0 6.627 5.373 12 12 12zm372 0v39.984c0 21.46 25.961 31.98 40.971 16.971l80-79.984c9.373-9.373 9.373-24.569 0-33.941l-80-79.981C409.943 24.021 384 34.582 384 56.019V96h-58.785a12.004 12.004 0 0 0-8.773 3.812L96 336H12c-6.627 0-12 5.373-12 12v56c0 6.627 5.373 12 12 12h110.785c3.326 0 6.503-1.381 8.773-3.812L352 176h32z"/>
                </svg>
            </button>

            <a href="/search" class="icon-button" aria-label="Search">
                <svg fill="#000000" width="32" height="32" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M12.027 9.92L16 13.95 14 16l-4.075-3.976A6.465 6.465 0 0 1 6.5 13C2.91 13 0 10.083 0 6.5 0 2.91 2.917 0 6.5 0 10.09 0 13 2.917 13 6.5a6.463 6.463 0 0 1-.973 3.42zM1.997 6.452c0 2.48 2.014 4.5 4.5 4.5 2.48 0 4.5-2.015 4.5-4.5 0-2.48-2.015-4.5-4.5-4.5-2.48 0-4.5 2.014-4.5 4.5z"/>
                </svg>
            </a>

            <!-- Scan split-button -->
            <div class="header-scan-split" class:scanning>
                <button
                    class="scan-main"
                    disabled={scanning}
                    onclick={() => fireScan(false)}
                    title="Quick scan (touched folders only)"
                >Scan</button>
                <button
                    class="scan-arrow"
                    disabled={scanning}
                    onclick={() => scanDropOpen = !scanDropOpen}
                    aria-label="More scan options"
                >▾</button>
                {#if scanDropOpen}
                    <div class="scan-dropdown">
                        <button onclick={() => fireScan(true)}>Novel Files Only</button>
                    </div>
                {/if}
            </div>

            <a href="/dashboard" class="dashboard-link" class:active={isActive('/dashboard')}>dashboard</a>

            <div class="config-menu-anchor relative">
                <button
                    type="button"
                    id="config-menu-button"
                    class="icon-button"
                    onclick={toggleConfigMenu}
                    aria-label="Settings"
                >
                    <svg fill="#000000" viewBox="0 0 45.973 45.973" xmlns="http://www.w3.org/2000/svg">
                        <path d="M43.454,18.443h-2.437c-0.453-1.766-1.16-3.42-2.082-4.933l1.752-1.756c0.473-0.473,0.733-1.104,0.733-1.774 c0-0.669-0.262-1.301-0.733-1.773l-2.92-2.917c-0.947-0.948-2.602-0.947-3.545-0.001l-1.826,1.815 C30.9,6.232,29.296,5.56,27.529,5.128V2.52c0-1.383-1.105-2.52-2.488-2.52h-4.128c-1.383,0-2.471,1.137-2.471,2.52v2.607 c-1.766,0.431-3.38,1.104-4.878,1.977l-1.825-1.815c-0.946-0.948-2.602-0.947-3.551-0.001L5.27,8.205 C4.802,8.672,4.535,9.318,4.535,9.978c0,0.669,0.259,1.299,0.733,1.772l1.752,1.76c-0.921,1.513-1.629,3.167-2.081,4.933H2.501 C1.117,18.443,0,19.555,0,20.935v4.125c0,1.384,1.117,2.471,2.501,2.471h2.438c0.452,1.766,1.159,3.43,2.079,4.943l-1.752,1.763 c-0.474,0.473-0.734,1.106-0.734,1.776s0.261,1.303,0.734,1.776l2.92,2.919c0.474,0.473,1.103,0.733,1.772,0.733 s1.299-0.261,1.773-0.733l1.833-1.816c1.498,0.873,3.112,1.545,4.878,1.978v2.604c0,1.383,1.088,2.498,2.471,2.498h4.128 c1.383,0,2.488-1.115,2.488-2.498v-2.605c1.767-0.432,3.371-1.104,4.869-1.977l1.817,1.812c0.474,0.475,1.104,0.735,1.775,0.735 c0.67,0,1.301-0.261,1.774-0.733l2.92-2.917c0.473-0.472,0.732-1.103,0.734-1.772c0-0.67-0.262-1.299-0.734-1.773l-1.75-1.77 c0.92-1.514,1.627-3.179,2.08-4.943h2.438c1.383,0,2.52-1.087,2.52-2.471v-4.125C45.973,19.555,44.837,18.443,43.454,18.443z M22.976,30.85c-4.378,0-7.928-3.517-7.928-7.852c0-4.338,3.55-7.85,7.928-7.85c4.379,0,7.931,3.512,7.931,7.85 C30.906,27.334,27.355,30.85,22.976,30.85z"/>
                    </svg>
                </button>

                {#if configMenuOpen}
                    <div class="config-menu">
                        <p class="text-[#aaa] text-sm whitespace-nowrap">Settings coming soon.</p>
                    </div>
                {/if}
            </div>
        </span>
    </nav>
</header>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .logo-main {
        font-family: 'Jaro';
        font-size: 1.7rem;
        color: #eee;
        transform: translateY(-2.5px);
    }

    .logo-secondary {
        font-family: sans-serif;
        color: rgb(240, 102, 22);
        font-weight: 600;
        font-size: 1.4rem;
        letter-spacing: -0.5px;
    }

    .page-link {
        font-family: 'Inter';
    }

    .page-link.active {
        color: rgb(204, 105, 179);
    }

    .icon-button {
        padding: 0 0.2rem;
        border: none;
        background: none;
        height: 1.3rem;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
    }
    .icon-button svg {
        width: auto;
        height: 100%;
        fill: #ccc;
    }
    .icon-button:hover svg {
        fill: white;
    }

    /* Scan split-button */
    .header-scan-split {
        position: relative;
        display: flex;
        margin: 0 0.3rem;
    }
    .scan-main,
    .scan-arrow {
        background: #01b8b8;
        color: #000;
        font-family: Verdana, Geneva, Tahoma, sans-serif;
        font-weight: 600;
        font-size: 0.88rem;
        border: none;
        cursor: pointer;
        transition: background 0.15s;
    }
    .scan-main {
        border-radius: 5px 0 0 5px;
        padding: 0.35rem 0.65rem;
        letter-spacing: -0.4px;
    }
    .scan-arrow {
        border-radius: 0 5px 5px 0;
        border-left: 1px solid rgba(0, 0, 0, 0.2);
        padding: 0.35rem 0.4rem;
        font-size: 0.75rem;
    }
    .scan-main:hover:not(:disabled),
    .scan-arrow:hover:not(:disabled) { background: #00d0d0; }
    .header-scan-split.scanning .scan-main,
    .header-scan-split.scanning .scan-arrow { opacity: 0.45; cursor: not-allowed; }

    .scan-dropdown {
        position: absolute;
        top: calc(100% + 4px);
        left: 0;
        background: #0a0f0f;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 5px;
        z-index: 9999;
        overflow: hidden;
        min-width: 140px;
    }
    .scan-dropdown button {
        display: block;
        width: 100%;
        padding: 0.45rem 0.85rem;
        background: none;
        border: none;
        color: #ccc;
        font-size: 0.83rem;
        text-align: left;
        cursor: pointer;
        white-space: nowrap;
    }
    .scan-dropdown button:hover { background: rgba(255, 255, 255, 0.07); color: #fff; }

    .dashboard-link {
        background: rgb(1, 184, 184);
        color: black;
        font-family: Verdana, Geneva, Tahoma, sans-serif;
        font-weight: 600;
        letter-spacing: -0.8px;
        font-size: 1rem;
        border-radius: 5px;
        padding: 0.4rem 0.7rem;
        margin: 0 0.7rem;
        text-decoration: none;
    }
    .dashboard-link:hover {
        color: #eee;
    }
    .dashboard-link.active {
        background: rgb(204, 105, 179);
    }

    #config-menu-button {
        margin-top: 2px;
        transition: transform 0.4s ease-out;
    }
    #config-menu-button:hover {
        transform: rotate(45deg);
    }

    .config-menu {
        position: absolute;
        top: 35px;
        right: 15px;
        background: black;
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 10px;
        padding: 0.7rem 0.8rem;
        z-index: 9999;
    }
</style>
