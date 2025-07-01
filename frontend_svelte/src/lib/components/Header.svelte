
<!-- SCRIPT ----------------------------------------------------------------------------------------------------------->
<script>
    import { page } from "$app/stores"; // TODO: figure out deprecation warning
    import RandomIcon from "$lib/icons/RandomIcon.svelte";
    import ReloadIcon from "$lib/icons/ReloadIcon.svelte";
    import SearchIcon from "$lib/icons/SearchIcon.svelte";
    import Logo from "./Logo.svelte";
</script>


<!-- HTML ------------------------------------------------------------------------------------------------------------->
<nav>
    
    <span>
        <a id='logo' href="/"         class:active={$page.url.pathname === "/"}>
            <Logo />
        </a>

    </span>
    
    <span>
        <span class="page-links">
            <a class="page-link" href="/"             class:active={$page.url.pathname === "/"}>home</a>
            <a class="page-link" href="/search"       class:active={$page.url.pathname === "/search"}>search</a>
            <a class="page-link" href="/catalogue"    class:active={$page.url.pathname === "/catalogue"}>catalogue</a>
            <a class="page-link" href="/curated"      class:active={$page.url.pathname === "/curated"}>curated</a>
        </span>
        <button class="icon-button" ><RandomIcon --fill-color="#ccc"/></button>
        <button class="icon-button" ><SearchIcon --fill-color="#ccc"/></button>
        <a class="dashboard-link" href="/dashboard"    class:active={$page.url.pathname === "/dashboard"}>dashboard</a>
    </span>
    
</nav>


<!-- STYLES ----------------------------------------------------------------------------------------------------------->
<style>
    
    nav {
        display: flex;
        justify-content: space-between;
        padding: 0 2.5%;
        background: black;
        outline: 1px solid #fff3;
    }
    
    span {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.3rem;
    }

    a {
        text-decoration: none;
        padding: 0.4rem 0.3rem;
        
    }
    
    /* page links */
    .page-links {
        transform: translateY(2px);
        display: flex;
        gap: 1px;
    }
    .page-link {
        padding: 0.4rem 0.5rem;
        font-size: 1.2rem;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        color: #d3d3d3;
        /* background: orange; */
    }
    .page-link:hover {
        color: #eee;
        text-decoration: underline dotted grey;
    }
    .page-link.active {
        color: rgb(204, 105, 179);
    }
    
    
    .icon-button {
        padding: 0;
        border: none;
        background: none;
        height: 1.3rem;
        cursor: pointer;
        padding: 0 0.2rem;
    }
    
    /* dashboard link */
    .dashboard-link {
        background: rgb(1, 184, 184);
        color: black;
        font-family: Verdana, Geneva, Tahoma, sans-serif;
        font-weight: 600;
        letter-spacing: -0.8px;
        font-size: 1.0rem;
        border-radius: 5px;
        padding: 0.4rem 0.7rem;
    }
    .dashboard-link:hover {
        color: #eee;
    }
    .dashboard-link.active {
        background: rgb(204, 105, 179);
    }

</style>
