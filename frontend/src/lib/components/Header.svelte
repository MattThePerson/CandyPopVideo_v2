<script>
    import { page } from "$app/stores";
</script>

<nav>
    <a href="/"         class:active={$page.url.pathname === "/"}>Home</a>
    <a href="/about"    class:active={$page.url.pathname === "/about"}>About</a>
    <a href="/contact"  class:active={$page.url.pathname === "/contact"}>Contact</a>
</nav>

<style>
    nav {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        background-color: #f0f0f0;
    }
    .active {
        font-weight: bold;
    }
</style>
