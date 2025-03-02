
<!-- SCRIPT ----------------------------------------------------------------------------------------------------------->
<script>
    import { page } from "$app/stores"; // TODO: figure out deprecation warning
    import RandomIcon from "$lib/icons/RandomIcon.svelte";
    import ReloadIcon from "$lib/icons/ReloadIcon.svelte";
    import SearchIcon from "$lib/icons/SearchIcon.svelte";
    import Logo from "./Logo.svelte";
    import Button from "./ui/button/button.svelte";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
</script>


<!-- HTML ------------------------------------------------------------------------------------------------------------->
<nav>
    
    <span>
        <a id='logo' href="/"         class:active={$page.url.pathname === "/"}>
            <Logo />
        </a>

        <Button>shad!!</Button>

        <DropdownMenu.Root>
            <DropdownMenu.Trigger>Open</DropdownMenu.Trigger>
            <DropdownMenu.Content>
                <DropdownMenu.Group>
                    <DropdownMenu.GroupHeading>My Account</DropdownMenu.GroupHeading>
                    <DropdownMenu.Separator />
                    <DropdownMenu.Item>Profile</DropdownMenu.Item>
                    <DropdownMenu.Item>Billing</DropdownMenu.Item>
                    <DropdownMenu.Item>Team</DropdownMenu.Item>
                    <DropdownMenu.Item>Subscription</DropdownMenu.Item>
                </DropdownMenu.Group>
            </DropdownMenu.Content>
        </DropdownMenu.Root>
        
    </span>
    
    <span>
        <a href="/"             class:active={$page.url.pathname === "/"}>home</a>
        <a href="/search"       class:active={$page.url.pathname === "/search"}>search</a>
        <a href="/contact"      class:active={$page.url.pathname === "/contact"}>catalogue</a>
        <a href="/"             class:active={$page.url.pathname === "/other"}>other</a>
        <button class="icon-button" ><RandomIcon --fill-color="#ccc"/></button>
        <button class="icon-button" ><SearchIcon --fill-color="#ccc"/></button>
        <a class="dashboard-link" href="/dashboard"    class:active={$page.url.pathname === "/dashboard"}>dashboard</a>
        <button class="icon-button" ><ReloadIcon --fill-color="#ccc"/></button>
        
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
        /* padding: 1rem; */
        /* background: green; */
    }

    a {
        text-decoration: none;
        padding: 0.4rem 0.3rem;
        /* background: orange; */
        font-size: 1.2rem;
        font-family: Arial, Helvetica, sans-serif;
        font-weight: 500;
        color: #ccc;
    }
    a:hover {
        color: #eee;
    }

    .active {
        color: rgb(165, 103, 150);
    }

    .icon-button {
        padding: 0;
        border: none;
        background: none;
        height: 1.3rem;
        cursor: pointer;
        padding: 0 0.2rem;
    }
    
    .dashboard-link {
        background: rgb(1, 184, 184);
        color: black;
        /* font-family:Verdana, Geneva, Tahoma, sans-serif; */
        font-weight: 600;
        letter-spacing: -0.8px;
        font-size: 1.08rem;
        border-radius: 5px;
        padding: 0.4rem 0.7rem;
    }
</style>
