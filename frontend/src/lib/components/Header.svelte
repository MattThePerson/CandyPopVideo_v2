
<!-- SCRIPT ----------------------------------------------------------------------------------------------------------->
<script>
    import { page } from "$app/stores"; // TODO: figure this shit out
</script>


<!-- HTML ------------------------------------------------------------------------------------------------------------->
<nav>

    <span>
        <a href="/"         class:active={$page.url.pathname === "/"}>
            <div>CandyPop</div>
            <div>Video</div>
        </a>
    </span>

    <span>
        <a href="/"         class:active={$page.url.pathname === "/"}>Home</a>
        <a href="/search"    class:active={$page.url.pathname === "/search"}>search</a>
        <a href="/contact"  class:active={$page.url.pathname === "/contact"}>catalogue</a>
        <a href="/"  class:active={$page.url.pathname === "/"}>other</a>
        <a href="/dashboard"  class:active={$page.url.pathname === "/dashboard"}>Dashboard</a>

    </span>
    
</nav>


<!-- STYLES ----------------------------------------------------------------------------------------------------------->
<style>
    nav {
        display: flex;
        background-color: #f0f0f0;
        justify-content: space-between;
    }
    
    span {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        background: green;
    }

    .active {
        font-weight: bold;
    }
</style>
